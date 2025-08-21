# n8n 워크플로우 설정 가이드

## n8n 설치 및 실행

### 1. n8n 설치
```bash
npm install -g n8n
```

### 2. n8n 실행
```bash
n8n start
```

n8n이 http://localhost:5678 에서 실행됩니다.

## 워크플로우 Import

### 1. 이메일 발송 워크플로우
1. n8n 웹 인터페이스에서 "Import from File" 클릭
2. `email-workflow.json` 파일 선택
3. 워크플로우가 생성됨

### 2. 카페 포스팅 워크플로우
1. n8n 웹 인터페이스에서 "Import from File" 클릭
2. `cafe-post-workflow.json` 파일 선택
3. 워크플로우가 생성됨

## 인증 설정

### Google Sheets OAuth2 설정
1. n8n에서 "Credentials" 메뉴 클릭
2. "Create New" → "Google Sheets OAuth2 API" 선택
3. Google Cloud Console에서 생성한 OAuth2 클라이언트 ID 정보 입력:
   - Client ID
   - Client Secret
   - Redirect URL: `http://localhost:5678/rest/oauth2-credential/callback`
4. "Connect my account" 클릭하여 Google 계정 연동

### Gmail OAuth2 설정
1. "Credentials" → "Create New" → "Gmail OAuth2 API"
2. Google OAuth2 정보 입력 (Google Sheets와 동일한 정보 사용 가능)
3. Gmail API 권한 승인

### Naver OAuth2 설정 (카페 포스팅용)
1. [네이버 개발자 센터](https://developers.naver.com/)에서 애플리케이션 등록
2. 카페 API 권한 신청
3. n8n에서 "OAuth2 API" 인증 정보 생성:
   - Authorization URL: `https://nid.naver.com/oauth2.0/authorize`
   - Access Token URL: `https://nid.naver.com/oauth2.0/token`
   - Client ID: 네이버에서 발급받은 클라이언트 ID
   - Client Secret: 네이버에서 발급받은 클라이언트 시크릿

## 워크플로우 설정 수정

### 이메일 워크플로우 (`email-workflow.json`)

#### [1] React에서 실행 (Webhook 노드)
- **Path**: `webhook-email-start`
- **Method**: POST
- 생성된 웹훅 URL을 React 앱의 `triggerEmailWorkflow` 함수에서 사용

#### [2] 구글 시트 읽기
- **Credential**: 위에서 생성한 Google Sheets OAuth2 인증 정보 선택
- **Document ID**: `={{$json.body.sheet_id}}` (React에서 전달받음)
- **Sheet Name**: `={{$json.body.sheet_name}}` (React에서 전달받음)
- **Operation**: Read

#### [5] Gmail 발송
- **Credential**: 위에서 생성한 Gmail OAuth2 인증 정보 선택
- **To**: `={{$json.이메일}}`
- **Subject**: 자동 생성된 제목 사용
- **Text**: 자동 생성된 본문 사용

### 카페 포스팅 워크플로우 (`cafe-post-workflow.json`)

#### [1] React에서 실행 (Webhook 노드)
- **Path**: `webhook-cafe-post`
- **Method**: POST
- 생성된 웹훅 URL을 React 앱의 `triggerCafeWorkflow` 함수에서 사용

#### [3] Naver Cafe API 요청
- **URL**: `https://openapi.naver.com/v1/cafe/{CAFE_ID}/menu/{MENU_ID}/articles`
  - `{CAFE_ID}`: 실제 카페 ID로 변경
  - `{MENU_ID}`: 실제 메뉴 ID로 변경
- **Authentication**: 위에서 생성한 Naver OAuth2 인증 정보 선택
- **Method**: POST
- **Body Parameters**:
  - `subject`: `={{$last.json.cafe_subject}}`
  - `content`: `={{$last.json.cafe_body}}`

## React 앱에서 웹훅 URL 업데이트

n8n에서 워크플로우를 활성화한 후, 각 웹훅 노드에서 생성된 URL을 복사하여 React 앱의 다음 부분을 수정하세요:

### `react-control-panel/src/App.js` 파일에서:

```javascript
// 이메일 워크플로우 웹훅 URL
const webhookUrl = 'http://localhost:5678/webhook/YOUR_EMAIL_WEBHOOK_ID';

// 카페 포스팅 워크플로우 웹훅 URL  
const webhookUrl = 'http://localhost:5678/webhook/YOUR_CAFE_WEBHOOK_ID';
```

## 테스트 방법

### 1. 전체 시스템 테스트
1. `python start_system.py` 실행
2. n8n 실행 (`n8n start`)
3. React 제어판에서 각 단계별로 테스트

### 2. 개별 워크플로우 테스트
1. n8n에서 워크플로우 선택
2. "Execute Workflow" 버튼 클릭
3. 테스트 데이터 입력하여 실행

## 문제 해결

### 웹훅 연결 실패
- n8n이 실행 중인지 확인
- 웹훅 URL이 정확한지 확인
- 방화벽 설정 확인

### Google API 인증 실패
- Google Cloud Console에서 API가 활성화되어 있는지 확인
- OAuth2 리다이렉트 URL이 정확한지 확인
- 인증 정보가 올바른지 확인

### 네이버 API 인증 실패
- 네이버 개발자 센터에서 애플리케이션 상태 확인
- 카페 API 권한이 승인되었는지 확인
- 클라이언트 ID/Secret이 정확한지 확인

## 보안 주의사항

1. **인증 정보 보호**: OAuth2 클라이언트 시크릿 등은 절대 공개하지 마세요
2. **HTTPS 사용**: 프로덕션 환경에서는 HTTPS를 사용하세요
3. **권한 최소화**: 필요한 최소한의 API 권한만 요청하세요
4. **로그 관리**: 민감한 정보가 로그에 기록되지 않도록 주의하세요