# renderer.py - 포스터 합성 렌더러
# 4가지 기능: ①NFC 정규화 ②픽셀 기준 줄바꿈 ③자동 크기 축소 ④외곽선
# + 화면(앱)에서 넘어온 값(색상/크기/폰트/외곽선)으로 요소별 설정을 덮어쓸 수 있음
import json
import unicodedata
from PIL import Image, ImageDraw, ImageFont

# 선택 가능한 폰트 목록: "화면에 보일 이름" -> "폰트 파일 경로"
# 디자인팀 폰트가 오면 assets/fonts/ 에 넣고 여기에 한 줄씩 추가하면 됩니다.
FONTS = {
    "맑은 고딕": r"C:\Windows\Fonts\malgun.ttf",
    "맑은 고딕 볼드": r"C:\Windows\Fonts\malgunbd.ttf",
}
DEFAULT_FONT = "맑은 고딕"

LINE_SPACING = 1.2
MIN_FONT_SIZE = 20


# ① NFC 정규화
def normalize_nfc(text):
    return unicodedata.normalize("NFC", text)


# ② 픽셀 기준 줄바꿈
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


# ③ 자동 크기 축소
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


# ④ 외곽선
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

        # 화면에서 넘어온 값이 있으면 그 값을, 없으면 JSON 기본값을 사용
        font_size = ov.get("font_size", el["font_size"])
        color = ov.get("color", el["color"])
        outline = ov.get("outline", el.get("outline", True))
        font_name = ov.get("font", DEFAULT_FONT)
        font_path = FONTS.get(font_name, FONTS[DEFAULT_FONT])

        text = normalize_nfc(raw)                                   # ①
        font, lines = fit_font(text, font_path, el["box"]["width"], # ②③
                               el["box"]["height"], font_size, draw)
        draw_block(draw, lines, font, el["box"], color, outline)    # ④

    img.save(output_path)
    return output_path
