# 환경변수 설정 가이드

## 📋 개요

이 프로젝트는 `.env` 파일을 사용하여 API 키와 민감한 정보를 안전하게 관리합니다.

## 🔧 설정 방법

### 1. 메인 프로젝트 환경변수 설정

1. `.env.example` 파일을 복사하여 `.env` 파일 생성:
```bash
cp .env.example .env
```

2. `.env` 파일을 편집하여 실제 값으로 변경:

```bash
# Google Sheets API 설정
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_TOKEN_FILE=token.json

# 네이버 API 설정 (카페 포스팅용)
NAVER_CLIENT_ID=your_actual_naver_client_id
NAVER_CLIENT_SECRET=your_actual_naver_client_secret
NAVER_CAFE_ID=12345678
NAVER_MENU_ID=87654321

# Gmail API 설정
GMAIL_CREDENTIALS_FILE=gmail_credentials.json

# n8n 웹훅 URL 설정
N8N_BASE_URL=http://localhost:5678
N8N_EMAIL_WEBHOOK_ID=your_actual_email_webhook_id
N8N_CAFE_WEBHOOK_ID=your_actual_cafe_webhook_id

# 기본 Google Sheets 설정
DEFAULT_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
DEFAULT_SHEET_NAME=Sheet1

# 보안 설정
SECRET_KEY=your_strong_secret_key_here
```

### 2. React 앱 환경변수 설정

1. React 앱 디렉토리로 이동:
```bash
cd react-control-panel
```

2. `.env.example` 파일을 복사하여 `.env` 파일 생성:
```bash
cp .env.example .env
```

3. 필요시 값 수정:
```bash
REACT_APP_API_BASE_URL=http://localhost:5000/api
REACT_APP_N8N_BASE_URL=http://localhost:5678
REACT_APP_N8N_EMAIL_WEBHOOK_ID=your_actual_email_webhook_id
REACT_APP_N8N_CAFE_WEBHOOK_ID=your_actual_cafe_webhook_id
```

## 🔑 API 키 발급 방법

### Google Sheets API
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Sheets API 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. `credentials.json` 파일 다운로드

### 네이버 개발자 API
1. [네이버 개발자 센터](https://developers.naver.com/) 접속
2. 애플리케이션 등록
3. 카페 API 권한 신청
4. 클라이언트 ID와 시크릿 발급받기

### Gmail API
1. Google Cloud Console에서 Gmail API 활성화
2. OAuth 2.0 인증 정보 생성 (Google Sheets와 동일 가능)
3. `gmail_credentials.json` 파일 다운로드

## 🛡️ 보안 주의사항

### ⚠️ 절대 공개하면 안 되는 파일들:
- `.env`
- `credentials.json`
- `gmail_credentials.json`
- `token.json`

### ✅ 안전한 관리 방법:
1. **Git에 커밋하지 않기**: `.gitignore`에 이미 추가됨
2. **강력한 SECRET_KEY 사용**: 랜덤 문자열 생성 권장
3. **정기적인 키 교체**: 보안을 위해 주기적으로 API 키 교체
4. **최소 권한 원칙**: 필요한 최소한의 API 권한만 부여

## 🔍 환경변수 확인 방법

### Python에서 확인:
```python
from config import *
print(f"Google Sheets 인증 파일: {CREDENTIALS_FILE}")
print(f"네이버 클라이언트 ID: {NAVER_CLIENT_ID}")
print(f"n8n 베이스 URL: {N8N_BASE_URL}")
```

### React에서 확인:
```javascript
console.log('API Base URL:', process.env.REACT_APP_API_BASE_URL);
console.log('n8n Base URL:', process.env.REACT_APP_N8N_BASE_URL);
```

## 🚀 실행 전 체크리스트

- [ ] `.env` 파일 생성 및 설정 완료
- [ ] `react-control-panel/.env` 파일 생성 및 설정 완료
- [ ] Google API 인증 파일 (`credentials.json`) 준비
- [ ] 네이버 API 키 발급 및 설정
- [ ] n8n 웹훅 ID 확인 및 설정
- [ ] 모든 민감한 파일이 `.gitignore`에 포함되어 있는지 확인

## 🔧 문제 해결

### 환경변수가 로드되지 않는 경우:
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. `python-dotenv` 패키지가 설치되어 있는지 확인
3. 환경변수 이름에 오타가 없는지 확인

### API 인증 실패:
1. API 키가 올바른지 확인
2. API 권한이 활성화되어 있는지 확인
3. 인증 파일 경로가 정확한지 확인

### React 환경변수 인식 안됨:
1. 환경변수 이름이 `REACT_APP_`로 시작하는지 확인
2. React 앱 재시작 필요
3. `.env` 파일이 `react-control-panel` 디렉토리에 있는지 확인