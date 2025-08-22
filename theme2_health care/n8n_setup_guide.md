# n8n VDT 증후군 관리 - 휴식시간 알리미 설정 가이드

## 📋 개요

이 워크플로우는 `posture_tip_notifier.py`와 `app_sb.py`의 내용을 참고하여 생성된 n8n 워크플로우입니다. 25분마다 Slack과 Gmail로 휴식시간 알림을 보내며, '올바른 컴퓨터 작업 자세' 정보를 포함합니다.

## 🚀 주요 기능

- ⏰ **25분마다 자동 알림**: Murrel 공식에 따른 권장 휴식시간
- 🕘 **업무시간 필터링**: 09:00-18:00 사이에만 알림 발송
- 💬 **Slack 알림**: 웹훅을 통한 실시간 알림
- 📧 **Gmail 알림**: 이메일을 통한 상세한 건강 정보
- 💺 **올바른 자세 가이드**: 모니터, 의자, 키보드, 목/어깨 자세
- 🏃‍♂️ **스트레칭 가이드**: 간단한 운동 방법 제시
- 🎯 **VDT 증후군별 팁**: 거북목, 라운드숄더, 허리디스크, 손목터널증후군

## ⚙️ 설정 방법

### 1. n8n 설치 및 실행

```bash
# n8n 설치
npm install -g n8n

# n8n 실행
n8n start
```

### 2. 워크플로우 가져오기

1. n8n 웹 인터페이스 접속 (기본: http://localhost:5678)
2. "Import from file" 클릭
3. `n8n_rest_reminder_workflow.json` 파일 업로드

### 3. 환경변수 설정

#### 방법 1: n8n 웹 인터페이스에서 설정
1. Settings → Environment Variables
2. 다음 변수들을 추가:

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/...` | Slack Incoming Webhook URL |
| `GMAIL_ADDRESS` | `your-email@gmail.com` | Gmail 주소 |
| `WORK_START_TIME` | `09:00` | 업무 시작 시간 (선택) |
| `WORK_END_TIME` | `18:00` | 업무 종료 시간 (선택) |
| `REST_INTERVAL` | `25` | 휴식 간격 (분, 선택) |

#### 방법 2: .env 파일 사용
1. `n8n_environment_variables.env` 파일을 `.env`로 복사
2. 실제 값으로 수정
3. n8n 실행 시 환경변수 로드

### 4. Slack 설정

1. **Slack 앱 생성**:
   - [Slack API](https://api.slack.com/apps) 접속
   - "Create New App" → "From scratch"
   - 앱 이름: "VDT 건강 관리 봇"

2. **Incoming Webhooks 활성화**:
   - Features → Incoming Webhooks → "Activate Incoming Webhooks"
   - "Add New Webhook to Workspace" 클릭
   - 채널 선택 후 Webhook URL 복사

3. **환경변수에 Webhook URL 설정**

### 5. Gmail 설정

1. **Gmail 2단계 인증 활성화**:
   - Google 계정 → 보안 → 2단계 인증

2. **앱 비밀번호 생성**:
   - Google 계정 → 보안 → 앱 비밀번호
   - "앱 선택" → "기타" → 이름 입력 (예: "n8n VDT 알리미")
   - 생성된 16자리 비밀번호 복사

3. **n8n Gmail 노드 인증**:
   - Gmail 노드에서 "Add Credential" 클릭
   - OAuth2 인증 설정
   - Gmail 주소와 앱 비밀번호 입력

## 🔧 워크플로우 구조

```
[Cron Trigger] → [업무시간 확인] → [메시지 생성] → [Slack + Gmail 전송] → [결과 로깅]
     ↓                ↓              ↓                    ↓              ↓
  25분마다      09:00-18:00    건강 정보 + 자세 가이드   알림 전송    전송 결과 기록
```

### 노드별 기능

1. **휴식시간 알리미 (Cron Trigger)**
   - 25분마다 실행
   - Murrel 공식 기반 휴식시간

2. **업무시간 확인 (IF)**
   - 09:00-18:00 사이에만 실행
   - 업무 외 시간에는 알림 중단

3. **알림 메시지 생성 (Code)**
   - 현재 시간 기반 맞춤 메시지
   - 올바른 자세 가이드 포함
   - VDT 증후군별 팁 제공
   - 간단한 스트레칭 방법

4. **Slack 알림 전송**
   - 웹훅을 통한 실시간 메시지
   - 봇 이름: "VDT 건강 관리 봇"
   - 이모지: :computer:

5. **Gmail 알림 전송**
   - HTML 형식의 상세한 건강 정보
   - 제목: "VDT 증후군 관리 - 휴식시간 알림"

6. **알림 전송 결과 로깅**
   - Slack/Gmail 전송 결과 기록
   - 다음 알림 시간 안내

## 📱 알림 메시지 예시

```
⏰ 휴식시간 알림 (14:00)

💻 장시간 컴퓨터 작업으로 인한 건강 관리가 필요합니다!

☀️ 점심: 건강한 점심 후 가벼운 산책이나 스트레칭을 권장합니다.

🔍 현재 자세 점검:
🧘 턱을 살짝 당기기
🤷 어깨는 자연스럽게 내리기
🦒 목을 앞으로 빼지 않기
🪑 등받이에 허리를 완전히 붙이기
🦶 발바닥 전체가 바닥에 닿게
🦵 무릎 각도 90도 유지

💡 자세 교정 팁:
🐢 모니터 상단이 눈높이와 같도록 조절하고, 턱을 가볍게 당겨 목이 앞으로 나오지 않게 해주세요.
🧘 가슴을 펴고 어깨를 뒤로 젖히는 스트레칭을 해주세요.
🪑 의자에 앉을 때는 허리를 등받이에 밀착시키고, 1시간마다 일어나서 가볍게 걸어주세요.
✍️ 키보드와 마우스 사용 시 손목이 꺾이지 않도록 중립 위치를 유지하세요.

🏃‍♂️ 간단한 스트레칭:
• 목 좌우 돌리기 (10초씩 3회)
• 어깨 으쓱하기 (10회)
• 손목 돌리기 (각 방향 10회)
• 허리 비틀기 (각 방향 15초)

⏱️ 다음 휴식시간까지 25분 남았습니다.

💪 건강한 개발자 되기, 지금 시작하세요!
```

## 🎯 커스터마이징

### 휴식 간격 변경
- `REST_INTERVAL` 환경변수 수정
- Cron Trigger의 `minutesInterval` 값 변경

### 업무시간 변경
- `WORK_START_TIME`, `WORK_END_TIME` 환경변수 수정
- IF 노드의 조건값 수정

### 메시지 내용 수정
- "알림 메시지 생성" 노드의 JavaScript 코드 수정
- 자세 가이드, 건강 팁, 스트레칭 방법 등 커스터마이징

## 🚨 주의사항

1. **Gmail 보안**: 앱 비밀번호 사용 필수 (일반 비밀번호 사용 불가)
2. **Slack 권한**: 웹훅 URL은 민감한 정보이므로 안전하게 보관
3. **환경변수**: 실제 값으로 반드시 수정 후 사용
4. **테스트**: 워크플로우 활성화 전 테스트 실행 권장

## 🔍 문제 해결

### Slack 알림이 안 올 때
- Webhook URL 확인
- Slack 앱 권한 확인
- 채널 설정 확인

### Gmail 알림이 안 올 때
- 2단계 인증 활성화 확인
- 앱 비밀번호 재생성
- OAuth2 인증 재설정

### 워크플로우가 실행되지 않을 때
- Cron Trigger 설정 확인
- 업무시간 조건 확인
- 환경변수 설정 확인

## 📚 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [Slack API 문서](https://api.slack.com/)
- [Gmail API 문서](https://developers.google.com/gmail/api)
- [VDT 증후군 예방 가이드](https://www.osha.gov/ergonomics/computer-workstation)

## 🤝 지원

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.
