# n8n 수동 워크플로우 생성 가이드

## 🚨 Import 오류가 계속 발생하는 경우

JSON 파일 import가 계속 실패한다면, 수동으로 워크플로우를 생성하는 것이 가장 확실한 방법입니다.

## 🚀 수동 생성 단계별 가이드

### 1단계: 빈 워크플로우 생성

1. n8n 웹 인터페이스 접속
2. "New workflow" 클릭
3. 빈 워크플로우가 생성됨

### 2단계: Cron Trigger 노드 추가

1. **노드 추가**: "+" 버튼 클릭 → "Cron" 검색 → 선택
2. **노드 이름**: "25분마다 실행"으로 변경
3. **설정**:
   - **Mode**: "Every X minutes"
   - **Minutes**: `25`
4. **저장**: "Save" 클릭

### 3단계: Code 노드 추가

1. **노드 추가**: "+" 버튼 클릭 → "Code" 검색 → 선택
2. **노드 이름**: "메시지 생성"으로 변경
3. **JavaScript 코드 복사**:

```javascript
const now = new Date();
const currentHour = now.getHours();
const currentTime = now.toFormat('HH:mm');

// 업무시간 체크 (09:00-18:00)
if (currentHour < 9 || currentHour >= 18) {
  return [];
}

// 시간대별 건강 팁
let healthTip = "";
if (currentHour < 12) {
  healthTip = "🌅 아침: 충분한 수분을 섭취하고 가벼운 스트레칭으로 하루를 시작하세요!";
} else if (currentHour < 15) {
  healthTip = "☀️ 점심: 건강한 점심 후 가벼운 산책이나 스트레칭을 권장합니다.";
} else {
  healthTip = "🌆 오후: 눈의 피로를 줄이기 위해 20-20-20 법칙을 실천하세요.";
}

const message = `⏰ 휴식시간 알림 (${currentTime})

💻 장시간 컴퓨터 작업으로 인한 건강 관리가 필요합니다!

${healthTip}

🔍 올바른 자세 점검:
🧘 턱을 살짝 당기기
🤷 어깨는 자연스럽게 내리기
🦒 목을 앞으로 빼지 않기
🪑 등받이에 허리를 완전히 붙이기
🦶 발바닥 전체가 바닥에 닿게
🦵 무릎 각도 90도 유지

💡 자세 교정 팁:
🐢 모니터 상단이 눈높이와 같도록 조절하세요
🧘 가슴을 펴고 어깨를 뒤로 젖히는 스트레칭을 하세요
🪑 1시간마다 일어나서 가볍게 걸어주세요
✍️ 손목이 꺾이지 않도록 중립 위치를 유지하세요

🏃‍♂️ 간단한 스트레칭:
• 목 좌우 돌리기 (10초씩 3회)
• 어깨 으쓱하기 (10회)
• 손목 돌리기 (각 방향 10회)
• 허리 비틀기 (각 방향 15초)

⏱️ 다음 휴식시간까지 25분 남았습니다.

💪 건강한 개발자 되기, 지금 시작하세요!`;

return [{
  json: {
    message: message,
    currentTime: currentTime
  }
}];
```

4. **저장**: "Save" 클릭

### 4단계: Slack 노드 추가

1. **노드 추가**: "+" 버튼 클릭 → "Slack" 검색 → 선택
2. **노드 이름**: "Slack 알림"으로 변경
3. **설정**:
   - **Authentication**: "Webhook URL" 선택
   - **Webhook URL**: `{{ $env.SLACK_WEBHOOK_URL }}`
   - **Text**: `{{ $json.message }}`
   - **Username**: "VDT 건강 관리 봇"
4. **저장**: "Save" 클릭

### 5단계: Gmail 노드 추가

1. **노드 추가**: "+" 버튼 클릭 → "Gmail" 검색 → 선택
2. **노드 이름**: "Gmail 알림"으로 변경
3. **설정**:
   - **Authentication**: "OAuth2" 선택
   - **From Email**: `{{ $env.GMAIL_ADDRESS }}`
   - **To Email**: `{{ $env.GMAIL_ADDRESS }}`
   - **Subject**: "VDT 증후군 관리 - 휴식시간 알림"
   - **Text**: `{{ $json.message }}`
4. **저장**: "Save" 클릭

### 6단계: 노드 연결

1. **Cron → Code**: Cron 노드의 출력을 Code 노드의 입력에 연결
2. **Code → Slack**: Code 노드의 출력을 Slack 노드의 입력에 연결
3. **Code → Gmail**: Code 노드의 출력을 Gmail 노드의 입력에 연결

### 7단계: 환경변수 설정

1. **Settings** → **Environment Variables** 클릭
2. **Add Variable** 클릭
3. **변수 추가**:

| Key | Value |
|-----|-------|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/...` |
| `GMAIL_ADDRESS` | `your-email@gmail.com` |

### 8단계: 워크플로우 저장 및 활성화

1. **워크플로우 저장**: "Save" 클릭
2. **워크플로우 활성화**: "Activate" 클릭

## 🔧 인증 설정

### Slack Webhook 설정

1. [Slack API](https://api.slack.com/apps) 접속
2. "Create New App" → "From scratch"
3. 앱 이름: "VDT 건강 관리 봇"
4. Features → Incoming Webhooks → "Activate Incoming Webhooks"
5. "Add New Webhook to Workspace" 클릭
6. 채널 선택 후 Webhook URL 복사

### Gmail OAuth2 설정

1. Gmail 노드에서 "Add Credential" 클릭
2. OAuth2 인증 설정
3. Gmail 주소와 앱 비밀번호 입력

## 📱 테스트 방법

1. **수동 실행**: Code 노드에서 "Execute Node" 클릭
2. **결과 확인**: 각 노드의 실행 결과 확인
3. **실제 알림 테스트**: Slack과 Gmail에서 실제 메시지 수신 확인

## 🚨 문제 해결

### Code 노드 오류
- JavaScript 문법 확인
- `now.toFormat()` 함수가 지원되지 않는 경우 `now.toLocaleTimeString()` 사용

### Slack 노드 오류
- Webhook URL 확인
- 환경변수 설정 확인

### Gmail 노드 오류
- OAuth2 인증 재설정
- 앱 비밀번호 확인

## 💡 팁

1. **단계별 테스트**: 각 노드를 하나씩 추가하고 테스트
2. **로그 확인**: 실행 결과와 오류 메시지 주의깊게 확인
3. **백업**: 정상 작동 시 워크플로우 백업

## 🔄 워크플로우 백업

수동으로 생성한 워크플로우가 정상 작동하면:
1. "Export" 클릭
2. JSON 파일로 저장
3. 향후 재사용 또는 공유 가능

---

**💡 핵심**: 수동 생성이 가장 확실한 방법입니다. 각 단계를 차근차근 진행해보세요!
