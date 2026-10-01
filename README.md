# 소상공인 AI 홍보물 제작소

소상공인이 짧은 문구만 입력하면 포스터·안내문을 자동으로 만들어 주는 웹 서비스입니다.
AI는 배경 이미지만 생성하고, 글자는 코드(Pillow)로 또렷하게 얹어 한글 가독성을 보장합니다.

## 기술 스택
- Python 3.10 이상
- Streamlit (웹 화면)
- Pillow (이미지 합성 및 텍스트 렌더링)
- OpenAI API (배경 이미지 생성 — 추후 연동 예정)

## 폴더 구조
- app.py — 웹 화면 (입력 → 합성 → 다운로드)
- renderer.py — 포스터 합성 엔진 (NFC 정규화·픽셀 줄바꿈·자동 축소·외곽선)
- make_mockup.py — 임시(목업) 배경 생성기
- config.py — 디자인 규격 설정 (레이아웃 좌표·색상·폰트)
- layouts/ — 레이아웃 좌표 JSON
- assets/ — 폰트·오버레이·장식·목업 배경
- output/ — 생성 결과물 (git에 올리지 않음)

## 처음 받아서 실행하는 법 (팀원용)

1. 저장소 내려받기: git clone 후 cd test
2. 가상환경 만들고 켜기: python -m venv venv 후 .\venv\Scripts\Activate.ps1
   - "스크립트를 실행할 수 없습니다" 오류 시: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned 실행 후 Y
3. 패키지 설치: python -m pip install -r requirements.txt
4. 환경변수 파일 만들기: copy .env.example .env (그 뒤 본인 키 입력)
5. 실행: streamlit run app.py

## 함께 작업할 때 규칙
- 작업 시작 전 항상 git pull 로 최신 코드를 먼저 받습니다.
- .env 는 절대 올리지 않습니다 (비밀 키).
- 커밋 메시지는 무엇을 바꿨는지 한 줄로 적습니다.
   ## 연습 메모
   브랜치와 PR 연습용으로 추가한 줄입니다.