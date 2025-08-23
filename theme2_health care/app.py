import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# YouTube 데이터 조회를 위한 라이브러리 추가
try:
    from youtube_collector import search_youtube_videos, search_videos_by_condition, collect_all_vdt_videos
    from database import get_videos_for_condition, get_recommended_videos_for_user, get_database_analytics
    from video_analyzer import analyze_single_video
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError as e:
    YOUTUBE_SEARCH_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="개발자 헬스케어 - VDT 증후군 관리",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

# Google Sheets 설정
GOOGLE_SHEETS_CREDENTIALS = "credentials.json"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
CREDENTIALS_EXISTS = os.path.exists(GOOGLE_SHEETS_CREDENTIALS)

# 세션 상태 초기화
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'selected_conditions' not in st.session_state:
    st.session_state.selected_conditions = []
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'steps_completed' not in st.session_state:
    st.session_state.steps_completed = [False, False, False, False, False]
if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = "홈"
if 'next_menu' not in st.session_state:
    st.session_state.next_menu = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = f'user_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

def init_google_sheets():
    try:
        if not GSPREAD_AVAILABLE or not CREDENTIALS_EXISTS:
            return None
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

def save_to_sheets(data, sheet_name="vdt_data"):
    try:
        if not GSPREAD_AVAILABLE or not SPREADSHEET_ID or not CREDENTIALS_EXISTS:
            return False
        client = init_google_sheets()
        if not client:
            return False
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            headers = ["timestamp", "user_id", "data_type", "conditions", "user_age", "user_gender", "work_hours", "exercise_purpose", "ai_recommendation", "pain_scores", "work_intensity", "env_score"]
            worksheet.append_row(headers)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_id = st.session_state.get('user_id', f'user_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        user_data = data.get('user_data', {})
        conditions_str = ', '.join(data.get('conditions', []))
        ai_rec = data.get('ai_recommendation', '')
        if len(ai_rec) > 500:
            ai_rec = ai_rec[:500] + "..."
        row_data = [timestamp, user_id, "ai_recommendation", conditions_str, str(user_data.get('age', '')), str(user_data.get('gender', '')), str(user_data.get('daily_work_hours', '')), str(data.get('exercise_purpose', '')), ai_rec, json.dumps(user_data.get('pain_scores', {}), ensure_ascii=False), str(user_data.get('work_intensity', '')), str(user_data.get('env_score', ''))]
        worksheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"Google Sheets 저장 실패: {str(e)}")
        return False

def get_enhanced_ai_recommendation(user_data, conditions, pain_scores, exercise_schedule=None):
    try:
        if not GEMINI_API_KEY or not GEMINI_AVAILABLE:
            return "⚠️ 제미나이 API가 설정되지 않았습니다."
        model = genai.GenerativeModel('gemini-1.5-flash')
        schedule_info = ""
        if exercise_schedule:
            available_days = exercise_schedule.get('available_days', [])
            daily_minutes = exercise_schedule.get('daily_minutes', 30)
            preferred_time = exercise_schedule.get('preferred_time', '언제든지')
            difficulty_level = exercise_schedule.get('difficulty_level', '초급자')
            schedule_info = f"""**운동 가능 시간 정보:**\n- 운동 가능 요일: {', '.join(available_days)}\n- 하루 운동 시간: {daily_minutes}분\n- 선호 시간대: {preferred_time}\n- 운동 수준: {difficulty_level}"""
        prompt = f"""당신은 VDT 증후군 전문 재활의학과 의사입니다. **환자 정보:** 나이: {user_data.get('age', 'N/A')}세, 성별: {user_data.get('gender', 'N/A')}, 개발 경력: {user_data.get('work_experience', 'N/A')}년, 일일 작업시간: {user_data.get('daily_work_hours', 'N/A')}시간, 운동 습관: {user_data.get('exercise_habit', 'N/A')}, 작업 강도: {user_data.get('work_intensity', 'N/A')}, 작업환경 점수: {user_data.get('env_score', 'N/A')}/100점 **현재 증상:** {', '.join([f"• {condition}: {pain_scores.get(condition, 0)}/10점" for condition in conditions])} {schedule_info} 다음 형식으로 운동 처방을 작성해주세요: ## 🎯 VDT 증후군 맞춤 운동 프로그램 ### 1. 증상별 맞춤 운동법 ### 2. 운동 순서와 시간 배분 ### 3. 주의사항 및 금기사항 ### 4. 일주일 운동 계획표 ### 5. 개선 예상 기간"""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 추천 생성 중 오류가 발생했습니다: {str(e)}"

def calculate_rest_time(work_intensity):
    intensity_map = {"가벼움": 30, "보통": 25, "높음": 20, "매우 높음": 15}
    return intensity_map.get(work_intensity, 25)

def get_exercises_for_condition(condition, purpose):
    exercises_db = {
        "거북목": {
            "예방 (자세교정)": [{"name": "목 스트레칭", "purpose": "목 근육 이완 및 자세 교정", "method": "고개를 천천히 좌우로 돌리고, 앞뒤로 숙이기", "reps": "각 방향 10초씩 3회", "caution": "급격한 움직임 금지"}],
            "운동 (근력 및 체력 증진)": [{"name": "목 근력 강화", "purpose": "목 주변 근육 강화", "method": "손으로 이마를 누르며 목으로 저항하기", "reps": "10초씩 5회", "caution": "과도한 힘 사용 금지"}],
            "재활 (통증감소)": [{"name": "온찜질 후 스트레칭", "purpose": "통증 완화 및 혈액순환 개선", "method": "따뜻한 수건으로 목을 찜질 후 가벼운 스트레칭", "reps": "15분 찜질 후 스트레칭", "caution": "통증이 심할 때는 중단"}]
        }
    }
    return exercises_db.get(condition, {}).get(purpose, [])

def get_enhanced_exercise_videos(condition, purpose="예방", limit=10):
    try:
        if YOUTUBE_SEARCH_AVAILABLE:
            db_videos = get_videos_for_condition(condition, purpose, limit)
            if db_videos and len(db_videos) >= 3:
                return db_videos[:limit]
    except:
        pass
    videos_db = {
        "거북목": [{"title": "거북목 교정 운동 5분", "url": "https://youtu.be/8hlp5u8m_Ao", "channel_name": "핏블리", "duration": "5:23", "view_count": "1.2M"}],
        "라운드숄더": [{"title": "라운드숄더 교정 운동", "url": "https://youtu.be/oLwTC-lAJws", "channel_name": "핏블리", "duration": "8:30", "view_count": "2.1M"}],
        "허리디스크": [{"title": "허리 강화 운동", "url": "https://youtu.be/4BOTvaRaDjI", "channel_name": "핏블리", "duration": "9:42", "view_count": "1.8M"}],
        "손목터널증후군": [{"title": "손목터널증후군 스트레칭", "url": "https://youtu.be/EiRC80FJbHU", "channel_name": "물리치료", "duration": "6:33", "view_count": "445K"}]
    }
    return videos_db.get(condition, [])

def format_duration(seconds):
    if isinstance(seconds, str):
        return seconds
    if seconds == 0:
        return "정보없음"
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

def format_view_count(count):
    if isinstance(count, str):
        return count
    if count >= 1000000:
        return f"{count/1000000:.1f}M"
    elif count >= 1000:
        return f"{count/1000:.1f}K"
    else:
        return str(count)

def show_posture_guide():
    col1, col2 = st.columns(2)
    with col1:
        st.write("**모니터 위치**\n- 눈높이와 같거나 약간 아래\n- 팔 길이만큼 거리 유지 (50-70cm)")
    with col2:
        st.write("**키보드 & 마우스**\n- 팔꿈치 각도 90도\n- 손목은 일직선 유지")

def calculate_environment_score(desk_height, chair_support, chair_sitting_style, monitor_height, keyboard_type, mouse_type, monitor_distance_level):
    score = 0
    if desk_height == "적절함":
        score += 20
    if chair_support == "매우 좋음":
        score += 20
    elif chair_support == "좋음":
        score += 15
    elif chair_support == "보통":
        score += 8
    if chair_sitting_style == "등을 완전히 붙이고 앉음":
        score += 10
    if monitor_height == "눈높이와 같음":
        score += 20
    elif monitor_height == "눈높이보다 낮음":
        score += 10
    if "인체공학" in keyboard_type:
        score += 15
    elif keyboard_type == "기계식":
        score += 10
    if mouse_type == "인체공학적":
        score += 15
    if monitor_distance_level.startswith("적당하다"):
        score += 10
    return score

def send_test_email(email, password):
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "VDT 관리 시스템 - 테스트 메일"
        body = "휴식 알리미 테스트 메일입니다."
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"이메일 발송 실패: {str(e)}")
        return False

def send_test_slack(webhook_url):
    try:
        payload = {"text": "🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 테스트입니다!"}
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Slack 메시지 발송 실패: {str(e)}")
        return False

def show_home():
    st.header("🏠 개발자를 위한 VDT 증후군 관리 시스템 v2.0")
    col1, col2, col3 = st.columns(3)
    with col1:
        if YOUTUBE_SEARCH_AVAILABLE:
            st.success("✅ YouTube 검색 활성화")
        else:
            st.error("❌ YouTube 검색 비활성화")
    with col2:
        if GEMINI_API_KEY and GEMINI_AVAILABLE:
            st.success("✅ AI 추천 활성화")
        else:
            st.error("❌ AI 추천 비활성화")
    with col3:
        if SPREADSHEET_ID and CREDENTIALS_EXISTS:
            st.success("✅ 데이터 저장 활성화")
        else:
            st.warning("⚠️ 데이터 저장 비활성화")
    st.info("👈 **왼쪽 메뉴에서 '증상 선택'부터 시작해주세요!**")

def show_condition_selection():
    st.header("🔍 증상 선택 및 통증 평가")
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed)
    st.caption(f"진행률: {completed_steps}/{len(steps)} 단계")
    st.progress(completed_steps / len(steps))
    
    conditions = {"거북목": "목이 앞으로 나오고 목, 어깨 통증이 있음", "라운드숄더": "어깨가 앞으로 말리고 상체가 구부정함", "허리디스크": "허리 통증, 다리 저림 등의 증상", "손목터널증후군": "손목, 손가락 저림 및 통증"}
    selected = []
    col1, col2 = st.columns(2)
    condition_items = list(conditions.items())
    for i, (condition, description) in enumerate(condition_items):
        with col1 if i % 2 == 0 else col2:
            if st.checkbox(f"**{condition}**", key=condition):
                selected.append(condition)
                st.caption(f"↳ {description}")
    
    if selected:
        st.session_state.selected_conditions = selected
        st.success(f"✅ **선택된 증상**: {', '.join(selected)}")
        if st.button("✅ 저장하고 다음 단계로", key="condition_next", type="primary"):
            st.session_state.steps_completed[0] = True
            st.session_state.current_step = 1
            st.session_state.next_menu = "개인정보 입력"
            st.success("✅ 증상 선택이 완료되었습니다!")
            st.rerun()
    else:
        st.warning("⚠️ 최소 하나의 증상을 선택해주세요.")

def show_personal_info():
    st.header("👤 개인정보 입력")
    if not st.session_state.selected_conditions:
        st.warning("⚠️ 먼저 증상을 선택해주세요.")
        return
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed)
    st.caption(f"진행률: {completed_steps}/{len(steps)} 단계")
    st.progress(completed_steps / len(steps))
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("나이", min_value=20, max_value=70, value=30)
        gender = st.selectbox("성별", ["남성", "여성"])
        work_experience = st.number_input("개발 경력 (년)", min_value=0, max_value=30, value=3)
        daily_work_hours = st.slider("일일 컴퓨터 작업시간", 4, 16, 8)
        work_intensity = st.selectbox("작업 강도", ["가벼움", "보통", "높음", "매우 높음"])
    with col2:
        exercise_habit = st.selectbox("운동 습관", ["전혀 안함", "주 1-2회", "주 3-4회", "주 5회 이상"])
        smoking = st.selectbox("흡연", ["비흡연", "과거 흡연", "현재 흡연"])
        drinking = st.selectbox("음주", ["안함", "주 1-2회", "주 3-4회", "거의 매일"])
        sleep_hours = st.slider("평균 수면시간", 4, 12, 7)
    
    personal_data = {'age': age, 'gender': gender, 'work_experience': work_experience, 'exercise_habit': exercise_habit, 'smoking': smoking, 'drinking': drinking, 'sleep_hours': sleep_hours, 'daily_work_hours': daily_work_hours, 'work_intensity': work_intensity}
    st.session_state.user_data.update(personal_data)
    
    if st.button("✅ 저장하고 다음 단계로", key="personal_next", type="primary"):
        st.session_state.steps_completed[1] = True
        st.session_state.current_step = 2
        st.session_state.next_menu = "작업환경 평가"
        st.success("✅ 개인정보가 저장되었습니다!")
        st.rerun()

def show_work_environment():
    st.header("🖥️ 작업환경 평가")
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed)
    st.caption(f"진행률: {completed_steps}/{len(steps)} 단계")
    st.progress(completed_steps / len(steps))
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🪑 책상 및 의자")
        desk_height = st.selectbox("책상 높이", ["너무 높음", "적절함", "너무 낮음"])
        chair_support = st.selectbox("의자 허리 지지", ["매우 좋음", "좋음", "보통", "나쁨"])
        chair_sitting_style = st.selectbox("평소 앉는 방식", ["등을 완전히 붙이고 앉음", "등받이에 기대지 않음", "한쪽으로 기울어져 앉음", "다리를 꼬고 앉음"])
        monitor_distance_level = st.selectbox("모니터 거리", ["가깝다 (50cm 이내)", "적당하다 (50-70cm)", "멀다 (70cm 이상)"])
        monitor_height = st.selectbox("모니터 높이", ["눈높이보다 높음", "눈높이와 같음", "눈높이보다 낮음"])
    with col2:
        st.subheader("⌨️ 키보드 및 마우스")
        keyboard_type = st.selectbox("키보드 타입", ["일반", "인체공학적", "기계식", "노트북 내장"])
        mouse_type = st.selectbox("마우스 타입", ["일반", "인체공학적", "트랙볼", "터치패드"])
        wrist_support = st.selectbox("손목 받침대", ["있음", "없음"])
        lighting = st.selectbox("조명 상태", ["너무 밝음", "적절함", "너무 어두움", "반사광 있음"])
    
    env_score = calculate_environment_score(desk_height, chair_support, chair_sitting_style, monitor_height, keyboard_type, mouse_type, monitor_distance_level)
    additional_score = 0
    if lighting == "적절함":
        additional_score += 5
    if wrist_support == "있음":
        additional_score += 5
    total_env_score = min(env_score + additional_score, 100)
    
    st.subheader("📊 작업환경 평가 결과")
    st.metric("종합 점수", f"{total_env_score}/100점")
    
    env_data = {'desk_height': desk_height, 'chair_support': chair_support, 'chair_sitting_style': chair_sitting_style, 'monitor_distance': monitor_distance_level, 'monitor_height': monitor_height, 'keyboard_type': keyboard_type, 'mouse_type': mouse_type, 'wrist_support': wrist_support, 'lighting': lighting, 'env_score': total_env_score}
    st.session_state.user_data.update(env_data)
    
    if st.button("✅ 저장하고 다음 단계로", key="env_next", type="primary"):
        st.session_state.steps_completed[2] = True
        st.session_state.current_step = 3
        st.session_state.next_menu = "운동 추천"
        st.success("✅ 작업환경 평가가 저장되었습니다!")
        st.rerun()

def show_exercise_recommendation():
    st.header("🏃‍♂️ 맞춤형 운동 추천")
    if not st.session_state.selected_conditions:
        st.warning("⚠️ 먼저 증상을 선택해주세요.")
        return
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed)
    st.caption(f"진행률: {completed_steps}/{len(steps)} 단계")
    st.progress(completed_steps / len(steps))
    
    exercise_purpose = st.selectbox("주요 목적을 선택하세요", ["예방 (자세교정)", "운동 (근력 및 체력 증진)", "재활 (통증감소)"])
    rest_time = calculate_rest_time(st.session_state.user_data.get('work_intensity', '보통'))
    st.info(f"⏰ **권장 휴식시간**: {rest_time}분마다")
    
    tab1, tab2, tab3 = st.tabs(["📋 기본 운동 추천", "📹 추천 영상", "🤖 AI 맞춤 운동 추천"])
    
    with tab1:
        for condition in st.session_state.selected_conditions:
            st.write(f"### {condition} 운동법")
            exercises = get_exercises_for_condition(condition, exercise_purpose)
            if exercises:
                for i, exercise in enumerate(exercises, 1):
                    with st.expander(f"{i}. {exercise['name']}"):
                        st.write(f"**운동 방법**: {exercise['method']}")
                        st.write(f"**운동 횟수**: {exercise['reps']}")
                        st.write(f"**주의사항**: {exercise['caution']}")
    
    with tab2:
        for condition in st.session_state.selected_conditions:
            st.write(f"### {condition} 관련 영상")
            videos = get_enhanced_exercise_videos(condition, exercise_purpose, limit=3)
            for i, video in enumerate(videos, 1):
                st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                duration = video.get('duration', video.get('duration_seconds', '정보없음'))
                if isinstance(duration, int):
                    duration = format_duration(duration)
                channel = video.get('channel_name', '알 수 없음')
                st.caption(f"📺 {channel} | ⏱️ {duration}")
    
    with tab3:
        st.subheader("🤖 AI 맞춤형 운동 추천")
        if st.button("🚀 AI 운동 추천 받기", key="ai_recommendation", type="primary"):
            if not st.session_state.user_data:
                st.warning("⚠️ 먼저 개인정보를 입력해주세요.")
                return
            with st.spinner("🤖 AI가 맞춤형 운동을 분석하고 있습니다..."):
                pain_scores = st.session_state.user_data.get('pain_scores', {})
                ai_recommendation = get_enhanced_ai_recommendation(st.session_state.user_data, st.session_state.selected_conditions, pain_scores)
            st.subheader("🎯 AI 맞춤 운동 계획")
            st.markdown(ai_recommendation)
    
    if st.button("✅ 운동 추천 완료 - 다음 단계로", key="exercise_next", type="primary"):
        st.session_state.steps_completed[3] = True
        st.session_state.current_step = 4
        st.session_state.next_menu = "휴식 알리미 설정"
        st.success("✅ 운동 추천이 완료되었습니다!")
        st.rerun()

def show_notification_setup():
    st.header("🔔 휴식 알리미 설정")
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed)
    st.caption(f"진행률: {completed_steps}/{len(steps)} 단계")
    st.progress(completed_steps / len(steps))
    
    notification_type = st.selectbox("알림 방식", ["이메일 (Gmail)", "Slack", "둘 다"])
    email = ""
    email_password = ""
    slack_webhook = ""
    
    col1, col2 = st.columns(2)
    with col1:
        if notification_type in ["이메일 (Gmail)", "둘 다"]:
            st.subheader("📧 Gmail 설정")
            email = st.text_input("Gmail 주소", placeholder="example@gmail.com")
            email_password = st.text_input("앱 비밀번호", type="password")
    with col2:
        if notification_type in ["Slack", "둘 다"]:
            st.subheader("💬 Slack 설정")
            slack_webhook = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")
    
    work_start = st.time_input("업무 시작 시간", value=datetime.strptime("09:00", "%H:%M").time())
    work_end = st.time_input("업무 종료 시간", value=datetime.strptime("18:00", "%H:%M").time())
    work_intensity = st.session_state.user_data.get('work_intensity', '보통')
    rest_interval = calculate_rest_time(work_intensity)
    custom_interval = st.number_input("휴식 간격 조정 (분)", min_value=15, max_value=120, value=rest_interval, step=5)
    
    if st.button("🚀 알리미 활성화", type="primary"):
        notification_config = {"type": notification_type, "email": email if email else None, "email_password": email_password if email_password else None, "slack_webhook": slack_webhook if slack_webhook else None, "work_start": work_start.strftime("%H:%M"), "work_end": work_end.strftime("%H:%M"), "interval": custom_interval, "created_at": datetime.now().isoformat()}
        try:
            with open("notification_config.json", "w", encoding="utf-8") as f:
                json.dump(notification_config, f, ensure_ascii=False, indent=2, default=str)
            st.success(f"✅ 알리미가 설정되었습니다!")
            st.session_state.steps_completed[4] = True
        except Exception as e:
            st.error(f"❌ 설정 저장 중 오류가 발생했습니다: {str(e)}")
    
    if st.session_state.steps_completed[4]:
        st.success("🎉 **모든 설정이 완료되었습니다!**")
        st.balloons()

def main():
    st.title("💻 개발자를 위한 VDT 증후군 관리 시스템 v2.0")
    st.markdown("---")
    
    options = ["홈", "증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정","운동 관리"]
    
    if st.session_state.next_menu:
        st.session_state.menu_selection = st.session_state.next_menu
        st.session_state.next_menu = None
    
    try:
        current_index = options.index(st.session_state.menu_selection)
    except ValueError:
        current_index = 0
        st.session_state.menu_selection = options[0]
    
    menu = st.sidebar.selectbox("📋 메뉴 선택", options, index=current_index)
    
    if menu != st.session_state.menu_selection:
        st.session_state.menu_selection = menu
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 시스템 상태")
    
    if YOUTUBE_SEARCH_AVAILABLE:
        st.sidebar.success("✅ YouTube 검색 활성화")
    else:
        st.sidebar.error("❌ YouTube 검색 비활성화")
    
    if GEMINI_API_KEY and GEMINI_AVAILABLE:
        st.sidebar.success("✅ AI 추천 활성화")
    else:
        st.sidebar.error("❌ AI 추천 비활성화")
    
    if SPREADSHEET_ID and CREDENTIALS_EXISTS and GSPREAD_AVAILABLE:
        st.sidebar.success("✅ 데이터 저장 활성화")
    else:
        st.sidebar.warning("⚠️ 데이터 저장 비활성화")
    
    completed_steps = sum(st.session_state.steps_completed)
    progress_percentage = (completed_steps / len(st.session_state.steps_completed)) * 100
    st.sidebar.progress(progress_percentage / 100)
    st.sidebar.caption(f"{completed_steps}/5 단계 완료 ({progress_percentage:.0f}%)")
    
    if menu == "홈":
        show_home()
    elif menu == "증상 선택":
        show_condition_selection()
    elif menu == "개인정보 입력":
        show_personal_info()
    elif menu == "작업환경 평가":
        show_work_environment()
    elif menu == "운동 추천":
        show_exercise_recommendation()
    elif menu == "휴식 알리미 설정":
        show_notification_setup()
    elif menu == "운동 관리":
        # 지연 로딩으로 서브 모듈을 호출합니다.
        try:
            import importlib.util
            import pathlib
            module_path = pathlib.Path(__file__).with_name("exercise_manager6.py")
            spec = importlib.util.spec_from_file_location("exercise_manager6", str(module_path))
            em6 = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(em6)
            user_id = st.session_state.get('user_id', f'user_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            if hasattr(em6, "show_integrated_dashboard"):
                em6.show_integrated_dashboard(user_id)
            else:
                st.error("exercise_manager6.py에 'show_integrated_dashboard' 함수가 없습니다.")
        except Exception as e:
            st.error(f"운동 관리 모듈 로드 실패: {e}")

if __name__ == "__main__":
    main()
