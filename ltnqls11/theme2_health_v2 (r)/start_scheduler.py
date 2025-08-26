"""
VDT 휴식 알리미 스케줄러 시작 스크립트
실제 알림 발송을 위한 백그라운드 프로세스
"""

import os
import json
from datetime import datetime
from notification_scheduler import NotificationScheduler

def main():
    print("VDT 휴식 알리미 스케줄러")
    print("=" * 40)
    
    # 설정 파일 확인
    config_file = "notification_config.json"
    if not os.path.exists(config_file):
        print("X notification_config.json 파일이 없습니다")
        print("먼저 앱에서 알리미 설정을 완료해주세요")
        return
    
    # 환경 변수 확인
    gmail_email = os.getenv("GMAIL_EMAIL", "")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
    
    if not gmail_email or not gmail_password:
        print("X .env 파일의 Gmail 설정을 확인해주세요")
        print("필요한 설정:")
        print("- GMAIL_EMAIL: Gmail 주소")
        print("- GMAIL_APP_PASSWORD: Gmail 앱 비밀번호")
        print("- Gmail 2단계 인증 활성화 필요")
        return
    
    # 설정 정보 표시
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("O 설정 확인 완료")
        print(f"- 알림 방식: {config.get('type', 'N/A')}")
        print(f"- 수신자: {config.get('email', 'N/A')}")
        print(f"- 근무 시간: {config.get('work_start', 'N/A')} ~ {config.get('work_end', 'N/A')}")
        print(f"- 휴식 간격: {config.get('interval', 'N/A')}분")
        
    except Exception as e:
        print(f"X 설정 파일 읽기 실패: {e}")
        return
    
    # 현재 시간 표시
    now = datetime.now()
    print(f"\n현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 스케줄러 시작 확인
    print("\n알리미를 시작하시겠습니까?")
    print("- 백그라운드에서 설정된 시간에 자동으로 알림이 발송됩니다")
    print("- 종료하려면 Ctrl+C를 누르세요")
    
    start_input = input("시작하시겠습니까? (y/n): ")
    
    if start_input.lower() == 'y':
        print("\n스케줄러를 시작합니다...")
        scheduler = NotificationScheduler()
        scheduler.run()
    else:
        print("스케줄러를 시작하지 않습니다")

if __name__ == "__main__":
    main()