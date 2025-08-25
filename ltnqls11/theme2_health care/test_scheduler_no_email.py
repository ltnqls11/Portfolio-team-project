"""
이메일 발송 없이 스케줄러 로직만 테스트
실제 알림 시간에 콘솔 메시지만 출력
"""

import schedule
import time
import json
from datetime import datetime, timedelta
import os

class TestNotificationScheduler:
    def __init__(self):
        self.config_file = "notification_config.json"
        self.config = None
        self.last_notification = None
        self.notification_count = 0
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ 설정 로드 성공: {self.config.get('email', 'N/A')}")
                print(f"근무시간: {self.config.get('work_start')} - {self.config.get('work_end')}")
                print(f"알림간격: {self.config.get('interval')}분")
                return True
            else:
                print("❌ notification_config.json 파일이 없습니다")
                return False
        except Exception as e:
            print(f"❌ 설정 로드 실패: {e}")
            return False
    
    def is_work_time(self):
        if not self.config:
            return False
        
        try:
            now = datetime.now().time()
            work_start = datetime.strptime(self.config['work_start'], "%H:%M").time()
            work_end = datetime.strptime(self.config['work_end'], "%H:%M").time()
            return work_start <= now <= work_end
        except:
            return False
    
    def send_test_notification(self):
        """실제 발송 대신 콘솔에 메시지 출력"""
        self.notification_count += 1
        now = datetime.now()
        
        print(f"\n🔔 [{now.strftime('%H:%M:%S')}] 휴식 알림 #{self.notification_count}")
        print(f"📧 수신자: {self.config.get('email', 'N/A')}")
        print(f"⏰ 다음 알림: {(now + timedelta(minutes=self.config.get('interval', 30))).strftime('%H:%M')}")
        print("💡 목과 어깨 스트레칭을 해보세요!")
        
        self.last_notification = now
        return True
    
    def check_and_notify(self):
        if not self.is_work_time():
            return
        
        interval = self.config.get('interval', 30)
        now = datetime.now()
        
        if (self.last_notification is None or 
            (now - self.last_notification).total_seconds() >= interval * 60):
            self.send_test_notification()
    
    def run_test(self, duration_minutes=2):
        """지정된 시간 동안 테스트 실행"""
        if not self.config:
            return
        
        # 테스트를 위해 간격을 30초로 조정
        original_interval = self.config['interval']
        self.config['interval'] = 0.5  # 30초
        
        schedule.every().minute.do(self.check_and_notify)
        
        print(f"\n🚀 {duration_minutes}분 동안 스케줄러 테스트 시작")
        print("(테스트용으로 30초마다 알림)")
        print("=" * 50)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        try:
            while datetime.now() < end_time:
                schedule.run_pending()
                time.sleep(1)
                
            print(f"\n✅ 테스트 완료! 총 {self.notification_count}개의 알림이 발송되었습니다")
            
        except KeyboardInterrupt:
            print(f"\n⚠️ 사용자에 의해 중단됨. 총 {self.notification_count}개 알림 발송")
        
        # 원래 간격으로 복원
        self.config['interval'] = original_interval

if __name__ == "__main__":
    print("VDT 휴식 알리미 - 테스트 모드")
    print("=" * 40)
    
    scheduler = TestNotificationScheduler()
    
    if scheduler.config:
        if scheduler.is_work_time():
            print("✅ 현재 근무 시간입니다")
            scheduler.run_test(2)  # 2분간 테스트
        else:
            print("⚠️ 현재 근무 시간이 아닙니다")
            print(f"근무 시간: {scheduler.config.get('work_start')} - {scheduler.config.get('work_end')}")
            print("테스트를 진행하시겠습니까? (y/n): ", end="")
            if input().lower() == 'y':
                # 강제로 근무 시간으로 설정
                now = datetime.now()
                scheduler.config['work_start'] = (now - timedelta(minutes=1)).strftime("%H:%M")
                scheduler.config['work_end'] = (now + timedelta(hours=1)).strftime("%H:%M")
                scheduler.run_test(2)
    else:
        print("설정 파일을 먼저 생성해주세요 (앱에서 알리미 설정)")