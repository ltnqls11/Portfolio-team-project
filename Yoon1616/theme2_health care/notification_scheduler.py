import json
import time
import schedule
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import random

class NotificationScheduler:
    def __init__(self):
        self.config = self.load_config()
        self.exercise_messages = [
            "🏃‍♂️ 휴식 시간입니다! 목과 어깨를 스트레칭해보세요.",
            "💺 잠깐 일어나서 허리를 펴고 스트레칭하세요!",
            "👀 눈의 피로를 위해 먼 곳을 바라보며 휴식하세요.",
            "🤲 손목과 손가락을 가볍게 풀어주세요.",
            "🧘‍♂️ 깊게 숨을 쉬며 어깨의 긴장을 풀어보세요.",
            "🚶‍♂️ 잠깐 자리에서 일어나 걸어보세요!",
        ]
    
    def load_config(self):
        """설정 파일 로드"""
        try:
            with open("notification_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("설정 파일이 없습니다. Streamlit 앱에서 먼저 설정해주세요.")
            return None
    
    def load_exercise_routine(self):
        """운동 루틴 로드"""
        try:
            with open("my_exercise_routine.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def send_email_notification(self, message):
        """이메일 알림 발송"""
        if not self.config or not self.config.get('email'):
            return False
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.config['email']
            msg['To'] = self.config['email']
            msg['Subject'] = "🔔 VDT 관리 - 휴식 시간 알림"
            
            # 운동 루틴 추가
            routine = self.load_exercise_routine()
            if routine and routine.get('break_exercises'):
                exercise = random.choice(routine['break_exercises'])
                message += f"\n\n📋 추천 운동: {exercise['name']}\n"
                message += f"방법: {exercise['method']}\n"
                message += f"횟수: {exercise['reps']}"
            
            msg.attach(MimeText(message, 'plain', 'utf-8'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.config['email'], self.config.get('email_password', ''))
            server.send_message(msg)
            server.quit()
            
            print(f"이메일 알림 발송 완료: {datetime.now()}")
            return True
        except Exception as e:
            print(f"이메일 발송 실패: {str(e)}")
            return False
    
    def send_slack_notification(self, message):
        """Slack 알림 발송"""
        if not self.config or not self.config.get('slack_webhook'):
            return False
        
        try:
            # 운동 루틴 추가
            routine = self.load_exercise_routine()
            if routine and routine.get('break_exercises'):
                exercise = random.choice(routine['break_exercises'])
                message += f"\n\n📋 *추천 운동*: {exercise['name']}\n"
                message += f"*방법*: {exercise['method']}\n"
                message += f"*횟수*: {exercise['reps']}"
            
            payload = {
                "text": message,
                "username": "VDT 관리봇",
                "icon_emoji": ":computer:"
            }
            
            response = requests.post(self.config['slack_webhook'], json=payload)
            
            if response.status_code == 200:
                print(f"Slack 알림 발송 완료: {datetime.now()}")
                return True
            else:
                print(f"Slack 발송 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"Slack 발송 실패: {str(e)}")
            return False
    
    def send_notification(self):
        """알림 발송"""
        if not self.config:
            return
        
        # 현재 시간이 업무 시간인지 확인
        now = datetime.now().time()
        work_start = datetime.strptime(self.config['work_start'], "%H:%M").time()
        work_end = datetime.strptime(self.config['work_end'], "%H:%M").time()
        
        if not (work_start <= now <= work_end):
            return
        
        message = random.choice(self.exercise_messages)
        
        notification_type = self.config.get('type', '')
        
        if notification_type in ["이메일 (Gmail)", "둘 다"]:
            self.send_email_notification(message)
        
        if notification_type in ["Slack", "둘 다"]:
            self.send_slack_notification(message)
    
    def start_scheduler(self):
        """스케줄러 시작"""
        if not self.config:
            print("설정이 없습니다. 종료합니다.")
            return
        
        interval = self.config.get('interval', 25)
        
        # 스케줄 등록
        schedule.every(interval).minutes.do(self.send_notification)
        
        print(f"🔔 VDT 관리 알리미가 시작되었습니다!")
        print(f"⏰ {interval}분마다 알림을 발송합니다.")
        print(f"🕐 업무 시간: {self.config['work_start']} - {self.config['work_end']}")
        print("종료하려면 Ctrl+C를 누르세요.\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n알리미가 종료되었습니다.")

if __name__ == "__main__":
    scheduler = NotificationScheduler()
    scheduler.start_scheduler()