# n8n 워크플로우 설정

이 디렉토리는 마케팅 자동화를 위한 n8n 워크플로우를 관리합니다.

## 설치 및 실행

```bash
# n8n 설치
npm install

# n8n 시작 (로컬)
npm start

# n8n 시작 (터널 모드 - 외부 웹훅 테스트용)
npm run dev
```

## 워크플로우 관리

```bash
# 모든 워크플로우 내보내기
npm run export

# 워크플로우 가져오기
npm run import
```

## 주요 워크플로우

### 1. 캠페인 자동화 워크플로우
- **트리거**: Flask API에서 웹훅 호출
- **기능**: 캠페인 생성 → AI 문구 생성 → 승인 대기

### 2. 이메일 발송 워크플로우
- **트리거**: 문구 승인 완료 웹훅
- **기능**: 인플루언서 목록 조회 → 개인화 이메일 생성 → 대량 발송

### 3. 상태 추적 워크플로우
- **트리거**: 이메일 발송 상태 변경
- **기능**: 발송 결과 Flask API로 전송 → 통계 업데이트

## 환경 변수

n8n 실행 시 다음 환경 변수를 설정하세요:

```bash
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=your-password
export WEBHOOK_URL=http://localhost:5678
```

## 웹훅 엔드포인트

- 캠페인 생성: `http://localhost:5678/webhook/campaign-created`
- 문구 승인: `http://localhost:5678/webhook/copy-approved`
- 이메일 발송: `http://localhost:5678/webhook/send-emails`