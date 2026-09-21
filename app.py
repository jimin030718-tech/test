# app.py - 소상공인 AI 홍보물 제작소 (목업 + 스타일 조절 버전)
# 화면에서 내용 / 폰트 / 크기 / 색상 / 외곽선을 직접 바꿀 수 있음
import json
import streamlit as st
import renderer

BACKGROUND_PATH = "assets/mockups/bg_mock.png"
LAYOUT_PATH = "layouts/layout_A.json"
OUTPUT_PATH = "output/poster_result.png"

# 요소별 화면 이름과 기본 문구
LABELS = {"title": "메인 제목", "subtitle": "부제목 / 설명"}
DEFAULT_TEXTS = {
    "title": "가을 신메뉴 출시",
    "subtitle": "10월 한 달간 전 메뉴 20% 할인",
}

layout = json.load(open(LAYOUT_PATH, encoding="utf-8-sig"))
font_names = list(renderer.FONTS.keys())

st.title("소상공인 AI 홍보물 제작소")
st.caption("내용과 스타일(폰트·크기·색상)을 정하고 버튼을 누르면 포스터가 만들어져요.")

texts = {}
overrides = {}

for el in layout["elements"]:
    el_id = el["id"]
    label = LABELS.get(el_id, el_id)
    st.subheader(label)

    texts[el_id] = st.text_input(
        "내용", DEFAULT_TEXTS.get(el_id, ""), key=f"text_{el_id}"
    )

    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    with c1:
        font = st.selectbox("폰트", font_names, key=f"font_{el_id}")
    with c2:
        size = st.slider("크기", 20, 250, el["font_size"], key=f"size_{el_id}")
    with c3:
        color = st.color_picker("색상", el["color"], key=f"color_{el_id}")
    with c4:
        outline = st.checkbox("외곽선", el.get("outline", True), key=f"outline_{el_id}")

    overrides[el_id] = {
        "font": font,
        "font_size": size,
        "color": color,
        "outline": outline,
    }

st.divider()

if st.button("AI 포스터 자동 완성하기", type="primary"):
    with st.spinner("포스터를 만들고 있어요..."):
        renderer.render_poster(
            BACKGROUND_PATH, LAYOUT_PATH, texts, OUTPUT_PATH, overrides=overrides
        )
    st.session_state["poster_ready"] = True

if st.session_state.get("poster_ready"):
    st.success("완성됐어요!")
    st.image(OUTPUT_PATH, caption="완성된 포스터 미리보기", width="stretch")
    with open(OUTPUT_PATH, "rb") as f:
        st.download_button(
            label="고화질 포스터 다운로드 (PNG)",
            data=f.read(),
            file_name="poster.png",
            mime="image/png",
        )
