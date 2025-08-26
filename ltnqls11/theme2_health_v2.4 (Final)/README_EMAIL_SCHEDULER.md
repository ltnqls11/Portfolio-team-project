# 🚀 VDT 자동 메일 스케줄러 가이드

## 📋 개요

이 시스템은 사용자가 선택한 시간 동안 원하는 시간 단위로 메일이 자동 발송되는 기능을 제공합니다. **Streamlit이 구동되지 않아도** 백그라운드에서 독립적으로 작동합니다.

## ⚡ 주요 기능

### 🔥 NEW! 자동 메일 스케줄러
- ✅ **Streamlit 종료 후에도 백그라운드에서 자동 실행**
- ✅ **시간 단위 간격** (1, 2, 3, 4, 6, 8시간)
- ✅ **근무 시간 내에만 발송**
- ✅ **평일/매일 발송 선택 가능**
- ✅ **실시간 스케줄러 상태 확인**

### 📧 기존 알림 방식
- 📧 이메일 (Gmail) 알림
- 💬 Slack 알림
- ⏰ 분 단위 간격 (15-120분)

## 🛠️ 사용 방법

### 1. Streamlit에서 설정

1. **개인정보 입력** 단계에서 이메일 주소 입력
2. **휴식 알리미 설정** 메뉴로 이동
3. **"자동 메일 스케줄러 사용"** 체크박스 선택
4. 발송 시간 및 간격 설정
5. **"🚀 자동 스케줄러 시작"** 버튼 클릭

### 2. 독립 실행

Streamlit을 종료해도 메일이 계속 발송되도록 하려면:

```bash
# 방법 1: 독립 실행 스크립트 사용 (권장)
python start_auto_email.py

# 방법 2: 직접 스케줄러 실행
python email_scheduler.py start
```

### 3. 스케줄러 제어

```bash
# 스케줄러 중지
python email_scheduler.py stop

# 스케줄러 상태 확인
python email_scheduler.py status
```

## 📊 설정 파일

### `email_schedule_config.json`
자동 메일 스케줄러 설정 파일:
```json
{
  "enabled": true,
  "email_settings": {
    "recipient_email": "user@example.com",
    "subject_template": "🏃‍♂️ VDT 건강 관리 알림",
    "sender_name": "VDT 건강 관리 시스템"
  },
  "schedule_settings": {
    "send_time": "09:00",
    "interval_hours": 4,
    "work_days_only": true,
    "work_start_time": "09:00",
    "work_end_time": "18:00"
  }
}
```

### `notification_config.json`
기존 알림 방식 설정 파일 (분 단위 간격)

## 🚨 주의사항

### Gmail 설정 필요
`.env` 파일에 Gmail 설정이 필요합니다:
```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Gmail 앱 패스워드 생성 방법
1. Google 계정 설정 → 보안
2. 2단계 인증 활성화
3. 앱 패스워드 생성
4. 생성된 패스워드를 `.env`에 입력

## 🔍 상태 확인

### Streamlit 사이드바
- 스케줄러 실행 상태
- 발송 횟수
- 마지막 발송 시간

### 로그 파일
- `email_scheduler.log`: 자동 스케줄러 로그
- `notification_scheduler.log`: 기존 스케줄러 로그

## 🛡️ 보안

- 이메일 설정 정보는 `.env` 파일에서 관리
- 민감한 정보는 코드에 하드코딩되지 않음
- 앱 패스워드 사용으로 보안 강화

## 📞 문제 해결

### 스케줄러가 시작되지 않는 경우
1. Gmail 설정 확인 (`.env` 파일)
2. 이메일 주소 입력 확인
3. 스케줄러 활성화 상태 확인

### 메일이 발송되지 않는 경우
1. 근무 시간 설정 확인
2. 평일/매일 설정 확인
3. Gmail 인증 정보 확인
4. 로그 파일 확인

### 로그 확인 명령어
```bash
# 실시간 로그 모니터링
tail -f email_scheduler.log

# 최근 로그 확인
cat email_scheduler.log | tail -20
```

## 🎯 활용 예시

### 시나리오 1: 일반 직장인
- 근무시간: 09:00 ~ 18:00
- 발송간격: 4시간마다
- 평일만 발송
- → 09:00, 13:00, 17:00에 발송

### 시나리오 2: 야간 근무자
- 근무시간: 22:00 ~ 06:00
- 발송간격: 2시간마다
- 매일 발송
- → 22:00, 00:00, 02:00, 04:00, 06:00에 발송

---

💪 **건강한 개발 생활을 응원합니다!**