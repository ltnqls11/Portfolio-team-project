"""
VDT 증후군 관리 시스템 - 휴식 알리미 스케줄러
정기적으로 휴식 알림을 발송하는 백그라운드 서비스
"""

import schedule
import time
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotificationScheduler:
    def __init__(self, config_file="notification_config.json"):
        """알림 스케줄러 초기화"""
        self.config_file = config_file
        self.config = None
        self.last_notification = None
        self.notification_count = 0
        
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"설정 파일을 찾을 수 없습니다: {self.config_file}")
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info("설정 파일 로드 완료")
            logger.info(f"알림 방식: {self.config.get('type', 'N/A')}")
            logger.info(f"근무 시간: {self.config.get('work_start', 'N/A')} - {self.config.get('work_end', 'N/A')}")
            logger.info(f"휴식 간격: {self.config.get('interval', 'N/A')}분")
            
            return True
            
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return False
    
    def is_work_time(self):
        """현재 시간이 근무 시간인지 확인"""
        if not self.config:
            return False
        
        try:
            now = datetime.now().time()
            work_start = datetime.strptime(self.config['work_start'], "%H:%M").time()
            work_end = datetime.strptime(self.config['work_end'], "%H:%M").time()
            
            # 같은 날 근무 시간 내인지 확인
            if work_start <= work_end:
                return work_start <= now <= work_end
            else:
                # 자정을 넘는 경우 (야간 근무)
                return now >= work_start or now <= work_end
                
        except Exception as e:
            logger.error(f"근무 시간 확인 중 오류: {e}")
            return False
    
    def send_email_notification(self):
        """이메일 알림 발송"""
        try:
            if not self.config.get('email') or not self.config.get('email_password'):
                logger.warning("이메일 설정이 없습니다.")
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = self.config['email']
            msg['Subject'] = "🏃‍♂️ VDT 휴식 알리미"
            
            # 알림 메시지 생성
            body = self.generate_notification_message()
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.config['email'], self.config['email_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("이메일 알림 발송 성공")
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def send_slack_notification(self):
        """Slack 알림 발송"""
        try:
            if not self.config.get('slack_webhook'):
                logger.warning("Slack 설정이 없습니다.")
                return False
            
            # Slack 메시지 생성
            message = self.generate_notification_message()
            
            payload = {
                "text": message,
                "username": "VDT 휴식 알리미",
                "icon_emoji": ":runner:"
            }
            
            response = requests.post(self.config['slack_webhook'], json=payload)
            
            if response.status_code == 200:
                logger.info("Slack 알림 발송 성공")
                return True
            else:
                logger.error(f"Slack 발송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 발송 실패: {e}")
            return False
    
    def generate_notification_message(self):
        """알림 메시지 생성"""
        interval = self.config.get('interval', 30)
        self.notification_count += 1
        
        # 시간대별 맞춤 메시지
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            time_greeting = "좋은 아침입니다!"
            exercise_tip = "목과 어깨 스트레칭으로 하루를 시작하세요."
        elif 12 <= current_hour < 18:
            time_greeting = "오후에도 화이팅!"
            exercise_tip = "허리를 펴고 심호흡을 해보세요."
        elif 18 <= current_hour < 22:
            time_greeting = "저녁 시간이네요!"
            exercise_tip = "하루 종일 수고하셨습니다. 가벼운 스트레칭으로 마무리하세요."
        else:
            time_greeting = "늦은 시간까지 수고하셨습니다!"
            exercise_tip = "목과 눈의 피로를 풀어주세요."
        
        # 운동 추천 (랜덤)
        exercises = [
            "목 좌우 돌리기 (각 방향 10초씩)",
            "어깨 으쓱하기 (10회)",
            "손목 위아래 구부리기 (10회)",
            "허리 좌우 비틀기 (각 방향 5회)",
            "심호흡하며 팔 들어 올리기 (5회)",
            "발목 돌리기 (각 방향 10회)",
            "목 앞뒤 숙이기 (천천히 5회)"
        ]
        
        import random
        recommended_exercise = random.choice(exercises)
        
        # 다음 알림 시간 계산
        next_time = datetime.now() + timedelta(minutes=interval)
        next_time_str = next_time.strftime("%H:%M")
        
        message = f"""🏃‍♂️ **VDT 휴식 알리미** (#{self.notification_count})

{time_greeting}
{interval}분이 지났습니다. 잠깐 휴식을 취해보세요!

💡 **추천 운동**: {recommended_exercise}
🎯 **운동 팁**: {exercise_tip}

⏰ **다음 알림**: {next_time_str}
📅 **오늘 알림 횟수**: {self.notification_count}회

건강한 개발 생활을 응원합니다! 💻✨
- VDT 증후군 관리 시스템
"""
        
        return message
    
    def send_notification(self):
        """알림 발송 (설정된 방식에 따라)"""
        if not self.config:
            logger.error("설정이 로드되지 않았습니다.")
            return
        
        if not self.is_work_time():
            logger.info("근무 시간이 아닙니다. 알림을 건너뜁니다.")
            return
        
        notification_type = self.config.get('type', '')
        success = False
        
        try:
            if notification_type in ["이메일 (Gmail)", "둘 다"]:
                email_success = self.send_email_notification()
                success = success or email_success
            
            if notification_type in ["Slack", "둘 다"]:
                slack_success = self.send_slack_notification()
                success = success or slack_success
            
            if success:
                self.last_notification = datetime.now()
                logger.info(f"알림 발송 완료 (총 {self.notification_count}회)")
            else:
                logger.error("모든 알림 발송 실패")
                
        except Exception as e:
            logger.error(f"알림 발송 중 오류: {e}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        if not self.config:
            logger.error("설정을 먼저 로드해주세요.")
            return False
        
        interval = self.config.get('interval', 30)
        
        # 매 분마다 확인하여 정확한 시간에 알림
        schedule.every().minute.do(self.check_and_notify)
        
        logger.info(f"스케줄 설정 완료: {interval}분마다 알림")
        return True
    
    def check_and_notify(self):
        """시간 확인 후 알림 발송"""
        if not self.is_work_time():
            return
        
        interval = self.config.get('interval', 30)
        now = datetime.now()
        
        # 첫 번째 알림이거나 지정된 간격이 지났으면 알림 발송
        if (self.last_notification is None or 
            (now - self.last_notification).total_seconds() >= interval * 60):
            self.send_notification()
    
    def run(self):
        """스케줄러 실행"""
        if not self.load_config():
            logger.error("설정 로드 실패. 프로그램을 종료합니다.")
            return
        
        if not self.setup_schedule():
            logger.error("스케줄 설정 실패. 프로그램을 종료합니다.")
            return
        
        logger.info("=== VDT 휴식 알리미 시작 ===")
        logger.info("프로그램을 종료하려면 Ctrl+C를 누르세요.")
        
        try:
            # 시작 메시지 발송
            if self.is_work_time():
                self.config['type'] = self.config.get('type', '')
                start_message = f"""🚀 **VDT 휴식 알리미가 시작되었습니다!**

⏰ 근무 시간: {self.config.get('work_start', 'N/A')} - {self.config.get('work_end', 'N/A')}
📅 휴식 간격: {self.config.get('interval', 30)}분마다
📧 알림 방식: {self.config.get('type', 'N/A')}

건강한 하루 되세요! 💪"""
                
                # 임시로 메시지 변경하여 시작 알림 발송
                original_generate = self.generate_notification_message
                self.generate_notification_message = lambda: start_message
                self.send_notification()
                self.generate_notification_message = original_generate
                self.notification_count = 0  # 카운트 리셋
            
            # 메인 루프
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("사용자에 의해 프로그램이 종료되었습니다.")
        except Exception as e:
            logger.error(f"프로그램 실행 중 오류: {e}")
        finally:
            # 종료 메시지 발송
            if self.is_work_time() and self.notification_count > 0:
                end_message = f"""👋 **VDT 휴식 알리미가 종료되었습니다.**

오늘 총 {self.notification_count}회의 휴식 알림을 보내드렸습니다.
수고하셨습니다! 🎉

내일도 건강한 개발 생활 되세요! 💻✨"""
                
                original_generate = self.generate_notification_message
                self.generate_notification_message = lambda: end_message
                self.send_notification()
                self.generate_notification_message = original_generate
            
            logger.info("=== VDT 휴식 알리미 종료 ===")

def main():
    """메인 함수"""
    scheduler = NotificationScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
