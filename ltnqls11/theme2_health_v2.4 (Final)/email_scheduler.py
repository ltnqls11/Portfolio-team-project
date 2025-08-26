"""
VDT 증후군 관리 시스템 - 자동 메일 스케줄러
Streamlit과 독립적으로 실행되는 메일 자동 전송 시스템
"""

import schedule
import time
import json
import smtplib
import threading
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv
from pathlib import Path
import random

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailScheduler:
    def __init__(self, config_file="email_schedule_config.json"):
        self.config_file = config_file
        self.config = None
        self.running = False
        self.scheduler_thread = None
        self.last_email_time = None
        self.email_count = 0
        
        if not os.path.exists(self.config_file):
            self.create_default_config()
        
        self.load_config()
    
    def create_default_config(self):
        """기본 설정 파일 생성"""
        default_config = {
            "enabled": False,
            "email_settings": {
                "recipient_email": "",
                "recipient_name": "",
                "subject_template": "🏃‍♂️ VDT 건강 관리 알림",
                "sender_name": "VDT 건강 관리 시스템"
            },
            "schedule_settings": {
                "send_time": "09:00",
                "interval_minutes": 30,
                "work_days_only": True,
                "work_start_time": "09:00",
                "work_end_time": "18:00"
            },
            "message_template": {
                "greeting": "안녕하세요! VDT 건강 관리 시스템입니다.",
                "main_message": "정기적인 스트레칭과 휴식으로 건강한 근무 환경을 유지하세요.",
                "exercises": [
                    "목 좌우 돌리기 (각 방향 10초씩)",
                    "어깨 으쓱하기 (10회)",
                    "손목 위아래 구부리기 (10회)",
                    "허리 좌우 비틀기 (각 방향 5회)",
                    "심호흡하며 팔 들어 올리기 (5회)"
                ],
                "closing": "건강한 하루 되세요! 💪"
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"기본 설정 파일을 생성했습니다: {self.config_file}")
    
    def load_config(self):
        """설정 파일 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info("설정 파일 로드 완료")
            return True
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return False
    
    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info("설정 파일 저장 완료")
            return True
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            return False
    
    def update_config(self, **kwargs):
        """설정 업데이트"""
        if not self.config:
            return False
        
        for key, value in kwargs.items():
            if key in ['enabled', 'recipient_email', 'send_time', 'interval_minutes']:
                if key == 'enabled':
                    self.config['enabled'] = value
                elif key == 'recipient_email':
                    self.config['email_settings']['recipient_email'] = value
                elif key == 'send_time':
                    self.config['schedule_settings']['send_time'] = value
                elif key == 'interval_minutes':
                    self.config['schedule_settings']['interval_minutes'] = value
        
        return self.save_config()
    
    def is_work_time(self):
        """현재 시간이 근무 시간인지 확인"""
        if not self.config or not self.config['schedule_settings']['work_days_only']:
            return True
        
        try:
            now = datetime.now()
            
            # 주말 체크
            if now.weekday() >= 5:  # 토(5), 일(6)
                return False
            
            # 근무 시간 체크
            current_time = now.time()
            work_start = datetime.strptime(self.config['schedule_settings']['work_start_time'], "%H:%M").time()
            work_end = datetime.strptime(self.config['schedule_settings']['work_end_time'], "%H:%M").time()
            
            return work_start <= current_time <= work_end
            
        except Exception as e:
            logger.error(f"근무 시간 확인 중 오류: {e}")
            return True
    
    def should_send_email(self):
        """이메일을 보낼 시간인지 확인"""
        if not self.config or not self.config['enabled']:
            return False
        
        if not self.is_work_time():
            return False
        
        now = datetime.now()
        interval_minutes = self.config['schedule_settings']['interval_minutes']
        
        # 첫 번째 이메일이거나 지정된 간격이 지났으면 True
        if (self.last_email_time is None or 
            (now - self.last_email_time).total_seconds() >= interval_minutes * 60):
            return True
        
        return False
    
    def generate_email_content(self):
        """이메일 내용 생성 (Plain Text)"""
        try:
            template = self.config['message_template']
            self.email_count += 1
            
            # 시간대별 인사말
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                time_greeting = "좋은 아침입니다!"
            elif 12 <= current_hour < 18:
                time_greeting = "오후에도 화이팅!"
            elif 18 <= current_hour < 22:
                time_greeting = "저녁 시간이네요!"
            else:
                time_greeting = "늦은 시간까지 수고하셨습니다!"
            
            # 랜덤 운동 추천
            recommended_exercise = random.choice(template['exercises'])
            
            # 다음 알림 시간 계산
            interval = self.config['schedule_settings']['interval_minutes']
            next_time = datetime.now() + timedelta(minutes=interval)
            next_time_str = next_time.strftime("%H:%M")
            
            content = f"""{time_greeting}

{template['greeting']}

💡 **추천 운동**: {recommended_exercise}
🎯 **건강 팁**: {template['main_message']}

⏰ **다음 알림**: {next_time_str} (약 {interval}분 후)
📅 **오늘 알림 횟수**: {self.email_count}회

{template['closing']}

- VDT 증후군 관리 시스템 📧
"""
            
            return content
            
        except Exception as e:
            logger.error(f"이메일 내용 생성 실패: {e}")
            return "VDT 건강 관리 알림입니다. 정기적인 휴식을 취해주세요!"
    
    def generate_html_email_content(self, user_name="사용자"):
        """HTML 형식 이메일 내용 생성"""
        try:
            template = self.config['message_template']
            self.email_count += 1
            
            # 시간대별 인사말과 이모지
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                time_greeting = "좋은 아침입니다!"
                header_emoji = "🌅"
                header_text = "아침 건강 알리미!"
            elif 12 <= current_hour < 18:
                time_greeting = "오후에도 화이팅!"
                header_emoji = "⚡"
                header_text = "오후 활력 충전 시간!"
            elif 18 <= current_hour < 22:
                time_greeting = "저녁 시간이네요!"
                header_emoji = "🌆"
                header_text = "저녁 휴식 알리미!"
            else:
                time_greeting = "늦은 시간까지 수고하셨습니다!"
                header_emoji = "🌙"
                header_text = "야근족 건강 알리미!"
            
            # 랜덤 운동 추천 (3개)
            exercises = template['exercises'].copy()
            random.shuffle(exercises)
            selected_exercises = exercises[:3]
            
            # 다음 알림 시간 계산
            interval = self.config['schedule_settings']['interval_minutes']
            next_time = datetime.now() + timedelta(minutes=interval)
            next_time_str = next_time.strftime("%H:%M")
            
            # HTML 템플릿 생성
            html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>휴식 알리미</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Malgun Gothic', sans-serif;">

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; margin-top: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <thead>
            <tr>
                <td align="center" style="padding: 40px 0 30px 0; background-color: #4A90E2; color: #ffffff; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">{header_emoji} {header_text}</h1>
                </td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 40px 30px 40px 30px; color: #333333;">
                    <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 1.6;">
                        {time_greeting} {user_name}님! 👋<br>
                        열심히 일하는 것도 좋지만, {user_name}님의 목과 어깨 건강이 더 중요해요.<br>
                        지금 잠시 자리에서 일어나 뻐근한 몸을 풀어주는 건 어떨까요?
                    </p>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9f9f9; border-radius: 5px; padding: 20px;">
                        <tr>
                            <td>
                                <h3 style="margin: 0 0 15px 0; color: #4A90E2;">✨ 지금 추천하는 스트레칭</h3>
                                <ul style="margin: 0; padding-left: 20px; list-style-type: none;">"""
            
            # 선택된 운동들을 HTML에 추가
            for i, exercise in enumerate(selected_exercises, 1):
                html_content += f"""
                                    <li style="margin-bottom: 10px; padding-left: 10px;">✅ {exercise}</li>"""
            
            html_content += f"""
                                </ul>
                            </td>
                        </tr>
                    </table>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #e8f4fd; border-radius: 5px; padding: 15px; margin-top: 20px;">
                        <tr>
                            <td>
                                <p style="margin: 0; font-size: 14px; color: #2c3e50;">
                                    ⏰ <strong>다음 알림:</strong> {next_time_str} (약 {interval}분 후)<br>
                                    📊 <strong>오늘 알림:</strong> {self.email_count}회째
                                </p>
                            </td>
                        </tr>
                    </table>
                    <p style="margin: 30px 0 0 0; font-size: 16px; line-height: 1.6;">
                        짧은 휴식이 오늘 하루의 업무 효율을 더욱 높여줄 거예요!<br>
                        건강한 하루 보내세요! 💪
                    </p>
                </td>
            </tr>
        </tbody>
        <tfoot>
            <tr>
                <td align="center" style="padding: 20px; font-size: 12px; color: #999999; background-color: #f8f8f8; border-top: 1px solid #e9e9e9; border-radius: 0 0 8px 8px;">
                    VDT 증후군 관리 시스템 - 자동 휴식 알리미 📧
                </td>
            </tr>
        </tfoot>
    </table>
    <div style="height: 20px;"></div>
</body>
</html>"""
            
            return html_content
            
        except Exception as e:
            logger.error(f"HTML 이메일 내용 생성 실패: {e}")
            return """<!DOCTYPE html>
<html><body style="font-family: Arial, sans-serif; padding: 20px;">
<h2>🏃‍♂️ VDT 건강 관리 알림</h2>
<p>정기적인 휴식을 취해주세요!</p>
</body></html>"""
    
    def send_email(self, custom_message=None, custom_subject=None, user_name=None):
        """이메일 전송 (HTML 형식)"""
        try:
            # Gmail 설정 로드
            gmail_email = os.getenv("GMAIL_EMAIL", "")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            
            recipient_email = self.config['email_settings']['recipient_email']
            
            if not gmail_email or not gmail_password or not recipient_email:
                logger.warning("이메일 설정이 완료되지 않았습니다.")
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['email_settings']['sender_name']} <{gmail_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = custom_subject if custom_subject else self.config['email_settings']['subject_template']
            
            # 이메일 내용 생성
            if custom_message:
                # 커스텀 메시지가 HTML인지 확인
                if custom_message.strip().startswith('<!DOCTYPE html') or custom_message.strip().startswith('<html'):
                    html_body = custom_message
                    plain_body = "VDT 건강 관리 알림입니다. HTML을 지원하는 메일 클라이언트에서 확인해주세요."
                else:
                    plain_body = custom_message
                    html_body = f"<html><body style='font-family: Arial, sans-serif; padding: 20px;'><pre>{custom_message}</pre></body></html>"
            else:
                # 사용자 이름 추출 (설정에서 또는 이메일에서)
                if not user_name:
                    user_name = self.config['email_settings'].get('recipient_name', '') or recipient_email.split('@')[0] if '@' in recipient_email else "사용자"
                
                # HTML과 Plain Text 버전 생성
                html_body = self.generate_html_email_content(user_name)
                plain_body = self.generate_email_content()
            
            # Plain text와 HTML 부분 추가
            msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(gmail_email, gmail_password)
            server.send_message(msg)
            server.quit()
            
            # 커스텀 메시지가 아닌 경우만 카운트 및 시간 업데이트
            if not custom_message:
                self.last_email_time = datetime.now()
                logger.info(f"HTML 정기 이메일 발송 성공: {recipient_email}")
            else:
                logger.info(f"HTML 특별 이메일 발송 성공: {recipient_email}")
            
            return True
            
        except Exception as e:
            logger.error(f"이메일 발송 실패: {e}")
            return False
    
    def check_and_send(self):
        """스케줄 체크 및 이메일 전송"""
        if self.should_send_email():
            logger.info("이메일 전송 조건 충족, 이메일 발송 중...")
            success = self.send_email()
            if success:
                logger.info(f"자동 이메일 발송 완료 (총 {self.email_count}회)")
            else:
                logger.error("이메일 발송 실패")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        logger.info("=== VDT 이메일 스케줄러 시작 ===")
        
        # 매분마다 체크
        schedule.every().minute.do(self.check_and_send)
        
        # 메인 루프
        while self.running:
            schedule.run_pending()
            time.sleep(1)
        
        logger.info("=== VDT 이메일 스케줄러 종료 ===")
    
    def generate_welcome_message(self):
        """활성화 시작 알림 메일 메시지 생성 (HTML 형식)"""
        try:
            schedule_settings = self.config['schedule_settings']
            interval = schedule_settings['interval_minutes']
            work_start = schedule_settings['work_start_time']
            work_end = schedule_settings['work_end_time']
            work_days_only = schedule_settings['work_days_only']
            recipient_email = self.config['email_settings']['recipient_email']
            
            work_day_text = "평일에만" if work_days_only else "매일"
            user_name = self.config['email_settings'].get('recipient_name', '') or recipient_email.split('@')[0] if '@' in recipient_email else "사용자"
            
            html_message = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>휴식 알리미 활성화</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Malgun Gothic', sans-serif;">

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse; margin-top: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <thead>
            <tr>
                <td align="center" style="padding: 40px 0 30px 0; background-color: #10b981; color: #ffffff; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🚀 휴식 알리미 활성화 완료!</h1>
                </td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 40px 30px 40px 30px; color: #333333;">
                    <p style="margin: 0 0 20px 0; font-size: 18px; line-height: 1.6;">
                        안녕하세요, {user_name}님! 🎉<br>
                        <strong>VDT 증후군 관리 시스템</strong>의 휴식 알리미가 정상적으로 설정되었습니다.
                    </p>
                    
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f0f9ff; border-radius: 8px; padding: 25px; margin: 20px 0;">
                        <tr>
                            <td>
                                <h3 style="margin: 0 0 20px 0; color: #1e40af; font-size: 20px;">📋 알리미 설정 정보</h3>
                                <table border="0" cellpadding="8" cellspacing="0" width="100%" style="font-size: 16px;">
                                    <tr>
                                        <td style="color: #374151; font-weight: bold; width: 120px;">📧 수신자:</td>
                                        <td style="color: #1f2937;">{recipient_email}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #374151; font-weight: bold;">⏰ 발송 시간:</td>
                                        <td style="color: #1f2937;">{work_start} ~ {work_end}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #374151; font-weight: bold;">📅 발송 일정:</td>
                                        <td style="color: #1f2937;">{work_day_text}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #374151; font-weight: bold;">🔄 발송 간격:</td>
                                        <td style="color: #1f2937;">{interval}분마다</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #374151; font-weight: bold;">🎯 특별 기능:</td>
                                        <td style="color: #1f2937;">Streamlit 종료 후에도 자동 실행</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fef3c7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <tr>
                            <td align="center">
                                <h3 style="margin: 0 0 10px 0; color: #92400e;">💡 이제 무엇이 달라질까요?</h3>
                                <ul style="text-align: left; color: #78350f; font-size: 15px; margin: 10px 0; padding-left: 20px;">
                                    <li>설정된 시간 동안 정기적으로 운동 알림이 도착합니다</li>
                                    <li>시간대별 맞춤 인사말과 추천 운동을 받을 수 있습니다</li>
                                    <li>매번 다른 스트레칭 조합으로 지루하지 않게!</li>
                                    <li>Streamlit 앱을 종료해도 백그라운드에서 계속 실행됩니다</li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                    
                    <p style="margin: 30px 0 0 0; font-size: 18px; line-height: 1.6; text-align: center;">
                        건강한 개발 생활을 위한 첫 걸음을 내디뎠습니다! 🚶‍♂️<br>
                        <strong>{user_name}님의 건강한 하루를 응원합니다!</strong> 💪
                    </p>
                </td>
            </tr>
        </tbody>
        <tfoot>
            <tr>
                <td align="center" style="padding: 25px; font-size: 14px; color: #6b7280; background-color: #f9fafb; border-top: 1px solid #e5e7eb; border-radius: 0 0 8px 8px;">
                    <strong>VDT 증후군 관리 시스템</strong><br>
                    자동 휴식 알리미 📧 | 건강한 개발 문화를 만들어갑니다
                </td>
            </tr>
        </tfoot>
    </table>
    <div style="height: 20px;"></div>
</body>
</html>"""
            
            return html_message
            
        except Exception as e:
            logger.error(f"HTML 환영 메시지 생성 실패: {e}")
            return """<!DOCTYPE html>
<html><body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
<div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px;">
<h2 style="color: #10b981;">🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 활성화</h2>
<p>안녕하세요! VDT 증후군 관리 시스템입니다.</p>
<p>휴식 알리미가 정상적으로 활성화되었습니다.<br>정기적인 운동 알림을 보내드리겠습니다.</p>
<p><strong>건강한 개발 생활을 응원합니다! 💪</strong></p>
<hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
<p style="text-align: center; color: #666; font-size: 12px;">VDT 증후군 관리 시스템</p>
</div></body></html>"""

    def start(self):
        """스케줄러 백그라운드에서 시작"""
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return False
        
        if not self.config or not self.config['enabled']:
            logger.info("스케줄러가 비활성화되어 있습니다.")
            return False
        
        # 활성화 시작 알림 메일 발송
        if self.is_work_time():
            welcome_message = self.generate_welcome_message()
            welcome_subject = "🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 활성화 안내"
            self.send_email(custom_message=welcome_message, custom_subject=welcome_subject)
            logger.info("활성화 시작 알림 메일을 발송했습니다.")
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("백그라운드 이메일 스케줄러가 시작되었습니다.")
        return True
    
    def stop(self):
        """스케줄러 중지"""
        if not self.running:
            logger.warning("스케줄러가 실행 중이 아닙니다.")
            return False
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("백그라운드 이메일 스케줄러가 중지되었습니다.")
        return True
    
    def get_status(self):
        """스케줄러 상태 반환"""
        return {
            "running": self.running,
            "enabled": self.config['enabled'] if self.config else False,
            "last_email_time": self.last_email_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_email_time else None,
            "email_count": self.email_count,
            "config": self.config
        }

# 전역 스케줄러 인스턴스
_email_scheduler = None

def get_email_scheduler():
    """전역 이메일 스케줄러 인스턴스 반환"""
    global _email_scheduler
    if _email_scheduler is None:
        _email_scheduler = EmailScheduler()
    return _email_scheduler

def start_email_scheduler():
    """이메일 스케줄러 시작"""
    scheduler = get_email_scheduler()
    return scheduler.start()

def stop_email_scheduler():
    """이메일 스케줄러 중지"""
    scheduler = get_email_scheduler()
    return scheduler.stop()

def get_scheduler_status():
    """스케줄러 상태 조회"""
    scheduler = get_email_scheduler()
    return scheduler.get_status()

def update_scheduler_config(**kwargs):
    """스케줄러 설정 업데이트"""
    scheduler = get_email_scheduler()
    return scheduler.update_config(**kwargs)

def send_test_html_email():
    """HTML 이메일 테스트 전송"""
    scheduler = get_email_scheduler()
    if not scheduler.config or not scheduler.config['email_settings']['recipient_email']:
        logger.error("수신자 이메일이 설정되지 않았습니다.")
        return False
    
    logger.info("HTML 테스트 이메일을 발송합니다...")
    return scheduler.send_email(
        custom_subject="🧪 HTML 이메일 테스트 - VDT 건강 관리 시스템"
    )

def main():
    """메인 함수 - 독립 실행용"""
    scheduler = EmailScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'start':
            scheduler.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("사용자에 의해 중단됨")
                scheduler.stop()
        elif command == 'stop':
            scheduler.stop()
        elif command == 'status':
            status = scheduler.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False, default=str))
        elif command == 'test':
            print("HTML 테스트 이메일을 발송합니다...")
            success = send_test_html_email()
            if success:
                print("✅ HTML 테스트 이메일 발송 성공!")
            else:
                print("❌ HTML 테스트 이메일 발송 실패!")
    else:
        print("사용법: python email_scheduler.py [start|stop|status|test]")

if __name__ == "__main__":
    main()