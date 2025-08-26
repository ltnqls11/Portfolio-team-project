"""
알리미 스케줄러 테스트 스크립트
실제 이메일 발송이 되는지 확인
"""

import json
from datetime import datetime, timedelta
from notification_scheduler import NotificationScheduler
import os

def create_test_config():
    """테스트용 설정 생성"""
    # 현재 시간 기준으로 근무 시간 설정 (테스트용)
    now = datetime.now()
    work_start = (now - timedelta(minutes=10)).strftime("%H:%M")  # 10분 전부터
    work_end = (now + timedelta(hours=2)).strftime("%H:%M")      # 2시간 후까지
    
    test_config = {
        "type": "이메일 (Gmail)",
        "email": os.getenv("GMAIL_EMAIL", ""),  # .env에서 이메일 가져오기
        "slack_webhook": None,
        "work_start": work_start,
        "work_end": work_end,
        "interval": 1,  # 1분마다 테스트 (실제로는 30분 권장)
        "user_data": {
            "name": "테스트 사용자",
            "work_intensity": "높음"
        },
        "conditions": ["목 어깨 통증"],
        "pain_scores": {"목": 7, "어깨": 5},
        "created_at": datetime.now().isoformat()
    }
    
    with open("test_notification_config.json", "w", encoding="utf-8") as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"테스트 설정 생성 완료:")
    print(f"- 근무 시간: {work_start} ~ {work_end}")
    print(f"- 알림 간격: 1분")
    print(f"- 알림 방식: 이메일")

def test_immediate_notification():
    """즉시 알림 테스트"""
    print("\n=== 즉시 알림 테스트 ===")
    
    scheduler = NotificationScheduler("test_notification_config.json")
    
    if scheduler.config:
        print("O 설정 로드 성공")
        
        # 근무 시간 확인
        if scheduler.is_work_time():
            print("O 현재 근무 시간입니다")
            
            # 즉시 알림 발송 테스트
            print("이메일 테스트 알림 발송 중...")
            scheduler.send_notification()
            
        else:
            print("X 현재 근무 시간이 아닙니다")
    else:
        print("X 설정 로드 실패")

def test_scheduler_run():
    """스케줄러 실행 테스트 (30초간)"""
    print("\n=== 30초 스케줄러 테스트 ===")
    print("30초 동안 스케줄러를 실행합니다...")
    
    scheduler = NotificationScheduler("test_notification_config.json")
    
    if scheduler.setup_schedule():
        print("✅ 스케줄 설정 성공")
        
        import schedule
        import time
        
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)
        
        print(f"시작 시간: {start_time.strftime('%H:%M:%S')}")
        print(f"종료 시간: {end_time.strftime('%H:%M:%S')}")
        
        try:
            while datetime.now() < end_time:
                schedule.run_pending()
                time.sleep(1)
            
            print("✅ 30초 테스트 완료")
            
        except KeyboardInterrupt:
            print("❌ 사용자에 의해 중단됨")
    else:
        print("❌ 스케줄 설정 실패")

if __name__ == "__main__":
    print("VDT 휴식 알리미 테스트")
    print("=" * 40)
    
    # 환경 변수 확인
    gmail_email = os.getenv("GMAIL_EMAIL", "")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
    
    if not gmail_email or not gmail_password:
        print("X .env 파일의 Gmail 설정을 확인해주세요.")
        print("필요한 설정: GMAIL_EMAIL, GMAIL_APP_PASSWORD")
    else:
        print(f"O Gmail 설정 확인: {gmail_email}")
        
        # 테스트 설정 생성
        create_test_config()
        
        # 즉시 알림 테스트
        test_immediate_notification()
        
        # 스케줄러 실행 테스트
        user_input = input("\n스케줄러 30초 테스트를 실행하시겠습니까? (y/n): ")
        if user_input.lower() == 'y':
            test_scheduler_run()
        
        # 테스트 파일 정리
        if os.path.exists("test_notification_config.json"):
            os.remove("test_notification_config.json")
            print("테스트 파일 정리 완료")