# posture_tip_notifier.py

# 필요한 라이브러리를 불러옵니다.
import time
import json
import random
from datetime import datetime, time as dt_time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Supabase 라이브러리 추가
from supabase import create_client, Client

# --- Supabase 설정 (사용자 정보에 맞게 수정하세요) ---
# Supabase 프로젝트 URL과 API 키를 입력합니다.
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# --- Supabase 설정 끝 ---


# --- 기존 함수들 (변경 없이 유지) ---
# 이메일 알림을 보내는 함수
def send_email_notification(email, password, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "VDT 증후군 관리 - 건강 알림!"
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"이메일 발송 실패: {str(e)}")
        return False

# Slack 알림을 보내는 함수
def send_slack_notification(webhook_url, message):
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Slack 메시지 발송 실패: {str(e)}")
        return False
# --- 기존 함수들 끝 ---


# --- Supabase에서 데이터를 로드하는 새로운 함수들 ---
def load_config_from_supabase(user_id):
    """Supabase에서 사용자의 알림 설정을 불러옵니다."""
    try:
        # 'user_settings' 테이블에서 특정 사용자의 설정 불러오기
        response = supabase.table('user_settings').select('*').eq('user_id', user_id).execute()
        if response.data:
            return response.data[0] # 첫 번째 레코드를 반환
        else:
            print(f"오류: 사용자 ID '{user_id}'에 대한 설정 데이터를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"Supabase에서 설정 로드 중 오류 발생: {e}")
        return None

def load_user_conditions_from_supabase(user_id):
    """Supabase에서 사용자의 증상 목록을 불러옵니다."""
    try:
        # 'user_conditions' 테이블에서 특정 사용자의 증상 목록 불러오기
        # 이 테이블에는 user_id와 conditions 필드가 있다고 가정합니다.
        response = supabase.table('user_conditions').select('conditions').eq('user_id', user_id).execute()
        if response.data and 'conditions' in response.data[0]:
            return response.data[0]['conditions']
        else:
            print(f"오류: 사용자 ID '{user_id}'에 대한 증상 데이터를 찾을 수 없습니다.")
            return []
    except Exception as e:
        print(f"Supabase에서 증상 로드 중 오류 발생: {e}")
        return []
# --- Supabase 로드 함수들 끝 ---


# VDT 증후군별 올바른 자세 가이드 메시지 사전
POSTURE_TIPS = {
    "거북목": "🐢 모니터 상단이 눈높이와 같도록 조절하고, 턱을 가볍게 당겨 목이 앞으로 나오지 않게 해주세요. 수시로 먼 곳을 바라보며 시야를 넓혀주는 것도 좋습니다.",
    "라운드숄더": "🧘 가슴을 펴고 어깨를 뒤로 젖히는 스트레칭을 해주세요. 팔꿈치를 뒤로 당기는 동작은 굽은 어깨를 펴는 데 도움이 됩니다.",
    "허리디스크": "🪑 의자에 앉을 때는 허리를 등받이에 밀착시키고, 무릎은 엉덩이보다 살짝 높게 유지하는 것이 좋습니다. 1시간마다 일어나서 가볍게 걸어주세요.",
    "손목터널증후군": "✍️ 키보드와 마우스 사용 시 손목이 꺾이지 않도록 중립 위치를 유지하세요. 15-20분마다 손목을 돌리거나 털어주는 스트레칭을 해주세요."
}

# 일반 건강 팁 사전 (무작위로 선택하여 보낼 메시지)
HEALTH_TIPS = [
    "💧 충분한 수분을 섭취하세요. 물을 마시는 것은 신진대사를 돕고 피로를 줄이는 데 좋습니다.",
    "🍎 간식으로 건강한 과일이나 견과류를 선택하세요. 당분이 많은 간식은 오히려 피로를 유발할 수 있습니다.",
    "🎶 좋아하는 음악을 들으며 잠시 휴식을 취하세요. 스트레스 해소에 도움이 됩니다.",
    "🌬️ 주기적으로 창문을 열어 환기를 시켜주세요. 신선한 공기는 집중력 향상에 좋습니다."
]

# 메인 알림 스케줄러 함수
def start_unified_notifier():
    # 실제 앱에서는 로그인 후 얻은 user_id를 사용합니다.
    # 여기서는 예시를 위해 임의의 ID를 사용합니다.
    user_id = "your_authenticated_user_id" 
    
    config = load_config_from_supabase(user_id)
    conditions = load_user_conditions_from_supabase(user_id)

    if not config:
        return

    notification_type = config.get('type')
    email = config.get('email')
    password = config.get('email_password')
    slack_webhook = config.get('slack_webhook')

    print("통합 알리미가 시작되었습니다.")

    while True:
        now = datetime.now()
        current_time = now.time()
        
        # 알림 메시지 생성
        # 사용자가 증상을 선택했다면 해당 증상에 대한 자세 교정 팁을 포함
        posture_tips_message = ""
        if conditions:
            selected_tips = [POSTURE_TIPS.get(cond) for cond in conditions if cond in POSTURE_TIPS]
            if selected_tips:
                posture_tips_message = "바른 자세 가이드:\n" + "\n".join(selected_tips) + "\n\n"

        # 무작위로 선택된 일반 건강 팁을 추가
        random_tip = random.choice(HEALTH_TIPS)
        health_tip_message = f"오늘의 건강 팁: {random_tip}"
        
        # 최종 메시지 조합
        final_message = posture_tips_message + health_tip_message

        # --- 알림 발송 ---
        # 매일 오전 10시와 오후 3시에 알림을 보냅니다.
        if (current_time.hour == 10 or current_time.hour == 15) and current_time.minute == 0:
            if final_message.strip(): # 메시지가 비어있지 않은 경우에만 발송
                if notification_type in ["이메일 (Gmail)", "둘 다"] and email and password:
                    send_email_notification(email, password, final_message)
                if notification_type in ["Slack", "둘 다"] and slack_webhook:
                    send_slack_notification(slack_webhook, final_message)
                
                print(f"알림 발송 완료: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 중복 발송을 막기 위해 1분간 대기합니다.
            time.sleep(60)

        time.sleep(1)

if __name__ == "__main__":
    start_unified_notifier()
