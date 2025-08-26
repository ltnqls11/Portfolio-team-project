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

# 이메일 스케줄러 모듈 import
try:
    from email_scheduler import (
        get_email_scheduler, 
        start_email_scheduler, 
        stop_email_scheduler, 
        get_scheduler_status,
        update_scheduler_config
    )
    EMAIL_SCHEDULER_AVAILABLE = True
    print("OK: Email Scheduler module loaded")
except ImportError as e:
    EMAIL_SCHEDULER_AVAILABLE = False
    print(f"ERROR: Email Scheduler module load failed: {e}")

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
    import openai
    OPENAI_AVAILABLE = True
    print("OK: OpenAI module loaded")
except ImportError:
    OPENAI_AVAILABLE = False
    print("ERROR: OpenAI module load failed")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
    print("OK: GSpread module loaded")
except ImportError:
    GSPREAD_AVAILABLE = False
    print("ERROR: GSpread module load failed")

# 광고 모듈 import 추가
try:
    from ads import (
        show_healthcare_product_recommendation, 
        show_general_healthcare_products,
        show_personalized_product_recommendation,
        show_adsense_ads,
        show_hospital_recommendation
    )
    ADS_AVAILABLE = True
    print("OK: Ads module loaded")
except ImportError as e:
    ADS_AVAILABLE = False
    print(f"ERROR: Ads module load failed: {e}")

# 페이지 설정
st.set_page_config(
    page_title="직장인 근무 환경 개선을 위한 맞춤형 운동 관리 시스템",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전문적인 색상 팔레트 CSS
st.markdown("""
<style>
/* 깔끔하고 보기 좋은 컬러 팔레트 */
:root {
    --primary-blue: #3b82f6;
    --primary-blue-hover: #2563eb;
    --secondary-blue: #60a5fa;
    --accent-green: #10b981;
    --accent-green-hover: #059669;
    --accent-orange: #f59e0b;
    --accent-orange-hover: #d97706;
    --accent-red: #ef4444;
    --neutral-gray: #6b7280;
    --bg-light: #ffffff;
    --bg-gray: #f8fafc;
    --white: #ffffff;
    --text-dark: #1f2937;
    --text-light: #6b7280;
    --text-muted: #9ca3af;
}

/* 전체 앱 스타일 - 라이트 테마 */
.main .block-container {
    background-color: var(--bg-light);
    padding-top: 2rem;
    padding-bottom: 2rem;
    color: var(--text-dark);
}

/* 헤더 스타일 - 높은 가독성 */
.main h1 {
    color: var(--primary-blue);
    font-weight: 700;
    margin-bottom: 1.5rem;
    font-size: 2rem;
}

.main h2 {
    color: var(--text-dark);
    font-weight: 600;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.main h3 {
    color: var(--text-dark);
    font-weight: 600;
    margin-bottom: 0.75rem;
    font-size: 1.25rem;
}

/* 버튼 스타일 - 깔끔한 파란색 */
.stButton > button {
    background-color: var(--primary-blue);
    color: var(--white);
    border: none;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stButton > button:hover {
    background-color: var(--primary-blue-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 진행률 바 스타일 - 깔끔한 파란색 */
.stProgress > div > div > div > div {
    background-color: var(--primary-blue);
    border-radius: 4px;
}

/* 메시지 스타일 - 높은 가독성 */
.stSuccess {
    background-color: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--accent-green);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: var(--text-dark);
    font-weight: 500;
}

.stError {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--accent-red);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: var(--text-dark);
    font-weight: 500;
}

.stWarning {
    background-color: rgba(245, 158, 11, 0.1);
    border: 1px solid var(--accent-orange);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: var(--text-dark);
    font-weight: 500;
}

.stInfo {
    background-color: rgba(59, 130, 246, 0.1);
    border: 1px solid var(--primary-blue);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    color: var(--text-dark);
    font-weight: 500;
}

/* 사이드바 스타일 - 라이트 테마 */
.sidebar .sidebar-content {
    background-color: var(--bg-gray);
    color: var(--text-dark);
}

/* 메트릭 카드 스타일 - 깔끔한 디자인 */
[data-testid="metric-container"] {
    background-color: var(--bg-light);
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    color: var(--text-dark);
}

/* 탭 스타일 - 깔끔한 디자인 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: var(--bg-gray);
    border-radius: 6px 6px 0 0;
    color: var(--text-light);
    font-weight: 500;
    padding: 10px 16px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.stTabs [aria-selected="true"] {
    background-color: var(--primary-blue);
    color: var(--white);
    border-color: var(--primary-blue);
}

/* 체크박스 스타일 - 높은 가독성 */
.stCheckbox > label {
    color: var(--text-dark);
    font-weight: 500;
    font-size: 1rem;
}

/* 슬라이더 스타일 - 깔끔한 디자인 */
.stSlider > div > div > div > div {
    background: var(--primary-blue);
    border-radius: 4px;
}

/* 셀렉트박스 스타일 - 높은 가독성 */
.stSelectbox > div > div {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background-color: var(--bg-light);
    color: var(--text-dark);
}

.stSelectbox > div > div:hover {
    border-color: var(--primary-blue);
}

/* 텍스트 입력 스타일 */
.stTextInput > div > div > input {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    color: var(--text-dark);
}

.stTextInput > div > div > input:focus {
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 확장기 스타일 */
.stExpander > div > div {
    background-color: var(--bg-light);
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    color: var(--text-dark);
}

/* 구분선 스타일 */
hr {
    border-color: #e5e7eb;
    margin: 2rem 0;
}

/* 확장 패널 스타일 */
.streamlit-expanderHeader {
    background-color: var(--light-gray);
    border-radius: 6px;
    font-weight: 600;
    color: var(--text-dark);
}

/* 구분선 스타일 */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--neutral-gray), transparent);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# AI API 설정
from config import GEMINI_API_KEY, OPENAI_API_KEY

if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

if OPENAI_API_KEY and OPENAI_AVAILABLE:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

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
    st.session_state.steps_completed = [False, False, False, False, False, False]  # 6단계로 수정
if 'exercise_schedule' not in st.session_state:
    st.session_state.exercise_schedule = {}
if 'subjective_status' not in st.session_state:
    st.session_state.subjective_status = ""
if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = "홈"
if 'next_menu' not in st.session_state:
    st.session_state.next_menu = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = f'user_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

def init_google_sheets():
    try:
        if not GSPREAD_AVAILABLE or not os.path.exists(GOOGLE_SHEETS_CREDENTIALS):
            return None
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

def save_to_sheets(data, sheet_name="vdt_data"):
    try:
        if not GSPREAD_AVAILABLE or not SPREADSHEET_ID or not os.path.exists(GOOGLE_SHEETS_CREDENTIALS):
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

def generate_consultation_summary(user_data, conditions, pain_scores):
    """상담 완료 후 상태 요약 생성"""
    # 주요 증상 분석
    main_condition = conditions[0] if conditions else "VDT 증후군"
    
    # 통증 레벨 평가
    avg_pain = sum(pain_scores.values()) / len(pain_scores) if pain_scores else 0
    
    # 작업환경 점수
    env_score = user_data.get('env_score', 50)
    work_hours = user_data.get('daily_work_hours', 8)
    
    if avg_pain >= 7:
        severity = "중증"
    elif avg_pain >= 5:
        severity = "중등도"
    elif avg_pain >= 3:
        severity = "경증"
    else:
        severity = "경미한"
    
    if env_score < 40:
        env_status = "불량한 작업환경으로 인한"
    elif env_score < 70:
        env_status = "개선이 필요한 작업환경에서의"
    else:
        env_status = "양호한 작업환경에서의"
    
    if work_hours >= 10:
        work_status = "과도한 업무량과"
    elif work_hours >= 8:
        work_status = "일반적인 업무량과"
    else:
        work_status = "적정 업무량과"
    
    summary = f"{env_status} {work_status} 관련된 {severity} {main_condition} 증상"
    return summary

def recommend_exercise_purpose(user_data, conditions, pain_scores):
    """설문조사 기반 운동 목적 자동 추천"""
    try:
        # 통증 수준 평균 계산
        avg_pain = sum(pain_scores.values()) / len(pain_scores) if pain_scores else 0
        
        # 작업환경 점수
        env_score = user_data.get('env_score', 50)
        
        # 운동 습관
        exercise_habit = user_data.get('exercise_habit', '전혀 안함')
        
        # 나이
        age = user_data.get('age', 30)
        
        # 추천 로직
        # 1. 고통증 (평균 7점 이상) -> 재활
        if avg_pain >= 7:
            return {
                'purpose': '재활 (통증감소)',
                'reason': f'평균 통증 수준이 {avg_pain:.1f}점으로 높아 통증 감소가 우선적으로 필요합니다.',
                'confidence': 'high'
            }
        
        # 2. 중간 통증 (4-6점) + 나쁜 작업환경 -> 재활
        elif avg_pain >= 4 and env_score < 50:
            return {
                'purpose': '재활 (통증감소)',
                'reason': f'통증 수준 {avg_pain:.1f}점과 작업환경 {env_score}점으로 재활이 필요합니다.',
                'confidence': 'medium'
            }
        
        # 3. 운동 습관 좋음 (주 3회 이상) + 낮은 통증 -> 운동
        elif exercise_habit in ['주 3-4회', '주 5회 이상'] and avg_pain < 4:
            return {
                'purpose': '운동 (근력 및 체력 증진)',
                'reason': f'규칙적인 운동 습관({exercise_habit})과 낮은 통증 수준으로 체력 증진이 적합합니다.',
                'confidence': 'high'
            }
        
        # 4. 젊은 나이 + 운동 습관 있음 -> 운동
        elif age <= 35 and exercise_habit in ['주 1-2회', '주 3-4회', '주 5회 이상']:
            return {
                'purpose': '운동 (근력 및 체력 증진)',
                'reason': f'젊은 연령({age}세)과 운동 경험으로 근력 증진이 효과적입니다.',
                'confidence': 'medium'
            }
        
        # 5. 기본: 예방 (자세교정)
        else:
            return {
                'purpose': '예방 (자세교정)',
                'reason': f'현재 상태를 고려할 때 자세 교정을 통한 예방이 가장 적합합니다.',
                'confidence': 'medium'
            }
            
    except Exception as e:
        print(f"운동 목적 추천 오류: {e}")
        return {
            'purpose': '예방 (자세교정)',
            'reason': '기본 추천: 자세 교정을 통한 예방',
            'confidence': 'low'
        }

def get_detailed_stretching_instructions():
    """스트레칭 상세 방법 안내"""
    stretching_guide = {
        "목 스트레칭": {
            "자세": "의자에 똑바로 앉아 어깨를 자연스럽게 내린 상태",
            "방법": [
                "1. 고개를 천천히 오른쪽으로 기울여 15초간 유지",
                "2. 같은 방법으로 왼쪽으로 기울여 15초간 유지", 
                "3. 고개를 천천히 앞으로 숙여 15초간 유지",
                "4. 고개를 뒤로 젖혀 15초간 유지 (과도하지 않게)"
            ],
            "주의사항": "급격한 움직임 금지, 통증이 있으면 즉시 중단",
            "효과": "목 근육 이완, 긴장성 두통 완화"
        },
        "어깨 스트레칭": {
            "자세": "서거나 앉은 상태에서 등을 곧게 편 자세",
            "방법": [
                "1. 오른팔을 왼쪽으로 당겨 가슴 앞에서 15초간 유지",
                "2. 왼팔로 오른팔을 감싸며 당겨주기",
                "3. 반대쪽도 같은 방법으로 실시",
                "4. 양팔을 위로 들어 좌우로 기울이며 옆구리 늘리기"
            ],
            "주의사항": "어깨에 무리가 가지 않도록 서서히 진행",
            "효과": "어깨 근육 이완, 라운드 숄더 예방"
        },
        "허리 스트레칭": {
            "자세": "바닥에 매트를 깔고 누운 상태 또는 의자에 앉은 상태",
            "방법": [
                "1. 무릎을 가슴쪽으로 당겨 20초간 유지",
                "2. 다리를 쭉 뻗고 상체를 앞으로 숙여 발끝 터치",
                "3. 의자에 앉아 몸통을 좌우로 비틀기",
                "4. 허리를 뒤로 젖혀 등 근육 스트레칭"
            ],
            "주의사항": "허리 디스크가 있는 경우 전문가 상담 후 실시",
            "효과": "허리 근육 이완, 요통 예방"
        }
    }
    return stretching_guide

def create_personalized_exercise_routine(user_data, conditions, pain_scores, exercise_schedule, exercise_purpose="재활 (통증감소)"):
    """개인 맞춤 운동 루틴 생성 - 설문 기반"""
    if not exercise_schedule or not exercise_schedule.get('available_days'):
        return None
    
    available_days = exercise_schedule.get('available_days', [])
    daily_minutes = exercise_schedule.get('daily_minutes', 30)
    difficulty_level = exercise_schedule.get('difficulty_level', '초급자')
    
    # 요일별 루틴 생성
    weekly_routine = {}
    
    for day in available_days:
        # 시간 배분: 75% 유튜브 영상, 15% 스트레칭, 10% 워밍업
        video_time = int(daily_minutes * 0.75)
        stretching_time = int(daily_minutes * 0.15)
        warmup_time = daily_minutes - video_time - stretching_time  # 나머지 시간
        
        # 각 증상별 영상 수집
        all_videos = []
        for condition in conditions:
            videos = get_enhanced_exercise_videos(condition, exercise_purpose, limit=5)
            if videos:
                all_videos.extend(videos)
        
        # 비디오 시간에 맞게 선택
        selected_videos = select_videos_for_time(all_videos, video_time, difficulty_level)
        
        # 환자 상태별 맞춤 스트레칭
        condition_stretches = get_condition_specific_stretches(conditions, pain_scores)
        
        daily_routine = {
            "총_시간": daily_minutes,
            "워밍업_시간": warmup_time,
            "영상_시간": video_time,
            "스트레칭_시간": stretching_time,
            "선택된_영상": selected_videos,
            "맞춤_스트레칭": condition_stretches,
            "난이도": difficulty_level
        }
        
        weekly_routine[day] = daily_routine
    
    return {
        "주간_루틴": weekly_routine,
        "총_주간시간": exercise_schedule.get('total_weekly_minutes', 0),
        "운동_일수": len(available_days),
        "스트레칭_가이드": get_detailed_stretching_instructions()
    }

def select_videos_for_time(videos, target_minutes, difficulty_level):
    """주어진 시간에 맞게 영상 선택"""
    if not videos:
        return []
    
    selected = []
    total_time = 0
    difficulty_priority = {"초급자": 1, "초중급": 2, "중급자": 3, "중상급": 4, "상급자": 5}
    user_level = difficulty_priority.get(difficulty_level, 1)
    
    # 영상을 시간순으로 정렬 (짧은 것부터)
    sorted_videos = sorted(videos, key=lambda x: parse_duration_to_minutes(x.get('duration', '0:00')))
    
    for video in sorted_videos:
        video_minutes = parse_duration_to_minutes(video)
        
        # 남은 시간에 맞는지 확인
        if total_time + video_minutes <= target_minutes:
            selected.append(video)
            total_time += video_minutes
            
        # 목표 시간의 90% 이상 채우면 완료
        if total_time >= target_minutes * 0.9:
            break
    
    return selected

def parse_duration_to_minutes(duration_input):
    """영상 길이를 분 단위로 변환"""
    try:
        # duration_seconds 필드가 있으면 우선 사용
        if isinstance(duration_input, dict):
            if 'duration_seconds' in duration_input:
                return duration_input['duration_seconds'] / 60
            elif 'duration' in duration_input:
                duration_str = duration_input['duration']
            else:
                return 5
        else:
            duration_str = duration_input
        
        # 숫자인 경우 (초 단위로 가정)
        if isinstance(duration_str, (int, float)):
            return duration_str / 60 if duration_str > 60 else duration_str
        
        # 문자열 파싱
        if ':' in str(duration_str):
            parts = str(duration_str).split(':')
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes + (seconds / 60)
            elif len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours * 60 + minutes + (seconds / 60)
        
        return 5  # 기본값
    except:
        return 5

def format_duration_from_seconds(seconds):
    """초를 분:초 형식으로 변환"""
    try:
        if isinstance(seconds, str):
            seconds = int(seconds)
        
        if seconds < 60:
            return f"0:{seconds:02d}"
        
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        
        if minutes >= 60:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            return f"{hours}:{remaining_minutes:02d}:{remaining_seconds:02d}"
        else:
            return f"{minutes}:{remaining_seconds:02d}"
    except:
        return "정보없음"

def get_video_duration_display(video):
    """비디오 객체에서 duration 정보를 올바르게 추출하고 포맷팅"""
    try:
        # 1. duration_seconds 필드 확인 (Supabase 주 필드)
        if 'duration_seconds' in video and video['duration_seconds']:
            return format_duration_from_seconds(video['duration_seconds'])
        
        # 2. duration 필드 확인 (백업 필드)
        if 'duration' in video and video['duration']:
            duration = video['duration']
            if isinstance(duration, (int, float)):
                return format_duration_from_seconds(duration)
            else:
                return str(duration)
        
        return "정보없음"
    except:
        return "정보없음"

def calculate_video_repetitions(videos, target_minutes):
    """목표 시간에 맞춰 각 영상의 반복 횟수 계산"""
    try:
        if not videos or target_minutes <= 0:
            return {
                'repetition_plan': [],
                'total_planned_minutes': 0,
                'target_minutes': target_minutes,
                'achievement_rate': 0
            }
        
        # 각 영상의 분 단위 길이 계산
        video_data = []
        for video in videos:
            duration_minutes = parse_duration_to_minutes(video)
            if duration_minutes > 0:
                video_data.append({
                    'video': video,
                    'duration_minutes': duration_minutes
                })
        
        if not video_data:
            return {
                'repetition_plan': [],
                'total_planned_minutes': 0,
                'target_minutes': target_minutes,
                'achievement_rate': 0
            }
        
        # 총 영상 시간 계산
        total_video_minutes = sum(v['duration_minutes'] for v in video_data)
        
        # 목표 시간과의 비율 계산
        ratio = target_minutes / total_video_minutes if total_video_minutes > 0 else 1
        
        # 각 영상의 반복 횟수 계산
        repetition_plan = []
        total_planned_minutes = 0
        
        for i, video_info in enumerate(video_data):
            video = video_info['video']
            duration_minutes = video_info['duration_minutes']
            
            # 기본 반복 횟수 (비율 기준)
            base_repetitions = max(1, round(ratio))
            
            # 마지막 영상은 남은 시간에 맞춰 조정
            if i == len(video_data) - 1:
                remaining_time = target_minutes - total_planned_minutes
                final_repetitions = max(1, round(remaining_time / duration_minutes))
                repetitions = final_repetitions
            else:
                repetitions = base_repetitions
            
            # 최대 5회까지 제한 (너무 많은 반복 방지)
            repetitions = min(repetitions, 5)
            
            planned_minutes = repetitions * duration_minutes
            total_planned_minutes += planned_minutes
            
            repetition_plan.append({
                'video': video,
                'duration_minutes': duration_minutes,
                'repetitions': repetitions,
                'total_minutes': planned_minutes
            })
        
        return {
            'repetition_plan': repetition_plan,
            'total_planned_minutes': total_planned_minutes,
            'target_minutes': target_minutes,
            'achievement_rate': (total_planned_minutes / target_minutes * 100) if target_minutes > 0 else 0
        }
        
    except Exception as e:
        print(f"반복 횟수 계산 오류: {e}")
        return {
            'repetition_plan': [],
            'total_planned_minutes': 0,
            'target_minutes': target_minutes,
            'achievement_rate': 0
        }

def get_condition_specific_stretches(conditions, pain_scores):
    """환자 증상별 맞춤 스트레칭"""
    stretches = []
    
    for condition in conditions:
        pain_level = pain_scores.get(condition, 0)
        
        if "목" in condition or "거북목" in condition:
            if pain_level >= 7:
                stretches.append({
                    "부위": "목 (중증)",
                    "동작": "매우 부드러운 목 좌우 기울이기",
                    "시간": "각 방향 10초씩",
                    "횟수": "3세트",
                    "주의": "통증이 있으면 즉시 중단"
                })
            else:
                stretches.append({
                    "부위": "목 (일반)",
                    "동작": "목 스트레칭 (상하좌우)",
                    "시간": "각 방향 15초씩",
                    "횟수": "3세트",
                    "주의": "천천히 부드럽게"
                })
        
        if "어깨" in condition or "라운드숄더" in condition:
            stretches.append({
                "부위": "어깨",
                "동작": "어깨 돌리기 + 가슴 열기",
                "시간": "20초씩",
                "횟수": "5세트",
                "주의": "어깨에 무리가 가지 않게"
            })
        
        if "허리" in condition:
            if pain_level >= 6:
                stretches.append({
                    "부위": "허리 (조심)",
                    "동작": "무릎 가슴으로 당기기 (누워서)",
                    "시간": "15초",
                    "횟수": "3세트",
                    "주의": "허리에 무리 없는 범위 내에서"
                })
            else:
                stretches.append({
                    "부위": "허리",
                    "동작": "허리 비틀기 + 고양이 자세",
                    "시간": "각 20초씩",
                    "횟수": "3세트",
                    "주의": "천천히 진행"
                })
    
    return stretches

def check_customer_history(email):
    """고객 이력 확인 (초진/재진 판별) - 통합 데이터베이스 사용"""
    try:
        from customer_database import get_customer_data, get_visit_count, increment_visit_count
        
        # 통합 데이터베이스에서 고객 정보 조회
        existing_customer = get_customer_data(email)
        
        if existing_customer:
            # 기존 고객 - 실제 방문 횟수 조회
            visit_count = get_visit_count(email)
            
            # 세션에 이미 방문 기록이 없으면 방문 횟수 증가
            if 'visit_incremented' not in st.session_state:
                visit_count = increment_visit_count(email)
                st.session_state.visit_incremented = True
            
            return {
                'is_return_customer': True,
                'previous_visit': existing_customer,
                'visit_count': visit_count
            }
        else:
            # 신규 고객
            return {
                'is_return_customer': False,
                'previous_visit': None,
                'visit_count': 0
            }
    except Exception as e:
        print(f"고객 이력 확인 오류: {e}")
        return None

def save_customer_data(email, user_data, conditions, pain_scores):
    """통합 고객 데이터베이스에 저장"""
    try:
        # 통합 데이터베이스 사용
        from customer_database import save_customer_data as save_to_db, get_customer_data, get_visit_count
        
        # 기존 고객 확인
        existing_customer = get_customer_data(email)
        
        if existing_customer:
            # 재방문 고객 - 실제 방문 횟수 조회
            visit_count = get_visit_count(email)
            st.session_state.user_data['customer_history'] = {
                'is_return_customer': True,
                'previous_visit': existing_customer,
                'visit_count': visit_count
            }
            print(f"재방문 고객 확인: {email} (방문 {visit_count}회)")
        else:
            # 신규 고객
            st.session_state.user_data['customer_history'] = {
                'is_return_customer': False,
                'previous_visit': None,
                'visit_count': 1
            }
            print(f"신규 고객 등록: {email}")
        
        # 통합 데이터베이스에 저장
        success = save_to_db(email, user_data, conditions, pain_scores)
        
        if success:
            print(f"통합 DB 저장 성공: {email}")
            
            # 백업: Google Sheets 저장
            try:
                from datetime import datetime
                import json
                sheets_data = {
                    'timestamp': datetime.now().isoformat(),
                    'user_id': email,
                    'data_type': 'customer_survey',
                    'conditions': ', '.join(conditions),
                    'user_age': user_data.get('age'),
                    'user_gender': user_data.get('gender'),
                    'work_hours': user_data.get('daily_work_hours'),
                    'exercise_purpose': user_data.get('exercise_purpose', ''),
                    'ai_recommendation': user_data.get('ai_recommended_purpose', ''),
                    'pain_scores': json.dumps(pain_scores, ensure_ascii=False),
                    'work_intensity': user_data.get('work_intensity'),
                    'env_score': user_data.get('env_score')
                }
                save_to_sheets(sheets_data)
                print(f"Google Sheets 백업 완료: {email}")
            except Exception as sheets_error:
                print(f"Google Sheets 백업 실패: {sheets_error}")
            
            return True
        else:
            print(f"통합 DB 저장 실패: {email}")
            return False
        
    except Exception as e:
        print(f"고객 데이터 저장 오류: {e}")
        return False

def analyze_condition_changes(current_conditions, current_pain_scores, previous_visit):
    """이전 방문 대비 증상 변화 분석"""
    try:
        import json
        
        prev_conditions = json.loads(previous_visit.get('conditions', '[]'))
        prev_pain_scores = json.loads(previous_visit.get('pain_scores', '{}'))
        
        analysis = {
            'new_conditions': [],
            'resolved_conditions': [],
            'pain_changes': {},
            'overall_status': 'similar'
        }
        
        # 새로 생긴 증상
        analysis['new_conditions'] = [c for c in current_conditions if c not in prev_conditions]
        
        # 해결된 증상
        analysis['resolved_conditions'] = [c for c in prev_conditions if c not in current_conditions]
        
        # 통증 변화 분석
        total_current_pain = sum(current_pain_scores.values())
        total_previous_pain = sum([prev_pain_scores.get(condition, 0) for condition in prev_conditions])
        
        if total_current_pain > total_previous_pain * 1.2:
            analysis['overall_status'] = 'worsened'
        elif total_current_pain < total_previous_pain * 0.8:
            analysis['overall_status'] = 'improved'
        else:
            analysis['overall_status'] = 'similar'
        
        # 각 증상별 통증 변화
        for condition in current_conditions:
            if condition in prev_conditions:
                current_pain = current_pain_scores.get(condition, 0)
                previous_pain = prev_pain_scores.get(condition, 0)
                change = current_pain - previous_pain
                
                if change > 1:
                    analysis['pain_changes'][condition] = 'increased'
                elif change < -1:
                    analysis['pain_changes'][condition] = 'decreased'
                else:
                    analysis['pain_changes'][condition] = 'stable'
        
        return analysis
    except Exception as e:
        print(f"증상 변화 분석 오류: {e}")
        return None

def get_enhanced_exercise_videos(condition, purpose="예방", limit=10):
    """
    Supabase에서 사용자 맞춤 운동 영상을 가져오고,
    없는 경우 기본 데이터베이스에서 가져옴
    """
    try:
        if YOUTUBE_SEARCH_AVAILABLE:
            db_videos = get_videos_for_condition(condition, purpose, limit)
            if db_videos and len(db_videos) >= 3:
                return db_videos[:limit]
    except:
        pass
    
    # 백업용 비디오 데이터베이스 (더 많은 영상 추가)
    videos_db = {
        "거북목": [
            {"title": "거북목 교정 운동 5분", "url": "https://youtu.be/8hlp5u8m_Ao", "channel_name": "핏블리", "duration": "5:23", "view_count": "1.2M"},
            {"title": "거북목 스트레칭 10분", "url": "https://youtu.be/example1", "channel_name": "물리치료사", "duration": "10:00", "view_count": "850K"},
            {"title": "목 근력 강화 운동", "url": "https://youtu.be/example2", "channel_name": "헬스코치", "duration": "7:45", "view_count": "620K"}
        ],
        "라운드숄더": [
            {"title": "라운드숄더 교정 운동", "url": "https://youtu.be/oLwTC-lAJws", "channel_name": "핏블리", "duration": "8:30", "view_count": "2.1M"},
            {"title": "어깨 자세 교정 루틴", "url": "https://youtu.be/example3", "channel_name": "필라테스", "duration": "12:00", "view_count": "950K"},
            {"title": "라운드숄더 예방 스트레칭", "url": "https://youtu.be/example4", "channel_name": "요가코치", "duration": "15:00", "view_count": "780K"}
        ],
        "허리디스크": [
            {"title": "허리 강화 운동", "url": "https://youtu.be/4BOTvaRaDjI", "channel_name": "핏블리", "duration": "9:42", "view_count": "1.8M"},
            {"title": "허리디스크 재활 운동", "url": "https://youtu.be/example5", "channel_name": "정형외과", "duration": "20:00", "view_count": "1.5M"},
            {"title": "코어 근력 강화", "url": "https://youtu.be/example6", "channel_name": "헬스트레이너", "duration": "11:30", "view_count": "890K"}
        ],
        "손목터널증후군": [
            {"title": "손목터널증후군 스트레칭", "url": "https://youtu.be/EiRC80FJbHU", "channel_name": "물리치료", "duration": "6:33", "view_count": "445K"},
            {"title": "손목 근력 강화 운동", "url": "https://youtu.be/example7", "channel_name": "재활의학과", "duration": "8:00", "view_count": "320K"},
            {"title": "손목 보호 스트레칭", "url": "https://youtu.be/example8", "channel_name": "전문의", "duration": "5:15", "view_count": "280K"}
        ]
    }
    return videos_db.get(condition, [])

def analyze_user_symptoms(user_data, conditions, pain_scores):
    """사용자의 증상을 분석하여 멘트 생성"""
    analysis = []
    
    # 증상별 분석
    for condition in conditions:
        pain_level = pain_scores.get(condition, 0)
        if pain_level >= 7:
            severity = "심각한 수준으로"
        elif pain_level >= 5:
            severity = "중간 수준으로"
        elif pain_level >= 3:
            severity = "경미한 수준으로"
        else:
            severity = "예방 차원에서"
        
        analysis.append(f"• **{condition}**: {severity} 증상이 나타나고 있습니다. (통증 지수 {pain_level}/10점)")
    
    # 작업환경 분석
    env_score = user_data.get('env_score', 0)
    work_hours = user_data.get('daily_work_hours', 8)
    work_intensity = user_data.get('work_intensity', '보통')
    
    if env_score < 40:
        env_analysis = f"작업환경 점수가 {env_score}점으로 개선이 시급합니다."
    elif env_score < 70:
        env_analysis = f"작업환경 점수가 {env_score}점으로 보통 수준입니다."
    else:
        env_analysis = f"작업환경 점수가 {env_score}점으로 양호한 편입니다."
    
    if work_hours >= 10:
        work_analysis = f"일일 {work_hours}시간의 장시간 작업으로 근골격계 문제 위험이 높습니다."
    elif work_hours >= 8:
        work_analysis = f"일일 {work_hours}시간의 일반적인 사무직 근무로 예방 관리가 중요합니다."
    else:
        work_analysis = f"일일 {work_hours}시간의 비교적 짧은 근무로 예방 중심의 관리가 적합합니다."
    
    return analysis, env_analysis, work_analysis

def create_video_based_weekly_schedule(exercise_schedule, conditions, pain_scores, exercise_purpose):
    """운동 스케줄과 영상을 기반으로 주간 운동 계획 생성"""
    available_days = exercise_schedule.get('available_days', [])
    daily_minutes = exercise_schedule.get('daily_minutes', 30)
    difficulty_level = exercise_schedule.get('difficulty_level', '초급자')
    
    # 각 증상별 영상 가져오기
    all_videos = {}
    for condition in conditions:
        videos = get_enhanced_exercise_videos(condition, exercise_purpose, limit=5)
        if videos:
            all_videos[condition] = videos
    
    # 주간 계획 생성
    weekly_plan = {}
    video_rotation = 0
    
    for i, day in enumerate(available_days):
        daily_videos = []
        remaining_minutes = daily_minutes
        
        # 메인 운동 영상 (총 시간의 60-70%)
        main_exercise_time = int(daily_minutes * 0.65)
        
        # 각 증상별로 영상 배치
        for condition in conditions:
            if condition in all_videos and all_videos[condition]:
                video_idx = (i + video_rotation) % len(all_videos[condition])
                video = all_videos[condition][video_idx]
                
                # 영상 길이 파싱
                duration_str = video.get('duration', '5:00')
                try:
                    if ':' in str(duration_str):
                        minutes = int(duration_str.split(':')[0])
                    else:
                        minutes = 5  # 기본값
                except:
                    minutes = 5
                
                if minutes <= remaining_minutes:
                    daily_videos.append({
                        'condition': condition,
                        'title': video.get('title', '제목 없음'),
                        'url': video.get('url', '#'),
                        'duration': duration_str,
                        'minutes': minutes,
                        'channel': video.get('channel_name', '알 수 없음')
                    })
                    remaining_minutes -= minutes
        
        # 나머지 시간은 스트레칭/마무리 운동
        stretching_time = remaining_minutes
        
        weekly_plan[day] = {
            'main_videos': daily_videos,
            'main_exercise_minutes': sum([v['minutes'] for v in daily_videos]),
            'stretching_minutes': stretching_time,
            'total_minutes': daily_minutes,
            'warm_up_minutes': 5,
            'cool_down_minutes': max(stretching_time - 5, 5)
        }
        
        video_rotation += 1
    
    return weekly_plan

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

def send_test_email(sender_email, app_password, recipient_email=None, work_start=None, work_end=None, interval=None):
    try:
        from config import SMTP_SERVER, SMTP_PORT
        
        # 수신자 이메일이 지정되지 않으면 발신자 이메일로 설정
        if not recipient_email:
            recipient_email = sender_email
            
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 활성화 안내"
        
        # 시간 정보가 제공된 경우 포함, 그렇지 않으면 기본 메시지
        if work_start and work_end and interval:
            body = f"""
안녕하세요! VDT 증후군 관리 시스템입니다.

휴식 알리미가 정상적으로 설정되었습니다.
앞으로 설정하신 {work_start}~{work_end}시간에 맞춰 {interval}분 간격으로
맞춤 운동 알림을 보내드리겠습니다.

건강한 개발 생활을 응원합니다! 💪

---
VDT 증후군 관리 시스템
            """
        else:
            body = f"""
안녕하세요! VDT 증후군 관리 시스템입니다.

휴식 알리미가 정상적으로 설정되었습니다.
앞으로 설정하신 시간에 맞춰 맞춤 운동 알림을 보내드리겠습니다.

건강한 개발 생활을 응원합니다! 💪

---
VDT 증후군 관리 시스템
            """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"이메일 발송 실패: {str(e)}")
        return False

def send_test_slack(webhook_url, work_start=None, work_end=None, interval=None):
    try:
        if work_start and work_end and interval:
            message = f"""🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 활성화 안내

안녕하세요! VDT 증후군 관리 시스템입니다.

휴식 알리미가 정상적으로 설정되었습니다.
앞으로 설정하신 {work_start}~{work_end}시간에 맞춰 {interval}분 간격으로
맞춤 운동 알림을 보내드리겠습니다.

건강한 개발 생활을 응원합니다! 💪"""
        else:
            message = "🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 테스트입니다!"
            
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Slack 메시지 발송 실패: {str(e)}")
        return False

def show_home():
    st.header("직장인들의 건강한 몸상태를 응원합니다.")
    
    st.markdown("---")
    
    # VDT 증후군 설명
    st.markdown("### 🏥 VDT 증후군의 주요 근골격계 증상")
    
    # 증상 설명을 카드 형태로 정리
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🐢 거북목 증후군**  
        모니터를 내려다보느라 목이 앞으로 구부러지는 증상
        
        **🔴 디스크 질환**  
        고개를 숙이는 자세로 목, 허리 등 척추 디스크에 가해지는 하중 증가
        """)
    
    with col2:
        st.markdown("""
        **💪 근막통증 증후군**  
        근육의 통증 유발점에 의해 발생하는 통증
        
        **⌨️ 손목터널 증후군**  
        키보드 장시간 사용으로 인한 손가락 저림 및 통증
        """)
    
    st.markdown("---")
    
    # 핵심 CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏃‍♂️ **증상 선택하고 건강 관리 시작하기**", key="quick_start", type="primary", use_container_width=True):
            st.session_state.menu_selection = "증상 선택"
            st.rerun()

def show_condition_selection():
    st.header("증상 선택 및 통증 평가")
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
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
        
        # 통증 정도 평가 추가 (이모티콘 척도 포함)
        st.subheader("🔴 통증 정도 평가")
        st.info("각 증상별로 현재 통증 정도를 아래 이모티콘과 색상을 참고하여 평가해주세요")
        
        # 통증 척도 이모티콘 및 색상 정의
        def get_pain_emoji_and_color(level):
            pain_scale = {
                0: ("😊", "#00FF00", "통증 없음"),
                1: ("🙂", "#66FF66", "매우 경미한 통증"),
                2: ("😐", "#99FF99", "경미한 통증"),
                3: ("🤕", "#CCFF99", "불편함"),
                4: ("😟", "#FFFF99", "약간 아픔"),
                5: ("😣", "#FFCC99", "보통 아픔"),
                6: ("😖", "#FF9966", "상당히 아픔"),
                7: ("😫", "#FF6633", "많이 아픔"),
                8: ("😵", "#FF3300", "심한 통증"),
                9: ("😱", "#CC0000", "매우 심한 통증"),
                10: ("🥵", "#990000", "견딜 수 없는 통증")
            }
            return pain_scale.get(level, ("❓", "#808080", "알 수 없음"))
        
        # 통증 척도 가이드 표시
        with st.expander("📊 통증 척도 가이드"):
            st.markdown("### PAIN MEASUREMENT SCALE - EMOTICON")
            cols = st.columns(11)
            for i in range(11):
                emoji, color, description = get_pain_emoji_and_color(i)
                with cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background-color: {color}; border-radius: 10px; margin: 2px;">
                        <div style="font-size: 24px;">{emoji}</div>
                        <div style="font-weight: bold; color: black;">{i}</div>
                        <div style="font-size: 10px; color: black;">{description}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        pain_scores = {}
        for condition in selected:
            st.markdown(f"### {condition} 통증 정도")
            
            # 슬라이더와 현재 선택된 값의 이모티콘 표시
            pain_level = st.slider(
                f"{condition} 통증 정도", 
                0, 10, 5, 
                key=f"pain_{condition}",
                help="위의 이모티콘 척도를 참고하여 선택해주세요"
            )
            
            # 현재 선택된 통증 수준의 이모티콘과 설명 표시
            current_emoji, current_color, current_desc = get_pain_emoji_and_color(pain_level)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background-color: {current_color}; 
                           border-radius: 15px; margin: 5px;">
                    <div style="font-size: 36px;">{current_emoji}</div>
                    <div style="font-weight: bold; color: black; font-size: 20px;">{pain_level}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                **현재 선택**: {pain_level}점  
                **상태**: {current_desc}  
                **설명**: {condition} 증상으로 인한 현재 통증이 이 정도입니다.
                """)
            
            pain_scores[condition] = pain_level
            st.markdown("---")
        
        st.session_state.user_data['pain_scores'] = pain_scores
        
        # 주관적 상태 입력 추가
        st.subheader("📋 주관적 상태 설명")
        st.info("현재 건강 상태나 증상에 대해 자유롭게 작성해주세요 (100자 이내)")
        subjective_status = st.text_area(
            "현재 상태",
            value=st.session_state.subjective_status,
            max_chars=100,
            placeholder="예: 오른쪽 어깨가 특히 많이 아프고, 업무 후 두통이 자주 생깁니다.",
            help="의료진에게 전달하고 싶은 증상을 구체적으로 작성해주세요."
        )
        st.session_state.subjective_status = subjective_status
        st.session_state.user_data['subjective_status'] = subjective_status
        
        # 심각한 통증이 있는 경우 병원 추천
        if ADS_AVAILABLE:
            for condition in selected:
                if pain_scores[condition] >= 7:  # 심각한 통증
                    show_hospital_recommendation(condition, pain_scores[condition])
        
        if st.button("✅ 저장하고 다음 단계로", key="condition_next", type="primary"):
            st.session_state.steps_completed[0] = True
            st.session_state.current_step = 1
            st.session_state.next_menu = "개인정보 입력"
            st.success("✅ 증상 선택이 완료되었습니다!")
            st.rerun()
    else:
        st.warning("⚠️ 최소 하나의 증상을 선택해주세요.")

def show_personal_info():
    st.header("개인정보 입력")
    if not st.session_state.selected_conditions:
        st.warning("먼저 증상을 선택해주세요.")
        return
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
    # Gmail 입력 및 고객 이력 확인
    st.subheader("📧 이메일 주소")
    email = st.text_input("Gmail 주소", placeholder="example@gmail.com", key="user_email")
    
    # 이메일 입력 시 고객 이력 확인
    customer_history = None
    if email and "@" in email:
        customer_history = check_customer_history(email)
        
        if customer_history and customer_history['is_return_customer']:
            # 재진 고객
            visit_count = customer_history['visit_count']
            st.success(f"👋 다시 방문해주셨군요! (총 {visit_count}번째 방문)")
            
            # 이전 방문 대비 증상 변화 분석
            previous_visit = customer_history['previous_visit']
            pain_scores = st.session_state.user_data.get('pain_scores', {})
            
            if pain_scores:  # 현재 통증 점수가 있을 때만 분석
                condition_changes = analyze_condition_changes(
                    st.session_state.selected_conditions,
                    pain_scores,
                    previous_visit
                )
                
                if condition_changes:
                    st.subheader("📊 이전 방문 대비 상태 변화")
                    
                    # 전체 상태 변화
                    if condition_changes['overall_status'] == 'improved':
                        st.success("✅ 전체적으로 호전되었습니다!")
                    elif condition_changes['overall_status'] == 'worsened':
                        st.error("⚠️ 전체적으로 악화되었습니다.")
                    else:
                        st.info("📍 전체적으로 비슷한 상태입니다.")
                    
                    # 새로 생긴 증상
                    if condition_changes['new_conditions']:
                        st.warning(f"🆕 새로 생긴 증상: {', '.join(condition_changes['new_conditions'])}")
                    
                    # 해결된 증상
                    if condition_changes['resolved_conditions']:
                        st.success(f"✅ 해결된 증상: {', '.join(condition_changes['resolved_conditions'])}")
                    
                    # 각 증상별 통증 변화
                    if condition_changes['pain_changes']:
                        st.markdown("**증상별 통증 변화:**")
                        for condition, change_type in condition_changes['pain_changes'].items():
                            if change_type == 'increased':
                                st.markdown(f"  - {condition}: 🔴 악화")
                            elif change_type == 'decreased':
                                st.markdown(f"  - {condition}: 🟢 호전")
                            else:
                                st.markdown(f"  - {condition}: 🟡 유지")
        else:
            # 초진 고객
            st.info("🆕 처음 방문해주셨네요! 환영합니다.")
    
    st.markdown("---")
    
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
    
    personal_data = {
        'email': email,
        'age': age, 
        'gender': gender, 
        'work_experience': work_experience, 
        'exercise_habit': exercise_habit, 
        'smoking': smoking, 
        'drinking': drinking, 
        'sleep_hours': sleep_hours, 
        'daily_work_hours': daily_work_hours, 
        'work_intensity': work_intensity,
        'customer_history': customer_history
    }
    st.session_state.user_data.update(personal_data)
    
    if st.button("✅ 저장하고 다음 단계로", key="personal_next", type="primary"):
        if not email or "@" not in email:
            st.error("올바른 이메일 주소를 입력해주세요.")
        else:
            # 고객 데이터 저장 (이미 완료된 설문 정보가 있는 경우)
            if st.session_state.selected_conditions and st.session_state.user_data.get('pain_scores'):
                save_customer_data(
                    email,
                    st.session_state.user_data,
                    st.session_state.selected_conditions,
                    st.session_state.user_data.get('pain_scores', {})
                )
            
            st.session_state.steps_completed[1] = True
            st.session_state.current_step = 2
            st.session_state.next_menu = "작업환경 평가"
            st.success("✅ 개인정보가 저장되었습니다!")
            st.rerun()

def show_work_environment():
    st.header("🖥️ 작업환경 평가")
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 📊 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
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
        st.session_state.next_menu = "개인 운동 설문"  # 다음 단계를 개인 운동 설문으로 변경
        st.success("✅ 작업환경 평가가 저장되었습니다!")
        st.rerun()

def show_exercise_survey():
    """개인 운동 설문 조사 페이지"""
    st.header("🏃‍♂️ 개인 운동 설문조사")
    
    if not st.session_state.selected_conditions:
        st.warning("먼저 증상을 선택해주세요.")
        return
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 📊 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
    st.subheader("📅 운동 가능 요일")
    st.info("운동이 가능한 요일을 모두 선택해주세요")
    
    days_of_week = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    available_days = []
    
    cols = st.columns(4)
    for idx, day in enumerate(days_of_week):
        with cols[idx % 4]:
            if st.checkbox(day, key=f"day_{day}"):
                available_days.append(day)
    
    st.subheader("⏰ 하루 운동 가능 시간")
    daily_minutes = st.slider(
        "하루에 운동할 수 있는 시간 (분)",
        min_value=10,
        max_value=120,
        value=30,
        step=10,
        help="무리하지 않고 지속 가능한 시간을 선택하세요"
    )
    
    st.subheader("🕐 선호 운동 시간대")
    preferred_time = st.selectbox(
        "언제 운동하시겠습니까?",
        ["아침 (06:00-09:00)", "오전 (09:00-12:00)", "점심시간 (12:00-14:00)", 
         "오후 (14:00-18:00)", "저녁 (18:00-21:00)", "밤 (21:00-24:00)", "언제든지"]
    )
    
    st.subheader("💪 운동 수준")
    difficulty_level = st.select_slider(
        "본인의 운동 수준을 선택하세요",
        options=["초급자", "초중급", "중급자", "중상급", "상급자"],
        value="초급자",
        help="현재 체력과 운동 경험을 고려하여 선택하세요"
    )
    
    # 운동 스케줄 저장
    exercise_schedule = {
        'available_days': available_days,
        'daily_minutes': daily_minutes,
        'preferred_time': preferred_time,
        'difficulty_level': difficulty_level,
        'total_weekly_minutes': len(available_days) * daily_minutes
    }
    
    st.session_state.exercise_schedule = exercise_schedule
    
    if available_days:
        st.success(f"✅ 주 {len(available_days)}일, 일일 {daily_minutes}분, 총 주간 {exercise_schedule['total_weekly_minutes']}분 운동 계획")
        
        # 운동 계획 요약
        st.subheader("📋 운동 계획 요약")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("주간 운동 일수", f"{len(available_days)}일")
            st.metric("일일 운동 시간", f"{daily_minutes}분")
        with col2:
            st.metric("주간 총 운동 시간", f"{exercise_schedule['total_weekly_minutes']}분")
            st.metric("운동 수준", difficulty_level)
        
        if st.button("✅ 저장하고 다음 단계로", key="exercise_survey_next", type="primary"):
            st.session_state.steps_completed[3] = True
            st.session_state.current_step = 4
            st.session_state.next_menu = "운동 추천"
            st.success("✅ 개인 운동 설문이 저장되었습니다!")
            st.rerun()
    else:
        st.warning("⚠️ 최소 하나의 운동 가능 요일을 선택해주세요.")

def show_exercise_recommendation():
    st.header("🩺 맞춤형 운동 상담")
    if not st.session_state.selected_conditions:
        st.warning("먼저 증상을 선택해주세요.")
        return
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 상담", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
    # 증상 분석 표시
    st.subheader("📊 현재 상태 분석")
    pain_scores = st.session_state.user_data.get('pain_scores', {})
    analysis, env_analysis, work_analysis = analyze_user_symptoms(
        st.session_state.user_data, 
        st.session_state.selected_conditions, 
        pain_scores
    )
    
    with st.container():
        st.markdown("**🔍 증상 분석 결과:**")
        for item in analysis:
            st.markdown(item)
        
        st.markdown(f"\n**🏢 작업환경 분석:** {env_analysis}")
        st.markdown(f"**⏰ 근무 패턴 분석:** {work_analysis}")
        
        # 주관적 상태가 있으면 표시
        subjective_status = st.session_state.user_data.get('subjective_status', '')
        if subjective_status:
            st.markdown(f"**📝 환자 주관적 상태:** {subjective_status}")
    
    st.markdown("---")
    
    rest_time = calculate_rest_time(st.session_state.user_data.get('work_intensity', '보통'))
    st.info(f"⏰ **권장 휴식시간**: {rest_time}분마다")
    
    # 4개 탭 사용: 전문 AI 상담, 추천 영상, 맞춤 루틴, 제품 추천
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 전문 AI와 상담하기", "📺 맞춤 운동 영상 추천", "🏃‍♀️ 맞춤형 운동 루틴 생성", "🛒 맞춤 제품 추천"])
    
    with tab1:
        st.subheader("👨‍⚕️ 재활의학과 전문의 챗봇과 실시간 상담")
        
        # 초기 운동 목적 추천
        if 'ai_recommended_purpose' not in st.session_state:
            recommended = recommend_exercise_purpose(
                st.session_state.user_data,
                st.session_state.selected_conditions,
                pain_scores
            )
            st.session_state.ai_recommended_purpose = recommended
        
        # 추천 결과 표시
        recommendation = st.session_state.ai_recommended_purpose
        
        if recommendation['confidence'] == 'high':
            st.success(f"🎯 **현재 귀하의 설문 조사를 바탕으로 '{recommendation['purpose']}'을 추천 드립니다.**")
        elif recommendation['confidence'] == 'medium':
            st.info(f"📊 **현재 귀하의 설문 조사를 바탕으로 '{recommendation['purpose']}'을 추천 드립니다.**")
        else:
            st.warning(f"💡 **현재 귀하의 설문 조사를 바탕으로 '{recommendation['purpose']}'을 추천 드립니다.**")
        
        st.markdown(f"**추천 근거:** {recommendation['reason']}")
        st.markdown("---")
        
        st.info("🎯 좀 더 세분화된 귀하의 상태를 분석하고 싶으시면 아래 채팅을 이용해주세요.")
        
        # AI 채팅 시스템
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # 채팅 메시지 표시
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # 채팅 입력
        if prompt := st.chat_input("증상이나 운동에 대해 궁금한 점을 질문해주세요..."):
            # 사용자 메시지 추가
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # AI 응답 생성 - OpenAI 우선 사용
            if OPENAI_AVAILABLE and OPENAI_API_KEY and openai_client:
                try:
                    # 전문의 역할 프롬프트
                    subjective_status = st.session_state.user_data.get('subjective_status', '')
                    system_prompt = f"""당신은 VDT 증후군 전문 재활의학과 의사입니다.
                    
환자 정보:
- 나이: {st.session_state.user_data.get('age', 'N/A')}세
- 성별: {st.session_state.user_data.get('gender', 'N/A')}
- 증상: {', '.join(st.session_state.selected_conditions)}
- 통증 수준: {', '.join([f'{k}: {v}/10점' for k, v in pain_scores.items()])}
- 작업환경 점수: {st.session_state.user_data.get('env_score', 'N/A')}/100점
- 일일 작업시간: {st.session_state.user_data.get('daily_work_hours', 'N/A')}시간
- 주관적 상태: {subjective_status if subjective_status else '없음'}

친근하고 전문적인 의료 상담을 제공해주세요. 구체적이고 실용적인 조언을 해주세요."""
                    
                    with st.chat_message("assistant"):
                        with st.spinner("전문의가 답변을 준비하고 있습니다..."):
                            response = openai_client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": prompt}
                                ],
                                max_tokens=1000,
                                temperature=0.7
                            )
                            ai_response = response.choices[0].message.content
                            st.write(ai_response)
                    
                    # AI 메시지 추가
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    with st.chat_message("assistant"):
                        st.error(f"죄송합니다. AI 상담 중 오류가 발생했습니다: {str(e)}")
            elif GEMINI_AVAILABLE and GEMINI_API_KEY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # 전문의 역할 프롬프트
                    subjective_status = st.session_state.user_data.get('subjective_status', '')
                    system_prompt = f"""당신은 VDT 증후군 전문 재활의학과 의사입니다.
                    
환자 정보:
- 나이: {st.session_state.user_data.get('age', 'N/A')}세
- 성별: {st.session_state.user_data.get('gender', 'N/A')}
- 증상: {', '.join(st.session_state.selected_conditions)}
- 통증 수준: {', '.join([f'{k}: {v}/10점' for k, v in pain_scores.items()])}
- 작업환경 점수: {st.session_state.user_data.get('env_score', 'N/A')}/100점
- 일일 작업시간: {st.session_state.user_data.get('daily_work_hours', 'N/A')}시간
- 주관적 상태: {subjective_status if subjective_status else '없음'}

친근하고 전문적인 의료 상담을 제공해주세요. 구체적이고 실용적인 조언을 해주세요."""
                    
                    full_prompt = f"{system_prompt}\n\n환자 질문: {prompt}"
                    
                    with st.chat_message("assistant"):
                        with st.spinner("전문의가 답변을 준비하고 있습니다..."):
                            response = model.generate_content(full_prompt)
                            ai_response = response.text
                            st.write(ai_response)
                    
                    # AI 메시지 추가
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    with st.chat_message("assistant"):
                        st.error(f"죄송합니다. AI 상담 중 오류가 발생했습니다: {str(e)}")
            else:
                with st.chat_message("assistant"):
                    st.warning("🤖 AI 상담 기능을 사용하려면 OpenAI 또는 Gemini API 키를 설정해주세요.")
        
        # 채팅 초기화 버튼
        if st.session_state.chat_messages:
            if st.button("🗑️ 대화 내역 삭제", key="clear_chat"):
                st.session_state.chat_messages = []
                st.rerun()
        
        # 상담 완료 후 맞춤 영상 추천으로 이동
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📺 맞춤 영상 추천 보기", key="goto_videos", type="primary"):
                st.success("👆 위의 '맞춤 운동 영상 추천' 탭을 클릭하여 주세요.")
        
        with col2:
            if st.button("🎆 상담 완료", key="consultation_complete"):
                # 상담 완료 후 최종 추천
                final_recommendation = st.session_state.ai_recommended_purpose
                
                # 채팅 기반으로 추천 업데이트 (선택적)
                if st.session_state.chat_messages:
                    # AI와의 대화 내용을 바탕으로 추천 재검토
                    updated_recommendation = recommend_exercise_purpose(
                        st.session_state.user_data,
                        st.session_state.selected_conditions,
                        pain_scores
                    )
                    st.session_state.ai_recommended_purpose = updated_recommendation
                    final_recommendation = updated_recommendation
                
                st.markdown("---")
                st.success("✅ 채팅이 마무리 되었습니다.")
                
                # 최종 추천 표시
                if final_recommendation['confidence'] == 'high':
                    st.success(f"🎯 **최종적으로 '{final_recommendation['purpose']}'을 추천 드립니다.**")
                else:
                    st.info(f"📊 **최종적으로 '{final_recommendation['purpose']}'을 추천 드립니다.**")
                
                st.markdown(f"**추천 근거:** {final_recommendation['reason']}")
                st.warning("🏥 더 자세한 진료를 받고 싶으시면 주변 정형외과나 재활의학과 등을 추천드립니다.")
                
                # 최종 추천을 session state에 저장
                st.session_state.final_exercise_purpose = final_recommendation['purpose']
                st.session_state.consultation_completed = True
    
    with tab2:
        st.subheader("📺 맞춤 운동 영상 추천")
        
        # AI 추천 운동 목적 확인
        if not st.session_state.get('final_exercise_purpose'):
            if not st.session_state.get('ai_recommended_purpose'):
                st.warning("❗ 먼저 '전문 AI와 상담하기' 탭에서 상담을 진행해주세요.")
                return
            ai_exercise_purpose = st.session_state.ai_recommended_purpose['purpose']
        else:
            ai_exercise_purpose = st.session_state.final_exercise_purpose
        
        # AI 추천 운동 목적 표시
        st.success(f"🤖 **AI 추천 운동 목적**: {ai_exercise_purpose}")
        if 'ai_recommended_purpose' in st.session_state:
            st.markdown(f"**추천 근거**: {st.session_state.ai_recommended_purpose.get('reason', '')}")
        
        st.markdown("---")
        
        # 추가 운동 목적 선택 기능
        st.subheader("🎯 원하는 운동 목적 선택하기")
        st.info("AI 추천 외에 다른 운동 목적도 궁금하시다면 아래에서 선택해보세요. (맞춤형 운동 루틴 생성에는 영향을 주지 않습니다)")
        
        manual_purpose = st.selectbox(
            "추가로 확인하고 싶은 운동 목적을 선택하세요:",
            ["선택안함", "예방 (자세교정)", "운동 (근력 및 체력 증진)", "재활 (통증감소)"],
            key="manual_exercise_purpose"
        )
        
        st.markdown("---")
        
        # 영상 추천 표시 섹션
        purposes_to_show = []
        
        # 1. AI 추천 목적은 항상 표시
        purposes_to_show.append(("AI 추천", ai_exercise_purpose))
        
        # 2. 수동 선택된 목적이 있고, AI 추천과 다르다면 추가 표시
        if manual_purpose != "선택안함" and manual_purpose != ai_exercise_purpose:
            purposes_to_show.append(("추가 선택", manual_purpose))
        
        # 각 운동 목적별 영상 추천 표시
        for purpose_type, exercise_purpose in purposes_to_show:
            if purpose_type == "AI 추천":
                st.subheader(f"🤖 AI 추천 운동 목적: {exercise_purpose}")
            else:
                st.subheader(f"🎯 추가 선택 운동 목적: {exercise_purpose}")
            
            # 각 증상별 추천 영상 표시
            for condition in st.session_state.selected_conditions:
                st.write(f"### {condition} 관련 영상 ({exercise_purpose})")
                
                # Supabase에서 전체 비디오 가져오기 (최대 10개)
                all_videos = get_enhanced_exercise_videos(condition, exercise_purpose, limit=10)
                
                if all_videos:
                    # 총 영상 개수 표시
                    st.info(f"🎯 {exercise_purpose} 목적으로 추천하는 영상은 총 **{len(all_videos)}개** 입니다.")
                    
                    # 상위 3개 영상 강조 표시
                    st.success(f"⭐ 이 중 가장 우선적으로 추천하는 영상 3개:")
                    
                    # 상위 3개 영상 표시
                    top_videos = all_videos[:3]
                    for i, video in enumerate(top_videos, 1):
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                # 하이퍼링크로만 표시 (썸네일 없음)
                                st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                                duration = get_video_duration_display(video)
                                if isinstance(duration, int):
                                    duration = format_duration(duration)
                                channel = video.get('channel_name', '알 수 없음')
                                view_count = video.get('view_count', 0)
                                if isinstance(view_count, int):
                                    view_count = format_view_count(view_count)
                                st.caption(f"📺 {channel} | ⏱️ {duration} | 👁️ {view_count} 조회수")
                            with col2:
                                if i == 1:
                                    st.metric("추천도", "🥇 최우선")
                                elif i == 2:
                                    st.metric("추천도", "🥈 우선")
                                else:
                                    st.metric("추천도", "🥉 권장")
                    
                    # 나머지 영상 보기 (선택적)
                    if len(all_videos) > 3:
                        with st.expander("📋 추가 추천 영상 보기"):
                            for i, video in enumerate(all_videos[3:], 4):
                                # 하이퍼링크로만 표시 (썸네일 없음)
                                st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                                duration = get_video_duration_display(video)
                                if isinstance(duration, int):
                                    duration = format_duration(duration)
                                channel = video.get('channel_name', '알 수 없음')
                                st.caption(f"📺 {channel} | ⏱️ {duration}")
                else:
                    st.warning(f"🔍 {exercise_purpose} 목적에 맞는 {condition} 관련 영상을 찾을 수 없습니다.")
                
                st.markdown("---")
            
            # 운동 목적 구분선
            if len(purposes_to_show) > 1 and purpose_type == "AI 추천":
                st.markdown("---")
                st.markdown("---")
        
        
    
    with tab3:
        st.subheader("🏃‍♀️ 맞춤형 운동 루틴 생성")
        
        # AI 추천 운동 목적 확인
        if not st.session_state.get('final_exercise_purpose'):
            if not st.session_state.get('ai_recommended_purpose'):
                st.warning("❗ 먼저 '전문 AI와 상담하기' 탭에서 상담을 진행해주세요.")
                return
            exercise_purpose = st.session_state.ai_recommended_purpose['purpose']
        else:
            exercise_purpose = st.session_state.final_exercise_purpose
        
        # 설문 데이터 확인
        exercise_schedule = st.session_state.get('exercise_schedule', {})
        
        if not exercise_schedule or not exercise_schedule.get('available_days'):
            st.warning("❗ 먼저 '개인 운동 설문조사'를 완료해주세요.")
            st.info("📋 운동 가능한 요일과 시간을 설정한 후 맞춤 루틴을 생성할 수 있습니다.")
            return
        
        # 상담 결과 기반 분석 표시
        analysis_summary = generate_consultation_summary(
            st.session_state.user_data,
            st.session_state.selected_conditions,
            pain_scores
        )
        
        st.info(f"📋 현재 당신의 상담 결과 **{analysis_summary}** 의 상태가 의심되어 다음과 같은 운동 루틴을 추천 드립니다.")
        st.success(f"🎯 **AI 추천 운동 목적**: {exercise_purpose}")
        
        # 설문 기반 루틴 생성
        routine = create_personalized_exercise_routine(
            st.session_state.user_data,
            st.session_state.selected_conditions,
            pain_scores,
            exercise_schedule,
            exercise_purpose
        )
        
        if not routine:
            st.error("루틴 생성에 실패했습니다. 설문 데이터를 확인해주세요.")
            return
        
        # 주간 루틴 요약 표시
        st.markdown("---")
        st.subheader("📊 주간 운동 루틴 요약")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🗓️ 운동 일수", f"{routine['운동_일수']}일")
        with col2:
            st.metric("⏰ 주간 총 시간", f"{routine['총_주간시간']}분")
        with col3:
            st.metric("⭐ 난이도", exercise_schedule.get('difficulty_level', '초급자'))
        with col4:
            avg_daily = int(routine['총_주간시간'] / routine['운동_일수']) if routine['운동_일수'] > 0 else 0
            st.metric("📅 일일 평균", f"{avg_daily}분")
        
        # 요일별 상세 루틴
        st.markdown("---")
        st.subheader("📅 요일별 맞춤 운동 루틴")
        
        weekly_routine = routine["주간_루틴"]
        
        for day, daily_routine in weekly_routine.items():
            with st.expander(f"📅 {day} - {daily_routine['총_시간']}분 루틴"):
                # 시간 배분 표시
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔥 워밍업", f"{daily_routine['워밍업_시간']}분")
                with col2:
                    st.metric("🎬 운동 영상", f"{daily_routine['영상_시간']}분")
                with col3:
                    st.metric("🧘‍♀️ 스트레칭", f"{daily_routine['스트레칭_시간']}분")
                
                # 1. 워밍업
                st.markdown("### 🔥 워밍업 단계")
                st.markdown(f"**시간**: {daily_routine['워밍업_시간']}분")
                st.markdown("""
                **동작**:
                - 목, 어깨 돌리기 (각 방향 10회씩)
                - 팔 벌려 크게 원 그리기 (앞뒤로 각 10회)
                - 제자리에서 가볍게 몸 흔들기
                - 심호흡 3회 (코로 들이마시고 입으로 내뱉기)
                """)
                
                # 2. 메인 운동 영상
                st.markdown("### 🎬 메인 운동 - 추천 영상")
                st.markdown(f"**목표 시간**: {daily_routine['영상_시간']}분")
                
                selected_videos = daily_routine.get('선택된_영상', [])
                if selected_videos:
                    target_time = daily_routine['영상_시간']
                    
                    # 반복 횟수 계산
                    repetition_result = calculate_video_repetitions(selected_videos, target_time)
                    
                    if repetition_result['repetition_plan']:
                        # 영상 및 반복 횟수 표시
                        repetition_plan = repetition_result['repetition_plan']
                        total_planned_time = repetition_result['total_planned_minutes']
                        achievement_rate = repetition_result['achievement_rate']
                        
                        for i, plan in enumerate(repetition_plan, 1):
                            video = plan['video']
                            repetitions = plan['repetitions']
                            video_duration = plan['duration_minutes']
                            total_minutes = plan['total_minutes']
                            
                            # 하이퍼링크로만 표시 (썸네일 없음)
                            st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                            duration = get_video_duration_display(video)
                            channel = video.get('channel_name', '알 수 없음')
                            st.caption(f"📺 {channel} | ⏱️ {duration} | 🎯 난이도: {daily_routine['난이도']}")
                            
                            # 반복 횟수 안내
                            if repetitions > 1:
                                st.info(f"🔁 **{repetitions}회 반복** (총 {total_minutes:.1f}분)")
                            else:
                                st.info(f"🔁 **1회** (총 {total_minutes:.1f}분)")
                        
                        # 총 계획 시간 표시
                        st.success(f"✅ 총 계획 시간: {total_planned_time:.1f}분 / 목표: {target_time}분 ({achievement_rate:.1f}% 달성)")
                        
                        # 반복 안내 메시지
                        st.markdown("---")
                        st.markdown("### 📋 운동 실행 안내")
                        st.markdown("**각 영상을 다음과 같이 반복해주세요:**")
                        for i, plan in enumerate(repetition_plan, 1):
                            video_title = plan['video'].get('title', '제목 없음')
                            repetitions = plan['repetitions']
                            if repetitions > 1:
                                st.markdown(f"- **{i}번 영상**: {repetitions}회 반복")
                            else:
                                st.markdown(f"- **{i}번 영상**: 1회 실시")
                    else:
                        # 기본 표시 (반복 계산 실패 시)
                        total_video_time = 0
                        for i, video in enumerate(selected_videos, 1):
                            video_minutes = parse_duration_to_minutes(video)
                            total_video_time += video_minutes
                            # 하이퍼링크로만 표시 (썸네일 없음)
                            st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                            duration = get_video_duration_display(video)
                            channel = video.get('channel_name', '알 수 없음')
                            st.caption(f"📺 {channel} | ⏱️ {duration} | 🎯 난이도: {daily_routine['난이도']}")
                        
                        st.success(f"✅ 총 영상 시간: {total_video_time:.1f}분 / 목표: {target_time}분")
                else:
                    st.warning("🔍 해당 날짜에 적합한 영상을 찾을 수 없습니다.")
                
                # 3. 맞춤 스트레칭
                st.markdown("### 🧘‍♀️ 맞춤 스트레칭")
                st.markdown(f"**시간**: {daily_routine['스트레칭_시간']}분")
                
                condition_stretches = daily_routine.get('맞춤_스트레칭', [])
                if condition_stretches:
                    for stretch in condition_stretches:
                        st.markdown(f"**• {stretch['부위']}**: {stretch['동작']}")
                        st.markdown(f"  - ⏱️ {stretch['시간']} | 🔁 {stretch['횟수']} | ⚠️ {stretch['주의']}")
                        st.markdown("")
                
                st.markdown("---")
        
        # 상세 스트레칭 가이드
        st.markdown("---")
        st.subheader("📖 상세 스트레칭 가이드")
        
        stretching_guide = routine["스트레칭_가이드"]
        for stretch_name, guide in stretching_guide.items():
            with st.expander(f"📋 {stretch_name} 상세 방법"):
                st.markdown(f"**🧍 기본 자세**: {guide['자세']}")
                st.markdown("**📝 실시 방법**:")
                for method in guide['방법']:
                    st.markdown(f"   - {method}")
                st.markdown(f"**⚠️ 주의사항**: {guide['주의사항']}")
                st.markdown(f"**✨ 효과**: {guide['효과']}")
        
        # 루틴 완료 버튼
        st.markdown("---")
        if st.button("✅ 맞춤 루틴 확인 완료 - 다음 단계로", key="routine_complete", type="primary"):
            st.session_state.steps_completed[4] = True
            st.session_state.current_step = 5
            st.session_state.next_menu = "휴식 알리미 설정"
            st.success("✅ 맞춤형 운동 루틴이 완료되었습니다!")
            st.rerun()
    
    with tab4:
        st.subheader("🛒 맞춤 제품 추천")
        
        # AI 추천 운동 목적 확인
        if not st.session_state.get('final_exercise_purpose'):
            if not st.session_state.get('ai_recommended_purpose'):
                st.warning("❗ 먼저 '전문 AI와 상담하기' 탭에서 상담을 진행해주세요.")
                return
        
        # 개인화된 제품 추천만 표시
        pain_scores = st.session_state.user_data.get('pain_scores', {})
        try:
            show_personalized_product_recommendation(
                st.session_state.user_data,
                st.session_state.selected_conditions,
                pain_scores
            )
        except Exception as e:
            st.info("💡 제품 추천 기능을 준비 중입니다.")
        
        # 제품 추천 완료 버튼
        st.markdown("---")
        if st.button("✅ 맞춤 제품 확인 완료 - 다음 단계로", key="product_complete", type="primary"):
            st.session_state.steps_completed[4] = True
            st.session_state.current_step = 5
            st.session_state.next_menu = "휴식 알리미 설정"
            st.success("✅ 맞춤 제품 추천이 완료되었습니다!")
            st.rerun()

def show_notification_setup():
    st.header("휴식 알리미 설정")
    
    # 개선된 진행률 시각화 - 6단계로 수정
    steps = ["증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정"]
    completed_steps = sum(st.session_state.steps_completed[:6])
    
    # 진행률 표시 개선
    st.markdown("### 진행 상황")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        progress_percentage = (completed_steps / len(steps)) * 100
        st.progress(progress_percentage / 100)
    with col2:
        st.metric("완료 단계", f"{completed_steps}/{len(steps)}")
    with col3:
        st.metric("진행률", f"{progress_percentage:.0f}%")
    
    st.markdown("---")
    
    # 기존에 입력된 이메일 정보 가져오기
    user_email = st.session_state.user_data.get('email', '')
    
    if not user_email:
        st.warning("📧 이메일 주소가 입력되지 않았습니다. '개인정보 입력' 단계에서 이메일을 입력해주세요.")
        st.info("💡 이메일 주소는 운동 알림을 받기 위해 필요합니다.")
        return
    
    st.info(f"📧 설정된 이메일: **{user_email}**")
    
    # 자동 메일 스케줄러 상태 표시
    if EMAIL_SCHEDULER_AVAILABLE:
        scheduler_status = get_scheduler_status()
        st.markdown("---")
        st.subheader("📧 자동 메일 스케줄러 상태")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if scheduler_status['running']:
                st.success("🟢 실행 중")
            else:
                st.info("🔵 중지됨")
        with col2:
            st.metric("발송 횟수", f"{scheduler_status['email_count']}회")
        with col3:
            if scheduler_status['last_email_time']:
                st.caption(f"마지막 발송: {scheduler_status['last_email_time']}")
            else:
                st.caption("아직 발송 안됨")
    
    st.markdown("---")
    # 알림 방식 선택
    st.subheader("🔔 알림 방식 선택")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📧 자동 메일 알림 (NEW)")
        st.markdown("- Streamlit 종료 후에도 백그라운드에서 자동 실행")
        st.markdown("- 설정한 시간 간격으로 자동 발송")
        st.markdown("- 근무 시간 내에만 발송")
        use_auto_scheduler = st.checkbox("자동 메일 스케줄러 사용", value=True)
    
    with col2:
        st.markdown("#### 🔔 기존 알림 방식")
        st.markdown("- 이메일 및 Slack 즉시 알림")
        st.markdown("- 별도 스케줄러 프로그램 실행 필요")
        use_old_notification = st.checkbox("기존 알림 방식 사용", value=False)
    
    notification_type = "이메일 (Gmail)"
    slack_webhook = ""
    
    if use_old_notification:
        notification_type = st.selectbox("알림 방식", ["이메일 (Gmail)", "Slack", "둘 다"])
        if notification_type in ["Slack", "둘 다"]:
            st.subheader("💬 Slack 설정")
            slack_webhook = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/services/...")
    
    st.markdown("---")
    st.subheader("⏰ 메일 발송 시간 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        work_start = st.time_input("근무 시작 시간", value=datetime.strptime("09:00", "%H:%M").time())
        work_end = st.time_input("근무 종료 시간", value=datetime.strptime("18:00", "%H:%M").time())
        work_days_only = st.checkbox("평일에만 발송", value=True)
    with col2:
        work_intensity = st.session_state.user_data.get('work_intensity', '보통')
        
        if use_auto_scheduler:
            st.markdown("#### 5분 단위 발송 간격")
            interval_options = list(range(5, 60, 5))  # 5분부터 55분까지 5분 단위
            interval_index = interval_options.index(30) if 30 in interval_options else 5  # 기본값 30분
            interval_minutes = st.selectbox("메일 발송 간격 (분)", interval_options, index=interval_index)
            st.info(f"💡 {interval_minutes}분마다 메일을 발송합니다")
        else:
            st.markdown("#### 분 단위 휴식 간격")  
            rest_interval = calculate_rest_time(work_intensity)
            st.info(f"🎯 권장 휴식 간격: {rest_interval}분 (작업 강도: {work_intensity})")
            custom_interval = st.number_input("휴식 간격 조정 (분)", min_value=15, max_value=120, value=rest_interval, step=5)
    
    # 알림 내용 미리보기
    st.markdown("---")
    st.subheader("📋 알림 미리보기")
    
    if use_auto_scheduler:
        st.markdown(f"""
        **📧 받는 사람:** {user_email}  
        **⏰ 발송 시간:** {work_start.strftime('%H:%M')} ~ {work_end.strftime('%H:%M')}  
        **📅 발송 요일:** {'평일만' if work_days_only else '매일'}  
        **🔄 발송 간격:** {interval_minutes}분마다  
        **💡 알림 내용:** 개인 맞춤 운동 루틴 및 스트레칭 가이드  
        **🔧 특징:** Streamlit 종료 후에도 백그라운드에서 자동 실행
        """)
    else:
        st.markdown(f"""
        **📧 받는 사람:** {user_email}  
        **⏰ 알림 시간:** {work_start.strftime('%H:%M')} ~ {work_end.strftime('%H:%M')}  
        **🔄 알림 간격:** {custom_interval}분마다  
        **💡 알림 내용:** 개인 맞춤 운동 루틴 및 스트레칭 가이드
        """)
    
    # 자동 스케줄러 제어 버튼들
    if EMAIL_SCHEDULER_AVAILABLE and use_auto_scheduler:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 자동 스케줄러 시작", type="primary"):
                # 설정 업데이트
                scheduler_config_updated = update_scheduler_config(
                    enabled=True,
                    recipient_email=user_email,
                    send_time=work_start.strftime('%H:%M'),
                    interval_minutes=interval_minutes
                )
                
                if scheduler_config_updated:
                    success = start_email_scheduler()
                    if success:
                        st.success("✅ 자동 메일 스케줄러가 시작되었습니다!")
                        st.success(f"📧 {user_email}로 {interval_minutes}분마다 자동으로 메일을 발송합니다!")
                        st.session_state.steps_completed[5] = True
                        st.rerun()
                    else:
                        st.error("❌ 스케줄러 시작에 실패했습니다.")
                else:
                    st.error("❌ 스케줄러 설정 업데이트에 실패했습니다.")
        
        with col2:
            if st.button("⏸️ 스케줄러 중지", type="secondary"):
                success = stop_email_scheduler()
                if success:
                    st.success("✅ 자동 메일 스케줄러가 중지되었습니다.")
                    st.rerun()
                else:
                    st.error("❌ 스케줄러 중지에 실패했습니다.")
        
        with col3:
            if st.button("🔄 상태 새로고침"):
                st.rerun()
    
    # 기존 알림 방식 활성화 버튼
    elif use_old_notification and st.button("🚀 기존 알리미 활성화", type="primary"):
        # 설정 검증
        valid_config = True
        
        if notification_type in ["이메일 (Gmail)", "둘 다"]:
            from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD
            if not GMAIL_EMAIL or not GMAIL_APP_PASSWORD:
                st.error("❌ Gmail 설정이 완료되지 않았습니다. .env 파일의 GMAIL_EMAIL과 GMAIL_APP_PASSWORD를 확인해주세요.")
                valid_config = False
            else:
                # 테스트 이메일 발송 (시간 정보 포함)
                if send_test_email(GMAIL_EMAIL, GMAIL_APP_PASSWORD, user_email, 
                                 work_start.strftime("%H:%M"), work_end.strftime("%H:%M"), custom_interval):
                    st.success("✅ 이메일 알림 테스트 성공!")
                else:
                    valid_config = False
        
        if notification_type in ["Slack", "둘 다"]:
            if not slack_webhook:
                st.error("❌ Slack Webhook URL을 입력해주세요.")
                valid_config = False
            else:
                # 테스트 슬랙 메시지 발송 (시간 정보 포함)
                if send_test_slack(slack_webhook, work_start.strftime("%H:%M"), work_end.strftime("%H:%M"), custom_interval):
                    st.success("✅ Slack 알림 테스트 성공!")
                else:
                    valid_config = False
        
        if valid_config:
            notification_config = {
                "type": notification_type, 
                "email": user_email,
                "slack_webhook": slack_webhook if slack_webhook else None, 
                "work_start": work_start.strftime("%H:%M"), 
                "work_end": work_end.strftime("%H:%M"), 
                "interval": custom_interval, 
                "user_data": st.session_state.user_data,
                "conditions": st.session_state.selected_conditions,
                "pain_scores": st.session_state.user_data.get('pain_scores', {}),
                "created_at": datetime.now().isoformat()
            }
            
            try:
                with open("notification_config.json", "w", encoding="utf-8") as f:
                    json.dump(notification_config, f, ensure_ascii=False, indent=2, default=str)
                
                # 최종 고객 데이터 저장
                save_customer_data(
                    user_email,
                    st.session_state.user_data,
                    st.session_state.selected_conditions,
                    st.session_state.user_data.get('pain_scores', {})
                )
                
                st.success(f"✅ 기존 알리미가 설정되었습니다!")
                st.success(f"📧 {user_email}로 {custom_interval}분마다 맞춤 운동 알림을 보내드립니다!")
                st.info("💡 별도의 스케줄러 프로그램을 실행해야 알림이 발송됩니다.")
                st.session_state.steps_completed[5] = True  # 6번째 단계 완료 (0부터 시작하므로 5)
            except Exception as e:
                st.error(f"❌ 설정 저장 중 오류가 발생했습니다: {str(e)}")
    
    # 자동 스케줄러가 사용 불가능한 경우 안내
    elif not EMAIL_SCHEDULER_AVAILABLE:
        st.warning("❌ 자동 메일 스케줄러 모듈을 로드할 수 없습니다.")
        st.info("💡 기존 알림 방식을 사용하거나 email_scheduler.py 파일을 확인해주세요.")
    
    if st.session_state.steps_completed[5]:
        st.success("🎉 **모든 설정이 완료되었습니다!**")
        st.markdown("---")
        if st.button("📊 운동기록 확인하기", type="primary", key="go_to_exercise_management"):
            st.session_state.menu_selection = "운동 관리"
            st.rerun()

def main():
    st.title("💻 직장인 근무 환경 개선을 위한 맞춤형 운동 관리 시스템")
    st.markdown("---")
    
    options = ["홈", "증상 선택", "개인정보 입력", "작업환경 평가", "개인 운동 설문", "운동 추천", "휴식 알리미 설정","운동 관리"]
    
    if st.session_state.next_menu:
        st.session_state.menu_selection = st.session_state.next_menu
        st.session_state.next_menu = None
    
    try:
        current_index = options.index(st.session_state.menu_selection)
    except ValueError:
        current_index = 0
        st.session_state.menu_selection = options[0]
    
    menu = st.sidebar.selectbox("메뉴 선택", options, index=current_index)
    
    if menu != st.session_state.menu_selection:
        st.session_state.menu_selection = menu
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 시스템 상태")
    
    # YouTube 검색 상태
    if YOUTUBE_SEARCH_AVAILABLE and os.getenv("YOUTUBE_API_KEY"):
        st.sidebar.success("✅ YouTube 검색 활성화")
    else:
        st.sidebar.error("❌ YouTube 검색 비활성화")
    
    # AI 추천 상태
    if GEMINI_API_KEY and GEMINI_AVAILABLE:
        st.sidebar.success("✅ AI 추천 활성화")
    else:
        st.sidebar.error("❌ AI 추천 비활성화")
    
    # 데이터 저장 상태 (Google Sheets)
    spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
    credentials_exists = os.path.exists("credentials.json")
    if spreadsheet_id and credentials_exists and GSPREAD_AVAILABLE:
        st.sidebar.success("✅ 데이터 저장 활성화")
    else:
        st.sidebar.warning("⚠️ 데이터 저장 비활성화")
    
    # 광고/제품 추천 상태
    if ADS_AVAILABLE:
        st.sidebar.success("✅ 광고/제품 추천 활성화")
    else:
        st.sidebar.warning("⚠️ 광고/제품 추천 비활성화")
    
    # 자동 메일 스케줄러 상태
    if EMAIL_SCHEDULER_AVAILABLE:
        scheduler_status = get_scheduler_status()
        if scheduler_status['running']:
            st.sidebar.success("✅ 자동 메일 스케줄러 실행 중")
            st.sidebar.caption(f"📧 발송 횟수: {scheduler_status['email_count']}회")
            if scheduler_status['last_email_time']:
                st.sidebar.caption(f"⏰ 마지막 발송: {scheduler_status['last_email_time']}")
        else:
            st.sidebar.info("⏸️ 자동 메일 스케줄러 중지됨")
    else:
        st.sidebar.error("❌ 메일 스케줄러 비활성화")
    
    completed_steps = sum(st.session_state.steps_completed[:6])  # 6단계까지만 계산
    progress_percentage = (completed_steps / 6) * 100
    st.sidebar.progress(progress_percentage / 100)
    st.sidebar.caption(f"{completed_steps}/6 단계 완료 ({progress_percentage:.0f}%)")
    
    if menu == "홈":
        show_home()
    elif menu == "증상 선택":
        show_condition_selection()
    elif menu == "개인정보 입력":
        show_personal_info()
    elif menu == "작업환경 평가":
        show_work_environment()
    elif menu == "개인 운동 설문":
        show_exercise_survey()
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
            # 개인정보 입력에서 저장된 이메일 확인
            user_email = st.session_state.user_data.get('email') if 'user_data' in st.session_state else None
            if hasattr(em6, "show_integrated_dashboard"):
                em6.show_integrated_dashboard(user_email)
            else:
                st.error("exercise_manager6.py에 'show_integrated_dashboard' 함수가 없습니다.")
        except Exception as e:
            st.error(f"운동 관리 모듈 로드 실패: {e}")

if __name__ == "__main__":
    main()
