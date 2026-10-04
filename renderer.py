# renderer.py - 포스터 합성 렌더러 (v3: 어느 OS에서나 한글 폰트 찾기)
import os, glob, json
import unicodedata
from PIL import Image, ImageDraw, ImageFont

# 폰트 후보 목록: 위에서부터 '존재하는 첫 번째' 파일을 씁니다.
# 윈도우(내 컴퓨터) → 저장소 번들 → 리눅스 서버(fonts-nanum / noto) 순.
FONT_CANDIDATES = {
    "맑은 고딕": [
        r"C:\Windows\Fonts\malgun.ttf",                            # Windows
        "assets/fonts/NanumGothic.ttf",                            # 저장소에 넣어둔 경우
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",         # Streamlit Cloud (packages.txt)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # 일반 리눅스
    ],
    "맑은 고딕 볼드": [
        r"C:\Windows\Fonts\malgunbd.ttf",
        "assets/fonts/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ],
}
DEFAULT_FONT = "맑은 고딕"
# 화면 드롭다운에 보일 이름 (renderer 를 import 하는 app 들이 사용)
FONTS = {name: name for name in FONT_CANDIDATES}

LINE_SPACING = 1.2
MIN_FONT_SIZE = 20


def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def resolve_font_path(name):
    """폰트 이름 -> 실제로 존재하는 폰트 파일 경로. 어느 OS에서나 동작."""
    path = _first_existing(FONT_CANDIDATES.get(name, FONT_CANDIDATES[DEFAULT_FONT]))
    if path is None:
        # 최후의 보루: 시스템 어딘가의 한글 가능한 폰트라도 찾아 씀
        for pat in ("/usr/share/fonts/**/*.ttc", "/usr/share/fonts/**/*.ttf"):
            found = glob.glob(pat, recursive=True)
            if found:
                return found[0]
    return path


def normalize_nfc(text):
    return unicodedata.normalize("NFC", text)


def wrap_by_pixel(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            trial = current + ch
            if draw.textlength(trial, font=font) <= max_width or current == "":
                current = trial
            else:
                lines.append(current)
                current = ch
        lines.append(current)
    return lines


def _block_height(lines, font):
    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    if not lines:
        return 0, line_h
    total = int(line_h * LINE_SPACING * (len(lines) - 1) + line_h)
    return total, line_h


def fit_font(text, font_path, box_w, box_h, start_size, draw):
    size = start_size
    while size >= MIN_FONT_SIZE:
        font = ImageFont.truetype(font_path, size)
        lines = wrap_by_pixel(text, font, box_w, draw)
        total_h, _ = _block_height(lines, font)
        if total_h <= box_h:
            return font, lines
        size -= 2
    font = ImageFont.truetype(font_path, MIN_FONT_SIZE)
    return font, wrap_by_pixel(text, font, box_w, draw)


def draw_block(draw, lines, font, box, color, outline):
    x, y, w, h = box["x"], box["y"], box["width"], box["height"]
    total_h, line_h = _block_height(lines, font)
    cur_y = y + (h - total_h) // 2
    cx = x + w // 2
    stroke = max(2, font.size // 20) if outline else 0
    for line in lines:
        draw.text((cx, cur_y), line, font=font, fill=color,
                  anchor="ma", stroke_width=stroke, stroke_fill="#000000")
        cur_y += int(line_h * LINE_SPACING)


def render_poster(background_path, layout_path, texts, output_path, overrides=None):
    layout = json.load(open(layout_path, encoding="utf-8-sig"))
    overrides = overrides or {}
    cw = layout["canvas"]["width"]
    ch = layout["canvas"]["height"]
    img = Image.open(background_path).convert("RGB").resize((cw, ch))
    draw = ImageDraw.Draw(img)
    for el in layout["elements"]:
        el_id = el["id"]
        raw = texts.get(el_id, "")
        if not raw:
            continue
        ov = overrides.get(el_id, {})
        font_size = ov.get("font_size", el["font_size"])
        color = ov.get("color", el["color"])
        outline = ov.get("outline", el.get("outline", True))
        font_name = ov.get("font", DEFAULT_FONT)
        font_path = resolve_font_path(font_name)
        text = normalize_nfc(raw)
        font, lines = fit_font(text, font_path, el["box"]["width"],
                               el["box"]["height"], font_size, draw)
        draw_block(draw, lines, font, el["box"], color, outline)
    img.save(output_path)
    return output_path