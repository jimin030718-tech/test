# ux_demo.py - UX 흐름 체험용 목업 (진짜 GPT 호출 없음)
# 기능 → 템플릿 → 사진 → 이미지 생성(목업) → 수정(텍스트·무드)
import json, os, time
import streamlit as st
from PIL import Image
import renderer

os.makedirs("output", exist_ok=True)
DEMO_BG = "output/_demo_bg.png"
DEMO_LAYOUT = "output/_demo_layout.json"
DEMO_POSTER = "output/_demo_poster.png"

# ----- 기능별 기본 문구 -----
FUNCTIONS = {
    "신메뉴 출시": {"title": "가을 신메뉴 출시", "subtitle": "따뜻한 호박 라떼 한정 판매"},
    "할인 이벤트": {"title": "오픈 기념 대할인", "subtitle": "전 메뉴 20% 할인"},
    "매장 공지": {"title": "임시 휴무 안내", "subtitle": "10월 9일 하루 쉽니다"},
}

# ----- 무드별 배경 색(위->아래 그라데이션) -----
MOODS = {
    "모던 / 깔끔": ((60, 70, 90), (125, 135, 155)),
    "감성 / 따뜻": ((90, 60, 45), (185, 140, 110)),
    "활기찬 / 할인": ((200, 55, 60), (240, 150, 45)),
    "전통 / 고급": ((22, 22, 32), (80, 62, 24)),
}

# ----- 템플릿별 레이아웃(글자 자리) -----
TEMPLATES = {
    "상단 텍스트형 (A)": {
        "name": "A", "canvas": {"width": 1240, "height": 1754},
        "elements": [
            {"id": "title", "box": {"x": 100, "y": 110, "width": 1040, "height": 300}, "font_size": 150, "color": "#FFFFFF", "outline": True},
            {"id": "subtitle", "box": {"x": 120, "y": 430, "width": 1000, "height": 180}, "font_size": 64, "color": "#FFF3C4", "outline": True},
        ],
    },
    "하단 텍스트형 (B)": {
        "name": "B", "canvas": {"width": 1240, "height": 1754},
        "elements": [
            {"id": "title", "box": {"x": 100, "y": 1150, "width": 1040, "height": 300}, "font_size": 150, "color": "#FFFFFF", "outline": True},
            {"id": "subtitle", "box": {"x": 120, "y": 1470, "width": 1000, "height": 180}, "font_size": 64, "color": "#FFF3C4", "outline": True},
        ],
    },
    "중앙 이벤트형 (C)": {
        "name": "C", "canvas": {"width": 1240, "height": 1754},
        "elements": [
            {"id": "title", "box": {"x": 100, "y": 700, "width": 1040, "height": 260}, "font_size": 160, "color": "#FFD400", "outline": True},
            {"id": "subtitle", "box": {"x": 120, "y": 980, "width": 1000, "height": 160}, "font_size": 60, "color": "#FFFFFF", "outline": True},
        ],
    },
}


def make_mood_bg(mood, path):
    top, bottom = MOODS[mood]
    h = 1754
    strip = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        strip.putpixel((0, y), tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    strip.resize((1240, h)).save(path)


def build_poster(template, mood, texts, overrides):
    make_mood_bg(mood, DEMO_BG)
    json.dump(TEMPLATES[template], open(DEMO_LAYOUT, "w", encoding="utf-8"))
    renderer.render_poster(DEMO_BG, DEMO_LAYOUT, texts, DEMO_POSTER, overrides=overrides)
    return DEMO_POSTER


# ================== 화면 ==================
st.set_page_config(page_title="UX 체험판", layout="centered")

ss = st.session_state
ss.setdefault("step", 1)
ss.setdefault("func", None)
ss.setdefault("template", "상단 텍스트형 (A)")
ss.setdefault("mood", "모던 / 깔끔")
ss.setdefault("texts", {"title": "가을 신메뉴 출시", "subtitle": "따뜻한 호박 라떼 한정 판매"})

STEP_LABELS = ["기능", "템플릿", "사진", "생성", "수정"]
cur = ss.step
st.markdown("### 🎨 AI 홍보물 제작 — UX 체험판")
st.caption("실제 GPT는 호출하지 않는 '느낌 체험용' 데모입니다.")
st.progress(cur / 5)
st.write(" → ".join([f"**{i+1}.{l}**" if i + 1 == cur else f"{i+1}.{l}" for i, l in enumerate(STEP_LABELS)]))
st.divider()


def go(n):
    ss.step = n


# --- 1단계: 기능 선택 ---
if cur == 1:
    st.subheader("1단계 · 무엇을 만들까요?")
    for name in FUNCTIONS:
        if st.button(name, use_container_width=True):
            ss.func = name
            ss.texts = dict(FUNCTIONS[name])
            go(2)
            st.rerun()
    if ss.func:
        st.success(f"선택됨: {ss.func}")

# --- 2단계: 템플릿 선택 ---
elif cur == 2:
    st.subheader("2단계 · 템플릿(배치) 고르기")
    ss.template = st.radio("글자가 들어갈 위치를 골라요", list(TEMPLATES.keys()),
                           index=list(TEMPLATES.keys()).index(ss.template))
    c1, c2 = st.columns(2)
    c1.button("← 이전", on_click=go, args=(1,), use_container_width=True)
    c2.button("다음 →", on_click=go, args=(3,), type="primary", use_container_width=True)

# --- 3단계: 사진 삽입 ---
elif cur == 3:
    st.subheader("3단계 · 매장/제품 사진 넣기")
    photo = st.file_uploader("사진을 올려보세요 (체험용이라 안 올려도 됩니다)", type=["png", "jpg", "jpeg"])
    if photo:
        st.image(photo, caption="삽입된 사진 (실제 버전에선 이 사진을 배경에 합성)", width=240)
    c1, c2 = st.columns(2)
    c1.button("← 이전", on_click=go, args=(2,), use_container_width=True)
    c2.button("다음 →", on_click=go, args=(4,), type="primary", use_container_width=True)

# --- 4단계: 이미지 생성 (목업) ---
elif cur == 4:
    st.subheader("4단계 · AI 배경 생성")
    st.caption("실제 버전에선 GPT가 배경을 그립니다. 지금은 목업 배경이 대신 떠요.")
    if st.button("✨ AI 배경 생성하기", type="primary", use_container_width=True):
        with st.spinner("GPT가 배경을 그리고 문구를 정돈하고 있어요..."):
            time.sleep(1.2)
            ov = {k: {} for k in ss.texts}
            build_poster(ss.template, ss.mood, ss.texts, ov)
        ss.generated = True
    if ss.get("generated"):
        st.image(DEMO_POSTER, caption="방금 생성된 포스터", width="stretch")
    c1, c2 = st.columns(2)
    c1.button("← 이전", on_click=go, args=(3,), use_container_width=True)
    c2.button("수정하러 가기 →", on_click=go, args=(5,), type="primary",
              use_container_width=True, disabled=not ss.get("generated"))

# --- 5단계: 수정 (텍스트 + 무드) ---
elif cur == 5:
    st.subheader("5단계 · 수정 (텍스트·무드)")
    layout = TEMPLATES[ss.template]
    ss.mood = st.selectbox("무드(배경 분위기) 바꾸기", list(MOODS.keys()),
                           index=list(MOODS.keys()).index(ss.mood))
    texts, overrides = {}, {}
    for el in layout["elements"]:
        eid = el["id"]
        label = "메인 제목" if eid == "title" else "부제목"
        st.markdown(f"**{label}**")
        texts[eid] = st.text_input("내용", ss.texts.get(eid, ""), key=f"t_{eid}")
        a, b, c = st.columns([3, 2, 2])
        size = a.slider("크기", 20, 250, el["font_size"], key=f"s_{eid}")
        color = b.color_picker("색상", el["color"], key=f"c_{eid}")
        outline = c.checkbox("외곽선", True, key=f"o_{eid}")
        overrides[eid] = {"font_size": size, "color": color, "outline": outline}
    ss.texts = texts
    if st.button("🔄 수정 반영하기", type="primary", use_container_width=True):
        build_poster(ss.template, ss.mood, texts, overrides)
    if os.path.exists(DEMO_POSTER):
        st.image(DEMO_POSTER, caption="수정 결과", width="stretch")
        with open(DEMO_POSTER, "rb") as f:
            st.download_button("포스터 다운로드 (PNG)", f.read(), "poster_demo.png", "image/png")
    st.button("← 이전", on_click=go, args=(4,))
    st.button("🏠 처음부터 다시", on_click=go, args=(1,))