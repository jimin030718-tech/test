# _test.py - 렌더러가 잘 도는지 한 번 시험해보는 파일
import renderer

texts = {
    "title": "가을 신메뉴 출시 특별 할인 이벤트",
    "subtitle": "10월 한 달간 전 메뉴 20% 할인",
}
out = renderer.render_poster(
    "assets/mockups/bg_mock.png",
    "layouts/layout_A.json",
    texts,
    "output/test_poster.png",
)
print("포스터 생성 완료:", out)
