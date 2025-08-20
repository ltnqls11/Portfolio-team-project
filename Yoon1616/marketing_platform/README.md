## 라인 마케팅 자동화 플랫폼 (AI + n8n)

### 개요
제품 정보를 입력하면 블로거 추천 → 홍보 문구 생성 → 연락 자동화까지 한 번에 수행하는 Streamlit 기반 앱입니다. 발송 및 상태 추적은 n8n 워크플로와 연동합니다.

### 구성
- `streamlit_app.py`: 메인 UI (추천/문구 생성/연락 자동화)
- `blogdex_scraper.py`: 블로그 후보 수집(블로그덱스 시도, 실패 시 CSV 업로드 대안)
- `promo_generator.py`: OpenAI 기반 채널별 홍보 문구/템플릿 생성
- `mailer.py`: (옵션) 로컬 SMTP 발송 유틸. 기본은 n8n 웹훅 사용
- `requirements.txt`: 의존성 목록

### 환경변수(.env)
- `OPENAI_API_KEY`: OpenAI API 키
- `N8N_OUTREACH_WEBHOOK_URL`: n8n 연락 자동화 웹훅 URL (예: `https://<workspace>.app.n8n.cloud/webhook/outreach`)
- (옵션 SMTP)
  - `GMAIL_EMAIL`, `GMAIL_APP_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`

### 실행
1) 패키지 설치
```bash
py -m pip install -r mini_project/marketing_platform/requirements.txt
```
2) 앱 실행
```bash
streamlit run mini_project/marketing_platform/streamlit_app.py
```

### n8n 워크플로
- `19-n8n/22. 블로거 연락 자동화.json`: 웹훅 입력(수신자/제목/본문) → Gmail 발송 → Google Sheets 로그
- `19-n8n/23. 블로거 회신 추적.json`: Gmail Trigger → 회신 감지 → Google Sheets 상태 업데이트

두 워크플로를 가져와 자격증명만 연결해 사용하세요.

