# 구글시트로 관리/db저장돼서 나오도록
# exercise_manager_updated.py

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import random
import altair as alt
import os
import json
from dotenv import load_dotenv

# YouTube 데이터 조회를 위한 라이브러리 추가
try:
    from youtube_collector import search_youtube_videos, search_videos_by_condition, collect_all_vdt_videos
    from database import get_videos_for_condition, get_recommended_videos_for_user, get_database_analytics
    from video_analyzer import analyze_single_video
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError as e:
    YOUTUBE_SEARCH_AVAILABLE = False

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

# --- Google Sheets 설정 ---
GOOGLE_SHEETS_CREDENTIALS = "credentials.json"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

def init_google_sheets():
    """Google Sheets 초기화"""
    try:
        if not GSPREAD_AVAILABLE or not os.path.exists(GOOGLE_SHEETS_CREDENTIALS):
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

def save_to_local_json(data, data_type, user_id):
    """데이터를 로컬 JSON 파일에 저장합니다. (하루에 한 번만 기록, 중복시 덮어쓰기)"""
    try:
        json_file = "local_exercise_data.json"
        
        # 기존 데이터 로드
        existing_data = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except Exception:
                existing_data = []
        
        # 오늘 날짜
        today = str(date.today())
        
        # 오늘 날짜의 같은 타입 데이터가 있는지 확인하고 제거 (하루에 한 번만 기록)
        
        # 새 데이터 추가
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_record = {
            'timestamp': timestamp,
            'user_id': user_id,
            'data_type': data_type,
            'date': today,
            'value': data
        }
        
        existing_data.append(new_record)
        
        # JSON 파일에 저장
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        st.success(f"{data_type} 데이터가 로컬 파일에 저장되었습니다.")
        return True
        
    except Exception as e:
        st.error(f"로컬 파일 저장 중 오류 발생: {e}")
        return False

def save_to_google_sheets(data, sheet_name, user_id):
    """데이터를 Google Sheets에 저장 (하루에 한 번만 기록, 중복시 덮어쓰기)"""
    try:
        if not GSPREAD_AVAILABLE or not os.path.exists(GOOGLE_SHEETS_CREDENTIALS):
            st.warning("Google Sheets 연동이 비활성화되어 로컬에만 저장됩니다.")
            return save_to_local_json(data, sheet_name, user_id)

        if not user_id:
            user_id = st.session_state.get('user_id', 'unknown_user')

        client = init_google_sheets()
        if not client:
            st.error("Google Sheets 클라이언트 초기화 실패.")
            return save_to_local_json(data, sheet_name, user_id)

        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # 시트가 없으면 생성
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        
        # 오늘 날짜
        today = date.today().strftime("%Y-%m-%d")
        
        # 기존 데이터 확인 (오늘 날짜의 데이터가 있는지)
        try:
            all_records = worksheet.get_all_records()
            if all_records:
                df = pd.DataFrame(all_records)
                # 첫 번째 컬럼이 timestamp, 두 번째가 user_id
                df['date'] = pd.to_datetime(df.iloc[:, 0]).dt.date.astype(str)
                
                        # 오늘 날짜의 데이터가 있으면 업데이트 (하루에 한 번만 기록)
        except Exception as e:
            st.warning(f"기존 데이터 확인 중 오류: {e}")
        
        # 오늘 데이터가 없으면 새로 추가
        row_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id, data]
        worksheet.append_row(row_data)
        
        st.success(f"{sheet_name} 데이터가 Google Sheets에 저장되었습니다.")
        return True

    except gspread.exceptions.APIError as e:
        if "10000000" in str(e):
            st.warning("Google Sheets 셀 한도에 도달했습니다. 로컬 파일에 저장합니다.")
            return save_to_local_json(data, sheet_name, user_id)
        else:
            st.error(f"Google Sheets API 오류: {e}")
            return save_to_local_json(data, sheet_name, user_id)
    except Exception as e:
        st.error(f"Google Sheets 저장 중 오류: {e}")
        st.info("로컬 파일에 저장을 시도합니다.")
        return save_to_local_json(data, sheet_name, user_id)

# Google Sheets 연결 상태 확인
try:
    client = init_google_sheets()
    if client and SPREADSHEET_ID:
        GOOGLE_SHEETS_ENABLED = True
    else:
        GOOGLE_SHEETS_ENABLED = False
except Exception as e:
    GOOGLE_SHEETS_ENABLED = False

# VDT 증후군 증상 데이터 (app.py와 동일한 구조)
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

def _fetch_videos_from_sheet(condition: str, purpose: str, limit: int):
    """Google Sheets의 vdt_videos 시트에서 조건/목적 기반 영상 목록을 가져옵니다."""
    try:
        if not GOOGLE_SHEETS_ENABLED:
            return []
        
        client = init_google_sheets()
        if not client:
            return []
            
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # 시트 열기
        try:
            videos_ws = spreadsheet.worksheet("vdt_videos")
        except Exception:
            return []
        
        records = videos_ws.get_all_records()
        if not records:
            return []
        
        df = pd.DataFrame(records)
        
        # 조건과 목적에 맞는 영상 필터링
        filtered_df = df[
            (df['condition'].str.contains(condition, case=False, na=False)) &
            (df['purpose'].str.contains(purpose, case=False, na=False))
        ]
        
        if filtered_df.empty:
            return []
        
        # 제한된 수만큼 반환
        videos = []
        for _, row in filtered_df.head(limit).iterrows():
            videos.append({
                'title': row.get('title', ''),
                'url': row.get('url', ''),
                'channel_name': row.get('channel_name', ''),
                'duration_seconds': row.get('duration_seconds', 0)
            })
        
        return videos
        
    except Exception as e:
        return []

def get_videos_for_condition_enhanced(condition: str, purpose: str = "예방", limit: int = 3):
    """향상된 영상 추천 시스템: 데이터베이스 > Google Sheets > 하드코딩 순서로 시도"""
    videos = []
    
    # 1. 데이터베이스에서 영상 가져오기
    if YOUTUBE_SEARCH_AVAILABLE:
        try:
            db_videos = get_videos_for_condition(condition)
            if db_videos:
                videos.extend(db_videos[:limit])
        except Exception:
            pass
    
    # 2. Google Sheets에서 영상 가져오기
    if not videos and GOOGLE_SHEETS_ENABLED:
        try:
            sheet_videos = _fetch_videos_from_sheet(condition, purpose, limit)
            if sheet_videos:
                videos.extend(sheet_videos)
        except Exception:
            pass
    
    # 3. 하드코딩된 영상으로 fallback
    if not videos:
        try:
            hardcoded_videos = get_exercise_videos(condition)
            if hardcoded_videos:
                videos.extend(hardcoded_videos)
        except Exception:
            pass
    
    return videos[:limit]

def show_integrated_dashboard(user_id):
    """통합 대시보드 기능"""
    st.header("💻 통합 건강 대시보드")
    st.markdown("오늘의 운동 루틴을 완료하고, 통증을 기록하며 건강을 관리하세요.")
    
    if GOOGLE_SHEETS_ENABLED:
        st.info("📊 Google Sheets와 연결되어 데이터를 저장하고 불러옵니다.")
    else:
        st.warning("⚠️ Google Sheets가 연결되지 않아 로컬 데이터만 사용합니다.")
    
    # YouTube 연결 상태 표시
    if YOUTUBE_SEARCH_AVAILABLE:
        st.success("🎥 YouTube 영상 추천 시스템이 활성화되어 있습니다.")
    else:
        st.warning("⚠️ YouTube 영상 추천 시스템을 사용하려면 관련 라이브러리를 설치하세요.")
    
    st.markdown("---")
    
    # 세션 상태 초기화
    if 'exercise_log' not in st.session_state:
        st.session_state.exercise_log = {}
    if 'pain_data' not in st.session_state:
        st.session_state.pain_data = {}
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {}
    
    today = str(date.today())
    
    # 증상 선택
    st.subheader("🔍 현재 겪고 있는 증상을 선택해주세요")
    symptom_options = list(VDT_SYMPTOMS.keys())
    selected_conditions = st.multiselect(
        "증상을 선택해주세요:",
        symptom_options
    )
    
    st.markdown("---")
    
    # 오늘의 루틴
    st.subheader("🏃‍♂️ 오늘의 루틴")
    if not selected_conditions:
        st.info("먼저 위에서 증상을 하나 이상 선택해 주세요.")
    else:
        for condition in selected_conditions:
            st.markdown(f"**🔹 {condition}**")
            
            # 증상과 원인 표시
            if "증상" in VDT_SYMPTOMS[condition]:
                st.markdown("**📋 주요 증상:**")
                symptoms = VDT_SYMPTOMS[condition]["증상"]
                for symptom in symptoms:
                    st.markdown(f"• {symptom}")
            
            if "원인" in VDT_SYMPTOMS[condition]:
                st.markdown("**🔍 주요 원인:**")
                causes = VDT_SYMPTOMS[condition]["원인"]
                for cause in causes:
                    st.markdown(f"• {cause}")
            
            st.markdown("---")
            
            # 운동 추천
            if "운동_추천" in VDT_SYMPTOMS[condition]:
                exercises = VDT_SYMPTOMS[condition]["운동_추천"]
                for purpose, exercise_list in exercises.items():
                    st.markdown(f"**✨ {purpose} 운동**")
                    for exercise in exercise_list:
                        # 고유한 체크박스 키 생성
                        unique_key = f"completed_exercise_{today}_{condition}_{exercise['name']}"
                        
                        # 체크박스 상태를 세션 상태에 저장하고 로드
                        if unique_key not in st.session_state.checkbox_states:
                            st.session_state.checkbox_states[unique_key] = False
                            
                        # 체크박스 표시 및 상태 변경 시 세션 업데이트
                        st.session_state.checkbox_states[unique_key] = st.checkbox(
                            f"**{exercise['name']}**",
                            value=st.session_state.checkbox_states[unique_key],
                            key=unique_key
                        )

                        # 운동 상세 정보 표시
                        st.markdown(
                            f"""
                            - **목적:** {exercise['purpose']}
                            - **방법:** {exercise['method']}
                            - **반복:** {exercise['reps']}
                            """
                        )
                        if "caution" in exercise:
                            st.markdown(f"⚠️ **주의사항:** {exercise['caution']}")
            
            st.markdown("---")
            
            # 유튜브 영상 표시
            st.markdown("**📺 추천 영상**")
            try:
                videos = get_videos_for_condition_enhanced(condition, "예방", 2)
                if videos:
                    for i, video in enumerate(videos):
                        if 'url' in video and video['url']:
                            # YouTube URL에서 video ID 추출
                            video_id = video['url'].split('v=')[-1].split('&')[0]
                            st.markdown(f"**{video.get('title', '추천 영상')}**")
                            st.video(f"https://www.youtube.com/watch?v={video_id}")
                            
                            # 유튜브 영상 완료 체크박스 추가
                            video_key = f"completed_video_{today}_{condition}_{video.get('title', '추천 영상')}"
                            if video_key not in st.session_state.checkbox_states:
                                st.session_state.checkbox_states[video_key] = False
                            st.session_state.checkbox_states[video_key] = st.checkbox(
                                f"**{video.get('title', '추천 영상')}** 영상 시청 완료",
                                value=st.session_state.checkbox_states[video_key],
                                key=video_key
                            )
                else:
                    st.info("해당 증상에 대한 영상이 없습니다.")
            except Exception as e:
                st.warning(f"영상 로드 중 오류가 발생했습니다: {e}")
                # 하드코딩된 영상으로 fallback
                try:
                    fallback_videos = get_exercise_videos(condition)
                    if fallback_videos:
                        for video in fallback_videos:
                            if 'url' in video and video['url']:
                                video_id = video['url'].split('v=')[-1].split('&')[0]
                                st.markdown(f"**{video.get('title', '추천 영상')}**")
                                st.video(f"https://www.youtube.com/watch?v={video_id}")
                                
                                # 하드코딩된 영상도 체크박스 추가
                                video_key = f"completed_video_{today}_{condition}_{video.get('title', '추천 영상')}"
                                if video_key not in st.session_state.checkbox_states:
                                    st.session_state.checkbox_states[video_key] = False
                                st.session_state.checkbox_states[video_key] = st.checkbox(
                                    f"**{video.get('title', '추천 영상')}** 영상 시청 완료",
                                    value=st.session_state.checkbox_states[video_key],
                                    key=video_key
                                )
                except Exception:
                    st.info("영상을 불러올 수 없습니다.")
            
            st.markdown("---")
    
    # 운동 완료 기록
    st.subheader("💪 운동 완료 기록")
    
    if st.button("운동 완료 기록"):
        completed_exercises = []
        completed_videos = []
        
        # 모든 체크박스를 순회하며 완료된 운동을 기록
        for key, value in st.session_state.checkbox_states.items():
            if value and key.startswith(f"completed_exercise_{today}"):
                completed_exercises.append(key)
            elif value and key.startswith(f"completed_video_{today}"):
                completed_videos.append(key)
        
        total_completed = len(completed_exercises) + len(completed_videos)
        
        if total_completed > 0:
            st.session_state.exercise_log[today] = total_completed
            
            # 데이터 저장
            save_to_google_sheets(total_completed, 'exercise_log', user_id)
            
            st.success(f"✅ 운동 완료 기록이 저장되었습니다!")
            st.success(f"📊 완료 항목: 운동 {len(completed_exercises)}개 + 영상 시청 {len(completed_videos)}개 = 총 {total_completed}개")
            
            # 완료된 항목들 표시
            if completed_exercises:
                st.info("✅ 완료된 운동:")
                for exercise_key in completed_exercises:
                    exercise_name = exercise_key.split('_')[-1]
                    st.write(f"• {exercise_name}")
            
            if completed_videos:
                st.info("📺 시청 완료한 영상:")
                for video_key in completed_videos:
                    video_name = video_key.split('_')[-1]
                    st.write(f"• {video_name}")
        else:
            st.warning("⚠️ 완료한 운동이나 영상이 없습니다. 체크박스를 선택해주세요.")
        
        st.rerun()
    
    # 통증 기록
    st.subheader("🏥 나의 통증 기록하기")
    current_pain_level = st.slider(
        "오늘의 통증 점수 (0: 없음, 15: 심함)",
        0, 15, key="pain_slider"
    )
    if st.button("통증 기록 저장"):
        st.session_state.pain_data[today] = current_pain_level
        
        # 데이터 저장
        save_to_google_sheets(current_pain_level, 'pain_data', user_id)
        
        st.success(f"✅ 통증 기록이 저장되었습니다! (통증 점수: {current_pain_level}/15)")
        st.rerun()
    
    st.markdown("---")
    
    # 통증·운동 리포트
    st.subheader("📈 통증·운동 리포트")
    
    # 데이터 로드 (세션 상태 우선, Google Sheets에서 로드, 실패시 로컬 JSON 파일에서)
    exercise_df = pd.DataFrame()
    pain_df = pd.DataFrame()
    
    # 0. 세션 상태에서 오늘 데이터 즉시 추가 (실시간 반영)
    today = str(date.today())
    if today in st.session_state.exercise_log:
        exercise_df = pd.DataFrame({
            'user_id': [user_id],
            'date': [pd.to_datetime(today)],
            'completed_count': [st.session_state.exercise_log[today]]
        })
    
    if today in st.session_state.pain_data:
        pain_df = pd.DataFrame({
            'user_id': [user_id],
            'date': [pd.to_datetime(today)],
            'pain_level': [st.session_state.pain_data[today]]
        })
    
    # 1. Google Sheets에서 데이터 로드 시도
    if GOOGLE_SHEETS_ENABLED:
        try:
            client = init_google_sheets()
            if client:
                spreadsheet = client.open_by_key(SPREADSHEET_ID)
                
                # exercise_log 시트에서 데이터 로드
                try:
                    exercise_ws = spreadsheet.worksheet("exercise_log")
                    exercise_records = exercise_ws.get_all_records()
                    if exercise_records:
                        sheet_exercise_df = pd.DataFrame(exercise_records)
                        sheet_exercise_df['date'] = pd.to_datetime(sheet_exercise_df.iloc[:, 0])  # 첫 번째 컬럼이 timestamp
                        sheet_exercise_df['completed_count'] = pd.to_numeric(sheet_exercise_df.iloc[:, 2], errors='coerce').fillna(0)  # 세 번째 컬럼이 value
                        sheet_exercise_df['user_id'] = sheet_exercise_df.iloc[:, 1]  # 두 번째 컬럼이 user_id
                        
                        # 날짜별로 중복 제거 (가장 최근 데이터만 유지)
                        sheet_exercise_df = sheet_exercise_df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
                        
                        # 세션 데이터와 병합
                        if not exercise_df.empty:
                            # 오늘 데이터가 있으면 덮어쓰기
                            exercise_df = pd.concat([sheet_exercise_df[sheet_exercise_df['date'].dt.date != date.today()], exercise_df])
                        else:
                            exercise_df = sheet_exercise_df
                except Exception as e:
                    st.info("💡 Google Sheets 연결을 건너뛰고 로컬 데이터를 사용합니다.")
                
                # pain_data 시트에서 데이터 로드
                try:
                    pain_ws = spreadsheet.worksheet("pain_data")
                    pain_records = pain_ws.get_all_records()
                    if pain_records:
                        sheet_pain_df = pd.DataFrame(pain_records)
                        sheet_pain_df['date'] = pd.to_datetime(sheet_pain_df.iloc[:, 0])  # 첫 번째 컬럼이 timestamp
                        sheet_pain_df['pain_level'] = pd.to_numeric(sheet_pain_df.iloc[:, 2], errors='coerce')  # 세 번째 컬럼이 value
                        sheet_pain_df['user_id'] = sheet_pain_df.iloc[:, 1]  # 두 번째 컬럼이 user_id
                        
                        # 날짜별로 중복 제거 (가장 최근 데이터만 유지)
                        sheet_pain_df = sheet_pain_df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
                        
                        # 세션 데이터와 병합
                        if not pain_df.empty:
                            # 오늘 데이터가 있으면 덮어쓰기
                            pain_df = pd.concat([sheet_pain_df[sheet_pain_df['date'].dt.date != date.today()], pain_df])
                        else:
                            pain_df = sheet_pain_df
                except Exception as e:
                    st.info("💡 Google Sheets 연결을 건너뛰고 로컬 데이터를 사용합니다.")
                    
        except Exception as e:
            st.info("💡 Google Sheets 연결을 건너뛰고 로컬 데이터를 사용합니다.")
    
    # 2. Google Sheets에서 데이터를 가져오지 못한 경우 로컬 JSON 파일에서 로드
    if exercise_df.empty and pain_df.empty:
        json_file = "local_exercise_data.json"
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data:
                    df = pd.DataFrame(data)
                    
                    # 운동 로그 데이터
                    exercise_data = df[df['data_type'] == 'exercise_log'].copy()
                    if not exercise_data.empty:
                        json_exercise_df = exercise_data[['user_id', 'date', 'value']].copy()
                        json_exercise_df['date'] = pd.to_datetime(json_exercise_df['date'])
                        json_exercise_df['completed_count'] = pd.to_numeric(json_exercise_df['value'], errors='coerce').fillna(0)
                        # 날짜별로 중복 제거 (가장 최근 데이터만 유지)
                        json_exercise_df = json_exercise_df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
                        
                        # 세션 데이터와 병합
                        if not exercise_df.empty:
                            exercise_df = pd.concat([json_exercise_df[json_exercise_df['date'].dt.date != date.today()], exercise_df])
                        else:
                            exercise_df = json_exercise_df
                    
                    # 통증 데이터
                    pain_data = df[df['data_type'] == 'pain_data'].copy()
                    if not pain_data.empty:
                        json_pain_df = pain_data[['user_id', 'date', 'value']].copy()
                        json_pain_df['date'] = pd.to_datetime(json_pain_df['date'])
                        json_pain_df['pain_level'] = pd.to_numeric(json_pain_df['value'], errors='coerce')
                        # 날짜별로 중복 제거 (가장 최근 데이터만 유지)
                        json_pain_df = json_pain_df.sort_values('date').drop_duplicates(subset=['date'], keep='last')
                        
                        # 세션 데이터와 병합
                        if not pain_df.empty:
                            pain_df = pd.concat([json_pain_df[json_pain_df['date'].dt.date != date.today()], pain_df])
                        else:
                            pain_df = json_pain_df
            except Exception as e:
                st.warning(f"로컬 데이터 로드 중 오류: {e}")
    
    # 데이터 로드 상태 표시
    if not exercise_df.empty or not pain_df.empty:
        st.success("✅ 데이터를 성공적으로 로드했습니다!")
        if not exercise_df.empty:
            st.info(f"📊 운동 데이터: {len(exercise_df)}건")
        if not pain_df.empty:
            st.info(f"🏥 통증 데이터: {len(pain_df)}건")
    else:
        st.warning("⚠️ 로드할 데이터가 없습니다. 운동과 통증을 기록해보세요!")
    
    # 데이터 상태 표시
    col1, col2 = st.columns(2)
    with col1:
        exercise_days = len(exercise_df) if not exercise_df.empty else 0
        st.metric("운동 기록", f"{exercise_days}일")
    with col2:
        pain_days = len(pain_df) if not pain_df.empty else 0
        st.metric("통증 기록", f"{pain_days}일")
    
    # 일별 기록 안내 메시지
    st.info("💡 각 날짜별로 개별 기록이 표시됩니다. 같은 날에 다시 기록하면 기존 데이터가 새로운 데이터로 업데이트됩니다.")
    
    # 그래프 생성
    if not exercise_df.empty or not pain_df.empty:
        try:
            # 사용자 데이터 필터링 (user_id가 정확히 일치하는 경우만)
            if not exercise_df.empty:
                user_exercise_df = exercise_df[exercise_df['user_id'] == user_id].copy()
                if user_exercise_df.empty:
                    # user_id가 정확히 일치하지 않으면 모든 데이터 사용
                    user_exercise_df = exercise_df.copy()
            else:
                user_exercise_df = pd.DataFrame()

            if not pain_df.empty:
                user_pain_df = pain_df[pain_df['user_id'] == user_id].copy()
                if user_pain_df.empty:
                    # user_id가 정확히 일치하지 않으면 모든 데이터 사용
                    user_pain_df = pain_df.copy()
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
                
                # join을 사용하여 데이터를 병합
                if not user_exercise_df.empty:
                    combined_df = combined_df.join(user_exercise_df[['completed_count']])
                
                if not user_pain_df.empty:
                    combined_df = combined_df.join(user_pain_df[['pain_level']])
                
                # 기본값으로 채우기 (그래프 표시용)
                combined_df = combined_df.fillna({'completed_count': 0, 'pain_level': 0})
                combined_df = combined_df.reset_index()
                combined_df = combined_df.rename(columns={'index': 'date'})
                
                # 데이터 정렬
                combined_df = combined_df.sort_values('date')

                # 운동 데이터와 통증 데이터를 분리 (실제 데이터가 있는 경우만)
                exercise_data = combined_df[combined_df['completed_count'] > 0].copy()
                pain_data = combined_df[combined_df['pain_level'] > 0].copy()
                
                # 안전한 최대값 계산
                max_count = max(exercise_data['completed_count'].max() if not exercise_data.empty else 1, 1)
                max_pain = max(pain_data['pain_level'].max() if not pain_data.empty else 1, 1)

                # 운동 횟수 차트 (바 차트)
                if not exercise_data.empty:
                    bar_chart = alt.Chart(exercise_data).mark_bar(color='#26A69A', opacity=0.7).encode(
                        x=alt.X('date:T', title='날짜', axis=alt.Axis(format="%m-%d")),
                        y=alt.Y(
                            'completed_count:Q',
                            title='운동 횟수',
                            axis=alt.Axis(labels=True, titleColor='#26A69A'),
                            scale=alt.Scale(domain=[0, max_count + 2])
                        ),
                        tooltip=[
                            alt.Tooltip('date:T', title='날짜', format="%Y-%m-%d"),
                            alt.Tooltip('completed_count:Q', title='운동 횟수')
                        ]
                    )
                else:
                    bar_chart = alt.Chart(pd.DataFrame()).mark_bar()

                # 통증 점수 차트 (선 + 점 차트)
                if not pain_data.empty:
                    line_chart = alt.Chart(pain_data).mark_line(color='#FF5722', strokeWidth=3).encode(
                        x=alt.X('date:T', title='날짜', axis=alt.Axis(format="%m-%d")),
                        y=alt.Y(
                            'pain_level:Q',
                            title='통증 점수',
                            axis=alt.Axis(labels=True, titleColor='#FF5722'),
                            scale=alt.Scale(domain=[0, 15])
                        ),
                        tooltip=[
                            alt.Tooltip('date:T', title='날짜', format="%Y-%m-%d"),
                            alt.Tooltip('pain_level:Q', title='통증 점수')
                        ]
                    )

                    point_chart = alt.Chart(pain_data).mark_point(
                        color='#FF5722',
                        size=80,
                        filled=True,
                    ).encode(
                        x=alt.X('date:T', title='날짜', axis=alt.Axis(format="%m-%d")),
                        y=alt.Y(
                            'pain_level:Q',
                            title='통증 점수',
                            axis=alt.Axis(labels=True, titleColor='#FF5722'),
                            scale=alt.Scale(domain=[0, 15])
                        ),
                        tooltip=[
                            alt.Tooltip('date:T', title='날짜', format="%Y-%m-%d"),
                            alt.Tooltip('pain_level:Q', title='통증 점수')
                        ]
                    )
                else:
                    line_chart = alt.Chart(pd.DataFrame()).mark_line()
                    point_chart = alt.Chart(pd.DataFrame()).mark_point()

                # 차트 결합
                combined_chart = alt.layer(bar_chart, line_chart, point_chart).resolve_scale(
                    y='independent'
                ).properties(
                    title='운동 횟수와 통증 점수 변화',
                    width=600,
                    height=400
                ).interactive()
                
                st.altair_chart(combined_chart, use_container_width=True)
                
                # 데이터 요약 표시
                st.subheader("📊 데이터 요약")
                col1, col2 = st.columns(2)
                with col1:
                    if not user_exercise_df.empty:
                        st.metric("총 운동 횟수", f"{user_exercise_df['completed_count'].sum()}회")
                        st.metric("평균 운동 횟수", f"{user_exercise_df['completed_count'].mean():.1f}회")
                with col2:
                    if not user_pain_df.empty:
                        st.metric("평균 통증 점수", f"{user_pain_df['pain_level'].mean():.1f}/15")
                        st.metric("최고 통증 점수", f"{user_pain_df['pain_level'].max()}/15")
            else:
                st.info("현재 사용자의 운동/통증 기록이 없습니다.")
        except Exception as e:
            st.error(f"차트 생성 중 오류가 발생했습니다: {e}")
            st.info("데이터를 확인하고 다시 시도해주세요.")
            # 디버깅을 위한 데이터 출력
            st.write("디버깅 정보:")
            st.write(f"exercise_df shape: {exercise_df.shape}")
            st.write(f"pain_df shape: {pain_df.shape}")
            if not exercise_df.empty:
                st.write("exercise_df columns:", exercise_df.columns.tolist())
                st.write("exercise_df head:", exercise_df.head())
            if not pain_df.empty:
                st.write("pain_df columns:", pain_df.columns.tolist())
                st.write("pain_df head:", pain_df.head())

    else:
        st.info("운동 기록 및 통증 기록이 부족합니다. 루틴을 완료하고 통증을 기록해 보세요.")
        
        # 기본 그래프 표시 (데이터가 없어도)
        st.subheader("📊 오늘의 기록")
        today = date.today()
        
        # 기본 데이터 생성
        basic_df = pd.DataFrame({
            'date': [today],
            'completed_count': [0],
            'pain_level': [0]
        })
        
        # Altair를 사용한 이중 축 차트 생성
        base = alt.Chart(basic_df).encode(
            alt.X('date:T', title='날짜')
        )
        
        bar_chart = base.mark_bar(color='#26A69A').encode(
            y=alt.Y(
                'completed_count:Q',
                title='운동 횟수',
                axis=alt.Axis(labels=True, titleColor='#26A69A'),
                scale=alt.Scale(domain=[0, 10])
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
            title='운동 횟수와 통증 점수 변화 (기본 표시)'
        )
        
        st.altair_chart(combined_chart, use_container_width=True)
        st.info("💡 운동을 완료하고 통증을 기록하면 그래프가 업데이트됩니다!")
        
        st.markdown("---")

# App Main Entry Point
if __name__ == "__main__":
    # Streamlit 앱으로 실행할 때는 user_id를 세션에서 가져오거나 생성
    if 'user_id' not in st.session_state:
        # 고정된 사용자 ID 사용 (하루에 한 번만 생성)
        today = date.today().strftime("%Y%m%d")
        st.session_state.user_id = f'user_{today}'
    
    user_id = st.session_state.user_id
    show_integrated_dashboard(user_id)
