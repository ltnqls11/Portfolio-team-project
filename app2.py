# app_sb_sr.py

import streamlit as st
import json
from datetime import datetime, timedelta
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 서브 페이지 파일들을 임포트합니다.
from exercise_manager6 import show_integrated_dashboard
from chatbot import show_chatbot_page

# 페이지 설정
st.set_page_config(
    page_title="개발자 헬스케어 - VDT 증후군 관리",
    page_icon="💻",
    layout="wide"
)

# .env 파일에서 환경변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API 설정 (실제 키는 환경변수에 저장 권장)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    pass

# --- Google Sheets 설정 (사용자 정보에 맞게 수정하세요) ---
GOOGLE_SHEET_CREDENTIALS = "credentials.json"
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0")
SHEET_NAME = "Sheet1"

GOOGLE_SHEETS_ENABLED = False
worksheet = None
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_SHEET_CREDENTIALS,
        scopes=scope
    )
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_url(GOOGLE_SHEET_URL).worksheet(SHEET_NAME)
    GOOGLE_SHEETS_ENABLED = True
    st.success("Google Sheets와 성공적으로 연결되었습니다.")
except Exception as e:
    st.error(f"Google Sheets 연결 오류: {e}. Google Sheets 기능을 비활성화합니다.")
    GOOGLE_SHEETS_ENABLED = False

# 세션 상태 초기화
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'selected_conditions' not in st.session_state:
    st.session_state.selected_conditions = []
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False
if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = "홈"

def calculate_rest_time(work_intensity):
    """Murrel의 공식을 적용한 휴식시간 계산"""
    intensity_map = {
        "가벼움": 30,
        "보통": 25,
        "높음": 20,
        "매우 높음": 15
    }
    return intensity_map.get(work_intensity, 25)

def show_symptom_selection():
    st.header("1. VDT 증후군 증상 선택")
    st.markdown("현재 겪고 있는 증상에 해당하는 항목을 모두 선택해주세요.")
    
    symptoms = {
        "눈의 피로": "눈의 건조함, 뻑뻑함, 시력 저하, 충혈 등",
        "거북목 증후군": "목 통증, 어깨 결림, 두통, 팔 저림 등",
        "손목터널 증후군": "손목 통증, 손가락 저림, 손 근력 약화 등",
        "허리디스크": "허리 통증, 다리 저림, 감각 이상 등",
        "근막통 증후군": "목, 어깨, 등 근육의 뭉침과 통증",
        "두통": "긴장성 두통, 편두통 등",
        "소화 불량": "장시간 앉아있어 발생하는 소화 기능 저하",
        "수면 장애": "불면증, 숙면 부족 등"
    }

    selected_conditions = st.multiselect(
        "증상을 선택해주세요:",
        list(symptoms.keys()),
        default=st.session_state.selected_conditions
    )
    st.session_state.selected_conditions = selected_conditions
    
    st.write("---")
    
    if st.button("다음"):
        st.session_state.menu_selection = "개인정보 입력"
        st.experimental_rerun()

def show_user_info_input():
    st.header("2. 개인정보 입력")
    st.markdown("건강 관리를 위한 개인정보를 입력해주세요. 이 정보는 개인의 증상과 생활 습관에 맞는 맞춤형 해결책을 제공하는 데 사용됩니다.")
    
    with st.form("user_info_form"):
        name = st.text_input("이름", st.session_state.user_data.get("name", ""))
        age = st.number_input("나이", min_value=1, max_value=120, value=st.session_state.user_data.get("age", 25))
        occupation = st.text_input("직업", st.session_state.user_data.get("occupation", "개발자"))
        daily_hours = st.number_input("하루 평균 컴퓨터 사용 시간 (시간)", min_value=1, max_value=24, value=st.session_state.user_data.get("daily_hours", 8))
        work_intensity = st.selectbox(
            "업무 강도",
            ["가벼움", "보통", "높음", "매우 높음"],
            index=["가벼움", "보통", "높음", "매우 높음"].index(st.session_state.user_data.get("work_intensity", "보통"))
        )
        
        submitted = st.form_submit_button("저장하고 다음")
        
        if submitted:
            st.session_state.user_data["name"] = name
            st.session_state.user_data["age"] = age
            st.session_state.user_data["occupation"] = occupation
            st.session_state.user_data["daily_hours"] = daily_hours
            st.session_state.user_data["work_intensity"] = work_intensity
            st.success("개인정보가 저장되었습니다!")
            st.session_state.menu_selection = "작업환경 평가"
            st.experimental_rerun()
            
def show_workspace_assessment():
    st.header("3. 작업환경 자가 평가")
    st.markdown("자신의 작업 환경이 VDT 증후군에 미치는 영향을 평가해 보세요.")
    
    questions = [
        "모니터 화면이 눈높이에 맞춰져 있나요?",
        "키보드와 마우스가 팔꿈치보다 아래에 있나요?",
        "등받이가 있는 의자에 등을 기대고 앉나요?",
        "발바닥 전체가 바닥에 닿거나 발받침대를 사용하나요?",
        "작업 시 1시간마다 5-10분 휴식을 취하나요?"
    ]
    
    answers = {}
    with st.form("assessment_form"):
        for i, q in enumerate(questions):
            answers[q] = st.radio(q, ["예", "아니오"], key=f"q{i}")
            
        submitted = st.form_submit_button("제출")
        
        if submitted:
            score = list(answers.values()).count("예")
            st.session_state.user_data["assessment_score"] = score
            st.session_state.assessment_complete = True
            st.success(f"평가 완료! 당신의 점수는 {score}점입니다.")
            if score < 3:
                st.warning("작업 환경 개선이 필요합니다. 전문가 추천을 참고하세요.")
            
            st.session_state.menu_selection = "운동 추천"
            st.experimental_rerun()

def show_exercise_recommendation():
    st.header("4. 맞춤형 운동 추천")
    st.markdown("당신의 증상과 작업 환경에 맞는 운동을 추천해 드립니다.")
    
    if 'selected_conditions' not in st.session_state or not st.session_state.selected_conditions:
        st.info("먼저 '증상 선택' 메뉴에서 증상을 선택해주세요.")
    else:
        st.markdown(f"**선택한 증상:** {', '.join(st.session_state.selected_conditions)}")
        
        # 임시 데이터로 대체
        VDT_SYMPTOMS = {
            "거북목 증후군": {
                "운동_추천": {
                    "예방 (자세교정)": [
                        {"name": "목 스트레칭", "purpose": "목 근육 이완 및 자세 교정", "method": "고개를 천천히 좌우로 돌리고, 앞뒤로 숙이기", "reps": "각 방향 10초씩 3회", "caution": "급격한 움직임 금지"}
                    ]
                }
            },
            "손목터널 증후군": {
                "운동_추천": {
                    "예방 (자세교정)": [
                        {"name": "손목 스트레칭", "purpose": "손목 긴장 완화 및 유연성 향상", "method": "손을 앞으로 뻗고 손목을 위아래로 꺾기", "reps": "각 방향 10초씩 3회", "caution": "무리하게 꺾지 않기"}
                    ]
                }
            }
        }
        
        for condition in st.session_state.selected_conditions:
            if condition in VDT_SYMPTOMS:
                st.subheader(f"✅ {condition} 운동")
                st.markdown(f"**{VDT_SYMPTOMS[condition]['운동_추천']['예방 (자세교정)'][0]['name']}**")
                st.markdown(f"**목적:** {VDT_SYMPTOMS[condition]['운동_추천']['예방 (자세교정)'][0]['purpose']}")
                st.markdown(f"**방법:** {VDT_SYMPTOMS[condition]['운동_추천']['예방 (자세교정)'][0]['method']}")
                st.markdown(f"**반복:** {VDT_SYMPTOMS[condition]['운동_추천']['예방 (자세교정)'][0]['reps']}")
                st.markdown(f"**주의:** {VDT_SYMPTOMS[condition]['운동_추천']['예방 (자세교정)'][0]['caution']}")
                st.markdown("---")


def show_rest_reminder_setting():
    st.header("5. 휴식 알리미 설정")
    st.markdown("업무 중 규칙적인 휴식을 위한 알리미를 설정해 보세요.")
    
    work_intensity = st.session_state.user_data.get("work_intensity", "보통")
    recommended_interval = calculate_rest_time(work_intensity)
    st.info(f"선택한 업무 강도({work_intensity})에 따라 **{recommended_interval}분**마다 휴식을 권장합니다.")
    
    rest_interval = st.number_input(
        f"휴식 알림 간격 (분):",
        min_value=1,
        max_value=120,
        value=recommended_interval
    )
    
    col1, col2 = st.columns(2)
    with col1:
        work_start = st.time_input("업무 시작 시간", value=datetime.strptime("09:00", "%H:%M").time())
    with col2:
        work_end = st.time_input("업무 종료 시간", value=datetime.strptime("18:00", "%H:%M").time())
        
    email_address = st.text_input("알림 받을 이메일 주소 (선택)")
    slack_webhook = st.text_input("슬랙 웹훅 URL (선택)")
    
    if st.button("알리미 설정 저장"):
        notification_config = {
            "email": email_address if email_address else None,
            "slack_webhook": slack_webhook if slack_webhook else None,
            "work_start": work_start.strftime("%H:%M"),
            "work_end": work_end.strftime("%H:%M"),
            "interval": rest_interval
        }
        
        try:
            with open("notification_config.json", "w", encoding="utf-8") as f:
                json.dump(notification_config, f, ensure_ascii=False, indent=2, default=str)
            
            st.success(f"알리미가 설정되었습니다! {rest_interval}분마다 휴식 알림을 받게 됩니다.")
            
            st.info("""
            **알리미 실행 방법:**
            1. 터미널에서 `python notification_scheduler.py` 실행
            2. 또는 백그라운드에서 실행: `python notification_scheduler.py &`
            """)
        except Exception as e:
            st.error(f"설정 저장 중 오류가 발생했습니다: {str(e)}")

def show_home():
    st.header("💻 개발자를 위한 VDT 증후군 관리 시스템")
    st.markdown("""
    **VDT 증후군**이란, 컴퓨터와 같은 영상 표시 단말기(Visual Display Terminal)를 장시간 사용하면서 발생하는 신체적, 정신적 이상 증상을 의미합니다.
    이 시스템은 개발자들이 흔히 겪는 VDT 증후군을 예방하고 관리하기 위해 맞춤형 기능을 제공합니다.
    """)
    st.markdown("---")
    st.markdown("""
    ### 주요 기능
    1.  **통합 대시보드:** 증상, 운동, 통증 기록을 한눈에 관리합니다.
    2.  **AI 챗봇:** VDT 증후군 관련 궁금증을 AI와 대화하며 해소합니다.
    3.  **휴식 알리미 설정:** 규칙적인 휴식을 위한 알림을 설정합니다.
    4.  **개인정보 및 환경 평가:** 맞춤형 조언을 제공합니다.
    """)

# 메인 함수
def main():
    st.title("💻 개발자를 위한 VDT 증후군 관리 시스템")
    st.markdown("---")

    options = ["홈", "증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정", "AI 챗봇", "통합 대시보드"]
    
    current_index = 0
    try:
        current_index = options.index(st.session_state.menu_selection)
    except ValueError:
        current_index = 0
        st.session_state.menu_selection = options[0]

    menu = st.sidebar.selectbox(
        "메뉴 선택",
        options,
        index=current_index
    )

    if menu != st.session_state.menu_selection:
        st.session_state.menu_selection = menu
        st.experimental_rerun()

    # 메뉴 선택에 따른 페이지 라우팅
    if menu == "홈":
        show_home()
    elif menu == "증상 선택":
        show_symptom_selection()
    elif menu == "개인정보 입력":
        show_user_info_input()
    elif menu == "작업환경 평가":
        show_workspace_assessment()
    elif menu == "운동 추천":
        show_exercise_recommendation()
    elif menu == "휴식 알리미 설정":
        show_rest_reminder_setting()
    elif menu == "AI 챗봇":
        show_chatbot_page()
    elif menu == "통합 대시보드":
        st.write("Google Sheets와 연동된 대시보드를 표시합니다.")
        if GOOGLE_SHEETS_ENABLED:
            show_integrated_dashboard(worksheet)
        else:
            st.warning("Google Sheets 연결이 비활성화되어 대시보드를 표시할 수 없습니다.")

if __name__ == "__main__":
    main()
