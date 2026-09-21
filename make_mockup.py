# make_mockup.py - 목업(임시) 배경 1장 만들기
# 진짜 AI 배경이 오기 전까지 자리를 대신할 그라데이션 이미지를 찍어냅니다.
from PIL import Image

WIDTH, HEIGHT = 1240, 1754          # A4 비율 캔버스
TOP_COLOR = (38, 50, 78)            # 위쪽 색 (짙은 남색)
BOTTOM_COLOR = (120, 90, 70)        # 아래쪽 색 (따뜻한 갈색)
OUT_PATH = "assets/mockups/bg_mock.png"

# 세로로 1픽셀짜리 그라데이션 띠를 만든 뒤 전체 크기로 늘립니다 (빠름)
strip = Image.new("RGB", (1, HEIGHT))
for y in range(HEIGHT):
    t = y / (HEIGHT - 1)            # 0.0(맨위) ~ 1.0(맨아래)
    r = round(TOP_COLOR[0] + (BOTTOM_COLOR[0] - TOP_COLOR[0]) * t)
    g = round(TOP_COLOR[1] + (BOTTOM_COLOR[1] - TOP_COLOR[1]) * t)
    b = round(TOP_COLOR[2] + (BOTTOM_COLOR[2] - TOP_COLOR[2]) * t)
    strip.putpixel((0, y), (r, g, b))

img = strip.resize((WIDTH, HEIGHT))
img.save(OUT_PATH)
print("목업 배경 저장 완료:", OUT_PATH, img.size)
