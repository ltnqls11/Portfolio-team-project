# 네이버 블로그 인플루언서 정보 수집 RPA

네이버 블로그에서 특정 키워드로 검색하여 블로거의 정보(블로그명, URL, 이메일)를 자동으로 수집하고 Google Sheets에 저장하는 RPA 스크립트입니다.

## 주요 기능

### 🤖 완전한 자동화 (n8n 없이 독립 실행)
- **①블로거 정보 수집** → **②이메일 자동 발송** → **③네이버 카페 자동 포스팅**
- 모든 과정이 하나의 스크립트로 완전 자동화
- 외부 도구(n8n) 없이 독립적으로 동작

### 📊 데이터 수집 및 관리
- 네이버 블로그 자동 검색
- 블로그 게시물 정보 추출 (블로그명, 포스트URL, 블로그URL)
- 블로그에서 이메일 주소 자동 탐색
- Google Sheets 자동 저장

### 📧 이메일 마케팅
- Gmail API를 통한 자동 이메일 발송
- 개인화된 HTML 이메일 템플릿
- 대량 이메일 발송 지원

### 📝 카페 마케팅
- 네이버 카페 자동 포스팅
- 제품 홍보 게시물 자동 생성
- 여러 카페 동시 포스팅 지원

### 🛡️ 안전성 및 편의성
- 환경변수 기반 보안 관리
- 예외 처리 및 안정적인 실행
- React 기반 사용자 친화적 제어판

## 설치 및 설정

### 1. 필요한 패키지 설치

```bash
python setup.py
```

### 2. 환경변수 설정

```bash
# .env.example 파일을 복사하여 .env 파일 생성
cp .env.example .env

# React 앱용 환경변수도 설정
cd react-control-panel
cp .env.example .env
cd ..
```

`.env` 파일을 편집하여 실제 API 키와 설정값을 입력하세요. 자세한 설정 방법은 `ENVIRONMENT_SETUP.md`를 참조하세요.

### 3. Google Sheets API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Sheets API 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. 인증 정보를 `credentials.json` 파일로 다운로드
6. 이 파일을 프로젝트 루트 디렉토리에 저장

## 사용법

### 🚀 통합 시스템 실행 (권장)

```bash
python start_system.py
```

이 명령어로 전체 시스템(API 서버 + React 제어판)이 자동으로 시작됩니다.

- **React 제어판**: http://localhost:3000
- **API 서버**: http://localhost:5000

### 📱 React 제어판 사용법

1. 브라우저에서 http://localhost:3000 접속
2. 기본 설정에서 키워드, Google Sheets ID, 시트 이름 입력
3. "블로거 정보 수집 시작" 버튼 클릭
4. n8n 워크플로우 설정 완료 후 이메일 발송 및 카페 포스팅 실행

### 🔧 개별 실행 (고급 사용자용)

```bash
# 1. API 서버만 실행
python api_server.py

# 2. 스크래핑만 실행
python main.py --keyword "검색키워드" --sheet-id "GOOGLE_SHEETS_ID" --sheet-name "시트이름"

# 3. React 앱만 실행
cd react-control-panel
npm install
npm start
```

### 매개변수 설명

- `--keyword`: 네이버 블로그에서 검색할 키워드
- `--sheet-id`: Google Sheets 문서의 ID (URL에서 확인 가능)
- `--sheet-name`: 데이터를 저장할 시트의 이름

### 🚀 완전한 자동화 실행

```bash
# 모든 단계를 한 번에 실행 (권장)
python complete_automation.py --keyword "내돈내산 영양제" --sheet-id "SHEET_ID" --sheet-name "Sheet1" --product-name "프리미엄 영양제"

# 대화형 실행
python run_automation.py
```

### 사용 예시

```bash
# 개별 단계 실행 (블로거 정보 수집만)
python main.py --keyword "내돈내산 영양제" --sheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" --sheet-name "Sheet1"

# 완전한 자동화 실행
python complete_automation.py --keyword "내돈내산 영양제" --sheet-id "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" --sheet-name "Sheet1" --product-name "프리미엄 영양제" --event-info "런칭 기념 50% 할인"
```

## Google Sheets ID 찾는 방법

Google Sheets URL에서 ID를 확인할 수 있습니다:
```
https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit#gid=0
```

## 출력 데이터 형식

Google Sheets에 다음과 같은 형식으로 데이터가 저장됩니다:

| 블로그명 | 포스트URL | 블로그URL | 이메일 |
|---------|-----------|-----------|--------|
| 예시블로그 | https://blog.naver.com/... | https://blog.naver.com/user | user@example.com |

## 파일 구조

```
├── main.py                 # 메인 실행 파일
├── naver_blog_scraper.py   # 네이버 블로그 스크래핑 클래스
├── google_sheets_client.py # Google Sheets API 클라이언트
├── config.py              # 설정 파일
├── setup.py               # 설치 스크립트
├── requirements.txt       # 필요한 패키지 목록
├── credentials.json       # Google API 인증 파일 (사용자가 추가)
└── token.json            # 자동 생성되는 토큰 파일
```

## 주의사항

1. **Google API 인증**: `credentials.json` 파일이 반드시 필요합니다.
2. **Chrome 브라우저**: 시스템에 Chrome 브라우저가 설치되어 있어야 합니다.
3. **네트워크 연결**: 안정적인 인터넷 연결이 필요합니다.
4. **사용 제한**: 네이버의 이용약관을 준수하여 적절한 간격으로 사용하세요.

## 문제 해결

### Chrome 드라이버 오류
- Chrome 브라우저가 최신 버전인지 확인
- `webdriver-manager`가 자동으로 드라이버를 관리합니다

### Google Sheets API 오류
- `credentials.json` 파일이 올바른 위치에 있는지 확인
- Google Cloud Console에서 API가 활성화되어 있는지 확인
- 시트 ID와 시트 이름이 정확한지 확인

### 이메일 추출 실패
- 모든 블로그에서 이메일을 찾을 수 있는 것은 아닙니다
- 이메일이 없는 경우 해당 셀은 비워집니다

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 상업적 사용 시 관련 법규를 준수하세요.