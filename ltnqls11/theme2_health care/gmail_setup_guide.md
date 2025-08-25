# Gmail 알림 설정 가이드

VDT 휴식 알리미에서 실제 이메일을 발송하려면 Gmail 앱 비밀번호 설정이 필요합니다.

## 1단계: Gmail 2단계 인증 활성화

1. [Google 계정 관리](https://myaccount.google.com/) 페이지로 이동
2. **보안** 탭 클릭
3. **2단계 인증** 활성화

## 2단계: Gmail 앱 비밀번호 생성

1. 2단계 인증 활성화 후 **앱 비밀번호** 메뉴로 이동
2. **앱 선택** → **메일** 선택
3. **기기 선택** → **Windows 컴퓨터** 선택
4. **생성** 버튼 클릭
5. 생성된 16자리 앱 비밀번호를 복사

## 3단계: .env 파일 업데이트

```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=generated-16-digit-password
```

## 4단계: 테스트

```bash
# 스케줄러 테스트
python test_scheduler_simple.py

# 실제 스케줄러 실행
python start_scheduler.py
```

## 주의사항

- 앱 비밀번호는 일반 Gmail 비밀번호와 다릅니다
- 2단계 인증이 활성화되어야 앱 비밀번호를 생성할 수 있습니다
- 앱 비밀번호는 공백 없이 16자리로 입력해주세요

## 문제 해결

- **535 인증 오류**: 앱 비밀번호가 잘못되었거나 2단계 인증이 비활성화됨
- **SMTP 연결 오류**: 방화벽이나 보안 프로그램에서 차단된 경우
- **시간대 문제**: 근무 시간 설정을 확인해주세요