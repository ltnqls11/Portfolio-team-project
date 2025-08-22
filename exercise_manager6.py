# 구글시트로 관리/db저장돼서 나오도록
# exercise_manager_updated.py

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import random
import altair as alt
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# Google Sheets 라이브러리 추가
try:
import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    st.warning("Google Sheets 연동을 사용하려면 'pip install -r requirements.txt'를 실행하세요.")

# --- Google Sheets 설정 (app_sb_sr.py와 동일하게 설정) ---
GOOGLE_SHEETS_CREDENTIALS = "credentials.json"  # 서비스 계정 키 파일
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

# Google Sheets 파일 존재 여부 확인
CREDENTIALS_EXISTS = os.path.exists(GOOGLE_SHEETS_CREDENTIALS)

def init_google_sheets():
    """Google Sheets 초기화 (app_sb_sr.py와 동일한 함수)"""
    try:
        if not GSPREAD_AVAILABLE:
            return None
            
        if not CREDENTIALS_EXISTS:
            return None
            
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS, 
            scopes=scope
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        return None

# Google Sheets 연결 상태 확인
try:
    client = init_google_sheets()
    if client and SPREADSHEET_ID:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet("vdt_data")  # app_sb_sr.py에서 사용하는 시트명
    GOOGLE_SHEETS_ENABLED = True
        # 연결 성공 메시지는 main 함수에서만 표시
    else:
        GOOGLE_SHEETS_ENABLED = False
        # 연결 실패 메시지는 main 함수에서만 표시
except Exception as e:
    GOOGLE_SHEETS_ENABLED = False
    # 연결 오류 메시지는 main 함수에서만 표시

# ====================================================================
# Data and Helper Functions
# ====================================================================

# VDT 증후군 증상 데이터 (app_sb_sr.py와 일치하도록 수정)
VDT_SYMPTOMS = {
    "거북목": {
        "증상": ["목 통증", "어깨 결림", "두통", "팔 저림"],
        "원인": ["잘못된 자세", "장시간 고개 숙임"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "목 스트레칭", "purpose": "목 근육 이완 및 자세 교정", "method": "고개를 천천히 좌우로 돌리고, 앞뒤로 숙이기", "reps": "각 방향 10초씩 3회", "caution": "급격한 움직임 금지"},
                {"name": "어깨 으쓱하기", "purpose": "어깨 긴장 완화", "method": "어깨를 귀 쪽으로 올렸다가 천천히 내리기", "reps": "10회 3세트", "caution": "천천히 부드럽게 실시"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "목 근력 강화", "purpose": "목 주변 근육 강화", "method": "손으로 이마를 누르며 목으로 저항하기", "reps": "10초씩 5회", "caution": "과도한 힘 사용 금지"}
            ],
            "재활 (통증감소)": [
                {"name": "온찜질 후 스트레칭", "purpose": "통증 완화 및 혈액순환 개선", "method": "따뜻한 수건으로 목을 찜질 후 가벼운 스트레칭", "reps": "15분 찜질 후 스트레칭", "caution": "통증이 심할 때는 중단"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "거북목 스트레칭 5분", "url": "https://www.youtube.com/watch?v=F0B6b9j8yJ8"},
            {"title": "일자목 스트레칭", "url": "https://www.youtube.com/watch?v=1F_454p-jR4"}
        ]
    },
    "라운드숄더": {
        "증상": ["굽은 등", "가슴 통증", "호흡 곤란"],
        "원인": ["장시간 컴퓨터 사용", "잘못된 자세"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "가슴 스트레칭", "purpose": "가슴 근육 이완으로 어깨 교정", "method": "벽에 손을 대고 몸을 앞으로 기울이기", "reps": "30초씩 3회", "caution": "무리하지 않는 범위에서"},
                {"name": "어깨날개 모으기", "purpose": "등 근육 강화", "method": "양쪽 어깨날개를 등 중앙으로 모으기", "reps": "10초씩 10회", "caution": "어깨를 올리지 말고 실시"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "등 근력 강화", "purpose": "등 근육 강화로 자세 개선", "method": "양팔을 뒤로 당기며 어깨날개 모으기", "reps": "15회 3세트", "caution": "천천히 정확한 자세로"}
            ],
            "재활 (통증감소)": [
                {"name": "부드러운 어깨 회전", "purpose": "어깨 관절 가동성 개선", "method": "어깨를 천천히 앞뒤로 회전시키기", "reps": "각 방향 10회씩", "caution": "통증 범위 내에서만"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "라운드숄더 교정 운동", "url": "https://www.youtube.com/watch?v=4dJ4K1z7n5o"}
        ]
    },
    "허리디스크": {
        "증상": ["허리 통증", "다리 저림", "감각 이상"],
        "원인": ["장시간 앉아있기", "잘못된 자세", "무거운 물건 들기"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "고양이-소 자세", "purpose": "허리 근육 이완", "method": "무릎을 꿇고 손바닥을 바닥에 대고 허리를 굽혔다 폈다 합니다.", "reps": "10회씩 3세트", "caution": "천천히 부드럽게"},
                {"name": "누워서 다리 올리기", "purpose": "허리 곡선 정상화", "method": "바로 누워 한쪽 다리를 천천히 들어올립니다.", "reps": "각 다리 10회", "caution": "통증이 없는 범위에서"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "코어 강화", "purpose": "허리 지지 근육 강화", "method": "배에 힘을 주고 10초간 유지", "reps": "10초씩 10회", "caution": "호흡을 멈추지 말 것"}
            ],
            "재활 (통증감소)": [
                {"name": "무릎 가슴으로 당기기", "purpose": "허리 근육 이완", "method": "앉아서 한쪽 무릎을 가슴으로 당기기", "reps": "각 다리 30초씩", "caution": "통증이 있으면 중단"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "허리디스크 예방 스트레칭", "url": "https://www.youtube.com/watch?v=eYk2S9f2gI4"}
        ]
    },
    "손목터널증후군_왼쪽": {
        "증상": ["왼쪽 손목 통증", "왼쪽 손가락 저림", "왼쪽 손 근력 약화"],
        "원인": ["반복적인 손목 사용", "부자연스러운 손목 각도"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "왼쪽 손목 스트레칭", "purpose": "왼쪽 손목 근육 이완", "method": "왼쪽 손목을 위아래로 구부리기", "reps": "10회씩 3세트", "caution": "통증 시 중단"},
                {"name": "왼쪽 손가락 펴기", "purpose": "왼쪽 손가락 근육 이완", "method": "왼쪽 손가락을 쭉 펴고 5초간 유지", "reps": "10회", "caution": "부드럽게 실시"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "왼쪽 손목 근력 강화", "purpose": "왼쪽 손목 주변 근육 강화", "method": "가벼운 무게로 왼쪽 손목 굽히기 운동", "reps": "15회 2세트", "caution": "무리하지 말 것"}
            ],
            "재활 (통증감소)": [
                {"name": "왼쪽 신경 활주 운동", "purpose": "왼쪽 신경 압박 완화", "method": "왼쪽 손목과 손가락을 천천히 펴고 구부리기", "reps": "10회씩 하루 3번", "caution": "저림이 심해지면 중단"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "왼쪽 손목 통증 스트레칭", "url": "https://www.youtube.com/watch?v=9D_r_z0i9pI"},
            {"title": "왼쪽 손목터널 증후군 예방", "url": "https://www.youtube.com/watch?v=G96q6sL3FhY"}
        ]
    },
    "손목터널증후군_오른쪽": {
        "증상": ["오른쪽 손목 통증", "오른쪽 손가락 저림", "오른쪽 손 근력 약화"],
        "원인": ["반복적인 손목 사용", "부자연스러운 손목 각도"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "오른쪽 손목 스트레칭", "purpose": "오른쪽 손목 근육 이완", "method": "오른쪽 손목을 위아래로 구부리기", "reps": "10회씩 3세트", "caution": "통증 시 중단"},
                {"name": "오른쪽 손가락 펴기", "purpose": "오른쪽 손가락 근육 이완", "method": "오른쪽 손가락을 쭉 펴고 5초간 유지", "reps": "10회", "caution": "부드럽게 실시"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "오른쪽 손목 근력 강화", "purpose": "오른쪽 손목 주변 근육 강화", "method": "가벼운 무게로 오른쪽 손목 굽히기 운동", "reps": "15회 2세트", "caution": "무리하지 말 것"}
            ],
            "재활 (통증감소)": [
                {"name": "오른쪽 신경 활주 운동", "purpose": "오른쪽 신경 압박 완화", "method": "오른쪽 손목과 손가락을 천천히 펴고 구부리기", "reps": "10회씩 하루 3번", "caution": "저림이 심해지면 중단"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "오른쪽 손목 통증 스트레칭", "url": "https://www.youtube.com/watch?v=9D_r_z0i9pI"},
            {"title": "오른쪽 손목터널 증후군 예방", "url": "https://www.youtube.com/watch?v=G96q6sL3FhY"}
        ]
    }
}

def get_exercises_for_condition(condition, purpose="예방 (자세교정)"):
    """
    특정 증상에 대한 운동 추천 목록을 반환합니다.
    """
    return VDT_SYMPTOMS.get(condition, {}).get("운동_추천", {}).get(purpose, [])

def get_exercise_videos(condition):
    """
    특정 증상에 대한 YouTube 영상 목록을 반환합니다.
    """
    videos = VDT_SYMPTOMS.get(condition, {}).get("유튜브_영상_링크", [])
    if not videos:
        return []

    day_of_year = date.today().timetuple().tm_yday
    random.seed(day_of_year)
    
    return [random.choice(videos)]

# ====================================================================
# Google Sheets 로드 및 저장 함수 (app_sb_sr.py의 vdt_data 시트에서 데이터 가져오기)
# ====================================================================

def load_data_from_google_sheets():
    """Google Sheets의 vdt_data 시트에서 모든 데이터를 불러와서 DataFrame으로 반환합니다."""
    if not GOOGLE_SHEETS_ENABLED:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        all_data = worksheet.get_all_records()
        df = pd.DataFrame(all_data)

        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # app_sb_sr.py에서 저장된 데이터 구조에 맞게 필터링
        # data_type별로 데이터 분리
        ai_data = df[df['data_type'] == 'ai_recommendation'].copy()
        exercise_data = df[df['data_type'] == 'exercise_log'].copy()
        pain_data = df[df['data_type'] == 'pain_data'].copy()
        point_data = df[df['data_type'] == 'point_data'].copy()
        
        # 운동 로그 데이터 처리
        exercise_df = pd.DataFrame()
        if not exercise_data.empty:
            # 필요한 컬럼이 있는지 확인
            required_cols = ['user_id', 'date', 'completed_count']
            available_cols = [col for col in required_cols if col in exercise_data.columns]
            if len(available_cols) >= 2:  # 최소 user_id와 date는 있어야 함
                exercise_df = exercise_data[available_cols].copy()
                if 'date' in exercise_df.columns:
                    exercise_df['date'] = pd.to_datetime(exercise_df['date'])
                if 'completed_count' not in exercise_df.columns:
                    exercise_df['completed_count'] = 0  # 기본값 설정
                else:
                    # 안전한 정수 변환
                    exercise_df['completed_count'] = pd.to_numeric(exercise_df['completed_count'], errors='coerce').fillna(0)
        
        # 통증 데이터 처리
        pain_df = pd.DataFrame()
        if not pain_data.empty:
            # 필요한 컬럼이 있는지 확인
            required_cols = ['user_id', 'date', 'pain_level']
            available_cols = [col for col in required_cols if col in pain_data.columns]
            if len(available_cols) >= 2:  # 최소 user_id와 date는 있어야 함
                pain_df = pain_data[available_cols].copy()
                if 'date' in pain_df.columns:
                    pain_df['date'] = pd.to_datetime(pain_df['date'])
                if 'pain_level' not in pain_df.columns:
                    pain_df['pain_level'] = 5  # 기본값 설정
                else:
                    # 안전한 숫자 변환
                    pain_df['pain_level'] = pd.to_numeric(pain_df['pain_level'], errors='coerce').fillna(5)
        
        # 포인트 데이터 처리
        point_df = pd.DataFrame()
        if not point_data.empty:
            # 필요한 컬럼이 있는지 확인
            required_cols = ['user_id', 'date', 'points_gained']
            available_cols = [col for col in required_cols if col in point_data.columns]
            if len(available_cols) >= 2:  # 최소 user_id와 date는 있어야 함
                point_df = point_data[available_cols].copy()
                if 'date' in point_df.columns:
                    point_df['date'] = pd.to_datetime(point_df['date'])
                if 'points_gained' not in point_df.columns:
                    point_df['points_gained'] = 0  # 기본값 설정
                else:
                    # 안전한 정수 변환
                    point_df['points_gained'] = pd.to_numeric(point_df['points_gained'], errors='coerce').fillna(0)
        
        # AI 추천 데이터가 있지만 다른 데이터가 없는 경우, 기본 데이터 생성
        if not ai_data.empty and exercise_df.empty and pain_df.empty and point_df.empty:
            st.info("AI 추천 데이터는 있지만 운동 기록이 없습니다. 운동을 시작해보세요!")
            
            # AI 데이터에서 사용자 정보 추출하여 기본 데이터 생성
            ai_data['timestamp'] = pd.to_datetime(ai_data['timestamp'])
            latest_ai = ai_data.sort_values('timestamp').groupby('user_id').last().reset_index()
            
            # 기본 운동 데이터 생성
            exercise_df = latest_ai[['user_id', 'timestamp']].copy()
            exercise_df['date'] = exercise_df['timestamp'].dt.date.astype(str)
            exercise_df['completed_count'] = 0  # 아직 운동하지 않음
            
            # 기본 통증 데이터 생성 (pain_scores에서 추출)
            pain_df = latest_ai[['user_id', 'timestamp']].copy()
            pain_df['date'] = pain_df['timestamp'].dt.date.astype(str)
            
            # pain_scores 컬럼에서 실제 통증 수준 추출
            def extract_pain_level(pain_scores_str):
                try:
                    import json
                    if pd.isna(pain_scores_str) or pain_scores_str == '':
                        return 5
                    pain_scores = json.loads(str(pain_scores_str))
                    if pain_scores:
                        # 모든 통증 점수의 평균 계산 (안전한 변환)
                        values = []
                        for v in pain_scores.values():
                            try:
                                val = float(v)
                                if 0 <= val <= 10:  # 유효한 범위 확인
                                    values.append(val)
                            except (ValueError, TypeError):
                                continue
                        return round(sum(values) / len(values), 1) if values else 5
                    return 5
                except Exception:
                    return 5
            
            pain_df['pain_level'] = latest_ai['pain_scores'].apply(extract_pain_level)
            
            # 기본 포인트 데이터 생성
            point_df = latest_ai[['user_id', 'timestamp']].copy()
            point_df['date'] = point_df['timestamp'].dt.date.astype(str)
            point_df['points_gained'] = 0  # 아직 포인트 없음

        return exercise_df, pain_df, point_df

    except Exception as e:
        st.error(f"Google Sheets에서 데이터 로드 중 오류 발생: {e}")
        st.info("로컬 데이터로 대체하여 계속 진행합니다.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def save_to_google_sheets(data, data_type, user_id):
    """데이터를 Google Sheets의 vdt_data 시트에 저장합니다."""
    if not GOOGLE_SHEETS_ENABLED:
        st.error("Google Sheets가 비활성화되어 데이터를 저장할 수 없습니다.")
        return

    try:
        # app_sb_sr.py와 동일한 데이터 구조로 저장
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = str(date.today())

        # 운동 로그 데이터 구조
        if data_type == 'exercise_log':
            row_data = {
                'timestamp': timestamp,
                'user_id': user_id,
                'data_type': 'exercise_log',
                'date': today,
                'completed_count': data.get('completed_count', 0)
            }
        elif data_type == 'pain_data':
            row_data = {
                'timestamp': timestamp,
                'user_id': user_id,
                'data_type': 'pain_data',
                'date': today,
                'pain_level': data.get('pain_level', 0)
            }
        elif data_type == 'point_data':
            row_data = {
                'timestamp': timestamp,
                'user_id': user_id,
                'data_type': 'point_data',
                'date': today,
                'points_gained': data.get('points_gained', 0)
            }
        else:
            st.error(f"지원하지 않는 데이터 타입: {data_type}")
            return
        
        # 기존 헤더 확인
            headers = worksheet.get_all_values()[0]
        
        # 필요한 컬럼이 없으면 추가
        required_headers = ['timestamp', 'user_id', 'data_type', 'date']
        if data_type == 'exercise_log':
            required_headers.append('completed_count')
        elif data_type == 'pain_data':
            required_headers.append('pain_level')
        elif data_type == 'point_data':
            required_headers.append('points_gained')
        
        # 누락된 헤더 추가
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            # 누락된 헤더를 기존 헤더에 추가
            headers.extend(missing_headers)
            # 헤더 행 업데이트
            worksheet.update('A1', [headers])
        
        # 새 행 데이터를 헤더에 맞게 정렬
        new_row_list = [row_data.get(header, '') for header in headers]
        
        # 데이터 추가
            worksheet.append_row(new_row_list)
        st.success(f"{data_type} 데이터가 성공적으로 저장되었습니다.")
        
    except Exception as e:
        st.error(f"Google Sheets에 데이터 저장 중 오류 발생: {e}")

# ====================================================================
# 페이지 함수
# ====================================================================

def show_integrated_dashboard(user_id):
    """
    통합 대시보드 기능을 보여주는 페이지입니다.
    """
    st.header("💻 통합 건강 대시보드")
    st.markdown("오늘의 운동 루틴을 완료하고, 통증을 기록하며 건강을 관리하세요.")
    
    # Google Sheets 연결 상태 표시
    if GOOGLE_SHEETS_ENABLED:
        st.info("📊 Google Sheets와 연결되어 app_sb_sr.py의 데이터를 가져옵니다.")
    else:
        st.warning("⚠️ Google Sheets가 연결되지 않아 로컬 데이터만 사용합니다.")
        st.info("💡 Google Sheets 설정을 완료하면 app_sb_sr.py에서 저장한 AI 추천 데이터를 확인할 수 있습니다.")
    
    st.markdown("---")
    
    if 'selected_conditions' not in st.session_state:
        st.session_state.selected_conditions = []
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {}
    
    if 'total_points' not in st.session_state:
        st.session_state.total_points = 0
    if 'last_exercise_date' not in st.session_state:
        st.session_state.last_exercise_date = None
    if 'consecutive_days' not in st.session_state:
        st.session_state.consecutive_days = 0

    today_date = str(date.today())

    exercise_df, pain_df, point_df = load_data_from_google_sheets()

    if not point_df.empty:
        try:
            # 안전한 정수 변환
            point_df['points_gained'] = pd.to_numeric(point_df['points_gained'], errors='coerce').fillna(0)
            total_points = int(point_df['points_gained'].sum())
        st.session_state.total_points = total_points
        except Exception as e:
            st.warning(f"포인트 데이터 처리 중 오류: {e}")
            st.session_state.total_points = 0
    else:
        st.session_state.total_points = 0

    # ====================================================================
    # 포인트 및 챌린지 현황
    # ====================================================================
    st.subheader("🎉 나의 건강 목표")
    st.markdown(f"**사용자 ID:** {user_id}")
    st.markdown(f"**현재까지 누적 포인트:** **{st.session_state.total_points}** 점")
    st.markdown(f"**연속 운동일:** **{st.session_state.consecutive_days}** 일")
    st.markdown("---")

    # ====================================================================
    # 증상 선택 섹션 (app_sb_sr.py와 연동)
    # ====================================================================
    st.subheader("🔎 현재 겪고 있는 증상을 선택해주세요")
    
    # app_sb_sr.py에서 선택된 증상이 있으면 사용, 없으면 새로 선택
    if 'selected_conditions' in st.session_state and st.session_state.selected_conditions:
        # 선택된 증상이 VDT_SYMPTOMS에 있는지 확인
        valid_conditions = [c for c in st.session_state.selected_conditions if c in VDT_SYMPTOMS]
        if valid_conditions:
            st.success(f"이미 선택된 증상: {', '.join([c.replace('_', ' - ') for c in valid_conditions])}")
            selected_conditions = valid_conditions
        else:
            st.warning("이전에 선택된 증상이 유효하지 않습니다. 다시 선택해주세요.")
            selected_conditions = []
    else:
        selected_conditions = []
    
    # 증상 선택이 없거나 유효하지 않은 경우 새로 선택
    if not selected_conditions:
    symptom_options = list(VDT_SYMPTOMS.keys())
    selected_conditions = st.multiselect(
        "증상을 선택해주세요:",
        symptom_options,
            default=st.session_state.get('selected_conditions', [])
    )
    st.session_state.selected_conditions = selected_conditions
    
    st.markdown("---")

    # ====================================================================
    # 오늘의 루틴 섹션 (사용자가 선택한 증상에 따라 동적으로 생성)
    # ====================================================================
    st.subheader("🏃‍♂️ 오늘의 루틴")
    if not selected_conditions:
        st.info("먼저 위에서 증상을 하나 이상 선택해 주세요.")
    else:
        for condition in selected_conditions:
            # 증상이 VDT_SYMPTOMS에 있는지 확인
            if condition not in VDT_SYMPTOMS:
                st.warning(f"증상 '{condition}'에 대한 데이터가 없습니다.")
                continue
                
            st.markdown(f"**🔹 {condition}**")
            
            try:
            videos = get_exercise_videos(condition)
            if videos:
                st.markdown("**📹 오늘의 추천 영상:**")
                for video in videos:
                    st.video(video['url'])
                    video_key = f"completed_video_{today_date}_{video['title']}"
                    if video_key not in st.session_state.checkbox_states:
                        st.session_state.checkbox_states[video_key] = False
                    st.session_state.checkbox_states[video_key] = st.checkbox(
                        f"**{video['title']}** 영상 시청 완료",
                        value=st.session_state.checkbox_states[video_key],
                        key=video_key
                    )
            
            if "운동_추천" in VDT_SYMPTOMS[condition]:
                exercises = VDT_SYMPTOMS[condition]["운동_추천"]
                for purpose, exercise_list in exercises.items():
                    st.markdown(f"**✨ {purpose} 운동**")
                    for exercise in exercise_list:
                        unique_key = f"completed_exercise_{today_date}_{condition}_{exercise['name']}"
                        
                        if unique_key not in st.session_state.checkbox_states:
                            st.session_state.checkbox_states[unique_key] = False
                            
                        st.session_state.checkbox_states[unique_key] = st.checkbox(
                            f"**{exercise['name']}**",
                            value=st.session_state.checkbox_states[unique_key],
                            key=unique_key
                        )

                        st.markdown(
                            f"""
                            - **목적:** {exercise['purpose']}
                            - **방법:** {exercise['method']}
                            - **반복:** {exercise['reps']}
                            - **주의:** {exercise['caution']}
                            """
                        )
            
            st.markdown("---")
            except Exception as e:
                st.error(f"증상 '{condition}' 처리 중 오류가 발생했습니다: {e}")
                continue
            
    if st.button("💪 운동 완료 기록"):
        completed_exercises = []
        for key, value in st.session_state.checkbox_states.items():
            if value and key.startswith(f"completed_exercise_{today_date}"):
                completed_exercises.append(key)
        
        for key, value in st.session_state.checkbox_states.items():
            if value and key.startswith(f"completed_video_{today_date}"):
                completed_exercises.append(key)
        
        if completed_exercises:
            points_gained = len(completed_exercises) * 5
            st.success(f"운동 완료! 🎉 {points_gained} 포인트를 획득했습니다.")
            
            today = date.today()
            if st.session_state.last_exercise_date:
                try:
                    last_date = datetime.strptime(st.session_state.last_exercise_date, '%Y-%m-%d').date()
                    if last_date == today - timedelta(days=1):
                        st.session_state.consecutive_days = st.session_state.get('consecutive_days', 0) + 1
                        if st.session_state.consecutive_days >= 3:
                            st.balloons()
                            st.info(f"축하합니다! 🏆 {st.session_state.consecutive_days}일 연속 운동 챌린지 성공!")
                    elif last_date != today:
                        st.session_state.consecutive_days = 1
                except ValueError:
                    st.session_state.consecutive_days = 1
            else:
                st.session_state.consecutive_days = 1
            
            st.session_state.last_exercise_date = str(today)

            save_to_google_sheets({'completed_count': len(completed_exercises)}, 'exercise_log', user_id)
            save_to_google_sheets({'points_gained': points_gained}, 'point_data', user_id)
        else:
            st.warning("먼저 완료한 운동을 체크해주세요!")

    # ====================================================================
    # 통증 기록 섹션
    # ====================================================================
    st.subheader("🏥 나의 통증 기록하기")
    current_pain_level = st.slider(
        "오늘의 통증 점수 (0: 없음, 15: 심함)",
        0, 15, key="pain_slider"
    )
    if st.button("통증 기록 저장"):
        save_to_google_sheets({'pain_level': current_pain_level}, 'pain_data', user_id)
        st.success(f"통증 기록이 저장되었습니다.")
        save_to_google_sheets({'points_gained': 2}, 'point_data', user_id)

    st.markdown("---")

    # ====================================================================
    # AI 추천 데이터 표시 (app_sb_sr.py에서 저장된 데이터)
    # ====================================================================
    st.subheader("🤖 AI 추천 데이터")
    
    if not exercise_df.empty or not pain_df.empty:
        # AI 추천 데이터 로드
        try:
            all_data = worksheet.get_all_records()
            df = pd.DataFrame(all_data)
            ai_data = df[df['data_type'] == 'ai_recommendation'].copy()
            
            if not ai_data.empty:
                # 현재 사용자의 최신 AI 추천 데이터 표시
                user_ai_data = ai_data[ai_data['user_id'] == user_id]
                if not user_ai_data.empty:
                    latest_ai = user_ai_data.sort_values('timestamp').iloc[-1]
                else:
                    # 사용자별 데이터가 없으면 전체 데이터에서 최신 것 표시
                    latest_ai = ai_data.sort_values('timestamp').iloc[-1]
                    st.warning("현재 사용자의 AI 추천 데이터가 없어 전체 데이터를 표시합니다.")
                
                with st.expander("📋 최신 AI 운동 추천 보기"):
                    st.write("**추천 시각:**", latest_ai.get('timestamp', 'N/A'))
                    st.write("**선택된 증상:**", latest_ai.get('conditions', 'N/A'))
                    st.write("**운동 목적:**", latest_ai.get('exercise_purpose', 'N/A'))
                    
                    # AI 추천 내용 표시
                    ai_recommendation = latest_ai.get('ai_recommendation', '')
                    if ai_recommendation:
                        st.write("**AI 추천 내용:**")
                        st.text_area("추천 내용", ai_recommendation, height=200, disabled=True)
                    
                    # 사용자 정보 표시
                    st.write("**사용자 정보:**")
                    st.write(f"- 나이: {latest_ai.get('user_age', 'N/A')}세")
                    st.write(f"- 성별: {latest_ai.get('user_gender', 'N/A')}")
                    st.write(f"- 일일 작업시간: {latest_ai.get('work_hours', 'N/A')}시간")
                    st.write(f"- 작업 강도: {latest_ai.get('work_intensity', 'N/A')}")
                    st.write(f"- 작업환경 점수: {latest_ai.get('env_score', 'N/A')}/100점")
            else:
                st.info("AI 추천 데이터가 없습니다. '운동 추천' 메뉴에서 AI 추천을 받아보세요.")
        except Exception as e:
            st.error(f"AI 추천 데이터 로드 중 오류: {e}")
    else:
        st.info("먼저 운동을 완료하고 데이터를 생성해보세요.")

    st.markdown("---")

    # ====================================================================
    # 통증·운동 리포트 시각화
    # ====================================================================
    st.subheader("📈 통증·운동 리포트")
    
    # 간단한 데이터 상태 표시 (현재 사용자 + 날짜 기준 고유 일수)
    def count_unique_days_by_user(df: pd.DataFrame, user_id_value: str) -> int:
        try:
            if df.empty:
                return 0
            # 날짜 형 변환
            if 'date' in df.columns:
                df = df.copy()
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                # user_id가 날짜형 ID로 시작하는 행 포함 (예: user_YYYYMMDD_123456)
                mask = df['user_id'].astype(str).str.startswith(user_id_value)
                return df.loc[mask, 'date'].dt.date.nunique()
            return 0
        except Exception:
            return 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("운동 기록", f"{count_unique_days_by_user(exercise_df, user_id)}일")
    with col2:
        st.metric("통증 기록", f"{count_unique_days_by_user(pain_df, user_id)}일")
    with col3:
        st.metric("포인트 기록", f"{count_unique_days_by_user(point_df, user_id)}일")
    
    if not exercise_df.empty or not pain_df.empty:
        try:
            # 데이터가 있는 경우에만 처리
            if not exercise_df.empty:
        exercise_df['date'] = pd.to_datetime(exercise_df['date'])
                exercise_df['completed_count'] = pd.to_numeric(
                    exercise_df['completed_count'], errors='coerce'
                ).fillna(0)
            
            if not pain_df.empty:
        pain_df['date'] = pd.to_datetime(pain_df['date'])
                pain_df['pain_level'] = pd.to_numeric(
                    pain_df['pain_level'], errors='coerce'
                ).fillna(5)
            
            # 'user_id'에 따라 필터링 (날짜형 ID로 시작하는 행 포함)
            if not exercise_df.empty:
                mask_ex = exercise_df['user_id'].astype(str).str.startswith(user_id)
                user_exercise_df = exercise_df.loc[mask_ex].copy()
            else:
                user_exercise_df = pd.DataFrame()

            if not pain_df.empty:
                mask_pn = pain_df['user_id'].astype(str).str.startswith(user_id)
                user_pain_df = pain_df.loc[mask_pn].copy()
            else:
                user_pain_df = pd.DataFrame()
            
            # 데이터가 있는 경우에만 차트 생성
            if not user_exercise_df.empty or not user_pain_df.empty:
        # 날짜를 인덱스로 설정
                if not user_exercise_df.empty:
        user_exercise_df = user_exercise_df.set_index('date')
                if not user_pain_df.empty:
        user_pain_df = user_pain_df.set_index('date')
        
        # 두 데이터프레임의 날짜 인덱스를 통합하여 결합
                if not user_exercise_df.empty and not user_pain_df.empty:
        combined_index = user_exercise_df.index.union(user_pain_df.index)
                elif not user_exercise_df.empty:
                    combined_index = user_exercise_df.index
                else:
                    combined_index = user_pain_df.index
                
        combined_df = pd.DataFrame(index=combined_index)
        
        # join을 사용하여 데이터를 병합하고, 데이터가 없는 날짜는 0으로 채우기
                if not user_exercise_df.empty:
                    combined_df = combined_df.join(user_exercise_df[['completed_count']])
                else:
                    combined_df['completed_count'] = 0
                
                if not user_pain_df.empty:
                    combined_df = combined_df.join(user_pain_df[['pain_level']])
                else:
                    combined_df['pain_level'] = 5
                
                combined_df = combined_df.fillna({'completed_count': 0, 'pain_level': 5})
        combined_df = combined_df.reset_index()
        combined_df = combined_df.rename(columns={'index': 'date'})

        # Altair를 사용한 이중 축 차트 생성
        base = alt.Chart(combined_df).encode(
            alt.X('date:T', title='날짜')
        )
                
                # 안전한 최대값 계산
                max_count = max(combined_df['completed_count'].max(), 1)

        bar_chart = base.mark_bar(color='#26A69A').encode(
                    y=alt.Y(
                        'completed_count:Q',
                        title='운동 횟수',
                        axis=alt.Axis(labels=True, titleColor='#26A69A'),
                        scale=alt.Scale(domain=[0, max_count + 2])
                    )
        )
        
        line_chart = base.mark_line(color='#FF5722').encode(
                    y=alt.Y(
                        'pain_level:Q',
                        title='통증 점수',
                        axis=alt.Axis(labels=True, titleColor='#FF5722'),
                        scale=alt.Scale(domain=[0, 15])
                    )
        )

        point_chart = base.mark_point(
            color='#FF5722',
            size=100,
            filled=True,
        ).encode(
                    y=alt.Y(
                        'pain_level:Q',
                        title='통증 점수',
                        axis=alt.Axis(labels=True, titleColor='#FF5722'),
                        scale=alt.Scale(domain=[0, 15])
                    ),
                    tooltip=[
                        alt.Tooltip('date:T', title='날짜'),
                        alt.Tooltip('pain_level:Q', title='통증 점수')
                    ]
        )

        combined_chart = alt.layer(bar_chart, line_chart, point_chart).resolve_scale(
            y='independent'
        ).properties(
            title='운동 횟수와 통증 점수 변화'
        )
        
        st.altair_chart(combined_chart, use_container_width=True)
            else:
                st.info("현재 사용자의 운동/통증 기록이 없습니다.")
        except Exception as e:
            st.error(f"차트 생성 중 오류가 발생했습니다: {e}")
            st.info("데이터를 확인하고 다시 시도해주세요.")

    else:
        st.info("운동 기록 및 통증 기록이 부족합니다. 루틴을 완료하고 통증을 기록해 보세요.")
        
        # 실제 데이터 입력 폼
        st.subheader("📝 오늘의 운동 기록")
        col1, col2 = st.columns(2)
        
        with col1:
            completed_count = st.number_input("완료한 운동 횟수", min_value=0, value=0, step=1)
            if st.button("운동 기록 저장"):
                try:
                    exercise_data = {'completed_count': completed_count}
                    save_to_google_sheets(exercise_data, 'exercise_log', user_id)
                    st.success("운동 기록이 저장되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"운동 기록 저장 중 오류: {e}")
        
        with col2:
            pain_level = st.slider("오늘의 통증 수준", min_value=0, max_value=10, value=5)
            if st.button("통증 기록 저장"):
                try:
                    pain_data = {'pain_level': pain_level}
                    save_to_google_sheets(pain_data, 'pain_data', user_id)
                    st.success("통증 기록이 저장되었습니다!")
                    st.rerun()
                except Exception as e:
                    st.error(f"통증 기록 저장 중 오류: {e}")
        
        st.markdown("---")
        
        # 테스트 데이터 생성 버튼 (개발 중에만 사용)
        if st.button("🧪 테스트 데이터 생성 (하루치)"):
            try:
                today = str(date.today())
                
                # 테스트 운동 데이터 생성
                test_exercise_data = {
                    'completed_count': 5
                }
                save_to_google_sheets(test_exercise_data, 'exercise_log', user_id)
                
                # 테스트 통증 데이터 생성
                test_pain_data = {
                    'pain_level': 3
                }
                save_to_google_sheets(test_pain_data, 'pain_data', user_id)
                
                # 테스트 포인트 데이터 생성
                test_point_data = {
                    'points_gained': 10
                }
                save_to_google_sheets(test_point_data, 'point_data', user_id)
                
                st.success("테스트 데이터가 생성되었습니다! 페이지를 새로고침해주세요.")
                st.rerun()
            except Exception as e:
                st.error(f"테스트 데이터 생성 중 오류: {e}")

    st.markdown("---")

    # ====================================================================
    # 🌟 일별 포인트 리포트 시각화
    # ====================================================================
    st.subheader("💰 포인트 획득 리포트")
    
    if not point_df.empty:
        try:
            # 'user_id'에 따라 필터링 (날짜형 ID로 시작하는 행 포함)
            mask_pt = point_df['user_id'].astype(str).str.startswith(user_id)
            user_point_df = point_df.loc[mask_pt].copy()
        
        if not user_point_df.empty:
            user_point_df['date'] = pd.to_datetime(user_point_df['date'])
                user_point_df['points_gained'] = pd.to_numeric(user_point_df['points_gained'], errors='coerce').fillna(0)
            
            point_chart = alt.Chart(user_point_df).mark_bar(color='#4CAF50').encode(
                x=alt.X('date:T', title='날짜'),
                y=alt.Y('points_gained:Q', title='획득 포인트', axis=alt.Axis(labels=True, titleColor='#4CAF50')),
                tooltip=[alt.Tooltip('date:T', title='날짜'), alt.Tooltip('points_gained:Q', title='획득 포인트')]
            ).properties(
                title='일별 획득 포인트 변화'
            )
            
            st.altair_chart(point_chart, use_container_width=True)
        else:
                st.info("현재 사용자의 포인트 기록이 없습니다. 운동을 완료하고 포인트를 쌓아보세요.")
        except Exception as e:
            st.error(f"포인트 차트 생성 중 오류가 발생했습니다: {e}")
            st.info("포인트 데이터를 확인하고 다시 시도해주세요.")
    else:
        st.info("포인트 기록이 부족합니다. 운동을 완료하고 포인트를 쌓아보세요.")

# ====================================================================
# App Main Entry Point
# ====================================================================
if __name__ == "__main__":
    # Streamlit 앱으로 실행할 때는 user_id를 세션에서 가져오거나 생성
    if 'user_id' not in st.session_state:
        # 고정된 사용자 ID 사용 (하루에 한 번만 생성)
        today = date.today().strftime("%Y%m%d")
        st.session_state.user_id = f'user_{today}'
    
    user_id = st.session_state.user_id
    show_integrated_dashboard(user_id)
