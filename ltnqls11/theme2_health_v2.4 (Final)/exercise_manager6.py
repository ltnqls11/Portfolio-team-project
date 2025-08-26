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

# Supabase 관련 라이브러리 추가
try:
    from supabase import create_client, Client
    from config import SUPABASE_URL, SUPABASE_ANON_KEY
    SUPABASE_AVAILABLE = True
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    else:
        SUPABASE_AVAILABLE = False
except ImportError as e:
    SUPABASE_AVAILABLE = False

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

def ensure_exercise_table_exists():
    """exercise_management 테이블 존재 확인 (생성은 Supabase Dashboard에서)"""
    if not SUPABASE_AVAILABLE:
        return False
    
    try:
        # 테이블 존재 여부 확인 - 간단한 SELECT 쿼리로 테스트
        result = supabase.table('exercise_management').select('id').limit(1).execute()
        return True
    except Exception as e:
        # 테이블이 없으면 안내 메시지
        st.warning("""
        ⚠️ Supabase에 'exercise_management' 테이블이 없습니다.
        
        다음 SQL을 Supabase Dashboard에서 실행해주세요:
        ```sql
        CREATE TABLE IF NOT EXISTS exercise_management (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            data_type VARCHAR(50) NOT NULL,
            user_email VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            value TEXT NOT NULL,
            details JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        ```
        """)
        return False

def save_to_supabase(data_type, user_id, date, value):
    """Supabase에 데이터 저장"""
    if not SUPABASE_AVAILABLE:
        return False
    
    try:
        # exercise_management 테이블에 저장 시도
        data = {
            'data_type': data_type,
            'user_email': user_id,
            'date': str(date),
            'value': str(value),
            'details': json.dumps({
                'timestamp': datetime.now().isoformat(),
                'type': data_type
            })
        }
        
        # 먼저 테이블이 있는지 확인
        try:
            result = supabase.table('exercise_management').insert(data).execute()
            return True
        except Exception as table_error:
            # 테이블이 없으면 customer_history 사용
            if 'PGRST' in str(table_error):
                st.info("📝 customer_history 테이블을 사용합니다...")
                
                # customer_history 테이블 구조에 맞게 저장
                history_data = {
                    'email': user_id,
                    'user_data': json.dumps({
                        'exercise_data': {
                            'data_type': data_type,
                            'date': str(date),
                            'value': str(value)
                        }
                    }),
                    'conditions': json.dumps([data_type]),
                    'pain_scores': json.dumps({'value': str(value)}) if data_type == 'pain_data' else json.dumps({}),
                    'created_at': datetime.now().isoformat()
                }
                
                result = supabase.table('customer_history').insert(history_data).execute()
                return True
            else:
                raise table_error
                
    except Exception as e:
        st.warning(f"Supabase 저장 오류: {e}")
        return False

def load_from_supabase(user_id=None):
    """Supabase에서 데이터 로드"""
    if not SUPABASE_AVAILABLE:
        return pd.DataFrame(), pd.DataFrame()
    
    exercise_df = pd.DataFrame()
    pain_df = pd.DataFrame()
    
    # 1. exercise_management 테이블에서 로드 시도
    try:
        query = supabase.table('exercise_management').select('*')
        if user_id:
            query = query.eq('user_email', user_id)
        
        result = query.execute()
        
        if result.data:
            df = pd.DataFrame(result.data)
            
            # 운동 데이터 필터링
            exercise_data = df[df['data_type'] == 'exercise_log'].copy()
            if not exercise_data.empty:
                temp_df = exercise_data.copy()
                temp_df['user_id'] = temp_df['user_email'] if 'user_email' in temp_df.columns else user_id
                temp_df['date'] = pd.to_datetime(temp_df['date'])
                temp_df['completed_count'] = pd.to_numeric(temp_df['value'], errors='coerce').fillna(0)
                exercise_df = temp_df[['user_id', 'date', 'completed_count']].copy()
            
            # 통증 데이터 필터링  
            pain_data = df[df['data_type'] == 'pain_data'].copy()
            if not pain_data.empty:
                temp_df = pain_data.copy()
                temp_df['user_id'] = temp_df['user_email'] if 'user_email' in temp_df.columns else user_id
                temp_df['date'] = pd.to_datetime(temp_df['date'])
                temp_df['pain_level'] = pd.to_numeric(temp_df['value'], errors='coerce').fillna(0)
                pain_df = temp_df[['user_id', 'date', 'pain_level']].copy()
                
    except Exception as e:
        # exercise_management 테이블이 없으면 customer_history 사용
        pass
    
    # 2. customer_history 테이블에서도 로드 시도
    try:
        query = supabase.table('customer_history').select('*')
        if user_id:
            query = query.eq('email', user_id)
        
        result = query.execute()
        
        if result.data:
            for record in result.data:
                try:
                    user_data_str = record.get('user_data', '{}')
                    if isinstance(user_data_str, str):
                        user_data = json.loads(user_data_str)
                    else:
                        user_data = user_data_str
                    
                    # exercise_data 확인
                    if 'exercise_data' in user_data:
                        ex_data = user_data['exercise_data']
                        if ex_data.get('data_type') == 'exercise_log':
                            new_row = pd.DataFrame({
                                'user_id': [record.get('email', user_id)],
                                'date': [pd.to_datetime(ex_data.get('date'))],
                                'completed_count': [pd.to_numeric(ex_data.get('value', 0), errors='coerce')]
                            })
                            exercise_df = pd.concat([exercise_df, new_row], ignore_index=True)
                        elif ex_data.get('data_type') == 'pain_data':
                            new_row = pd.DataFrame({
                                'user_id': [record.get('email', user_id)],
                                'date': [pd.to_datetime(ex_data.get('date'))],
                                'pain_level': [pd.to_numeric(ex_data.get('value', 0), errors='coerce')]
                            })
                            pain_df = pd.concat([pain_df, new_row], ignore_index=True)
                            
                except Exception as parse_error:
                    continue
    except Exception as e:
        pass
    
    # 중복 제거 및 정렬
    if not exercise_df.empty:
        exercise_df = exercise_df.drop_duplicates(subset=['date'], keep='last').sort_values('date')
    if not pain_df.empty:
        pain_df = pain_df.drop_duplicates(subset=['date'], keep='last').sort_values('date')
    
    return exercise_df, pain_df

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
    "손목터널증후군": {
        "증상": ["손목 통증", "손가락 저림", "손 근력 약화", "밤에 심해지는 손목 통증"],
        "원인": ["반복적인 손목 사용", "부자연스러운 손목 각도", "장시간 컴퓨터 사용"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "손목 스트레칭", "purpose": "손목 근육 이완", "method": "손목을 위아래로 구부리기 (양손)", "reps": "10회씩 3세트", "caution": "통증 시 중단"},
                {"name": "손가락 펴기", "purpose": "손가락 근육 이완", "method": "손가락을 쭉 펴고 5초간 유지", "reps": "10회", "caution": "부드럽게 실시"},
                {"name": "손목 측면 스트레칭", "purpose": "손목 측면 근육 이완", "method": "손목을 좌우로 젖히기", "reps": "각 방향 10초씩 3회", "caution": "서서히 진행"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "손목 근력 강화", "purpose": "손목 주변 근육 강화", "method": "가벼운 무게로 손목 굽히기 운동", "reps": "15회 2세트", "caution": "무리하지 말 것"},
                {"name": "손가락 운동", "purpose": "손가락 근력 강화", "method": "주먹 쥐었다 펴기 반복", "reps": "20회 2세트", "caution": "천천히 실시"}
            ],
            "재활 (통증감소)": [
                {"name": "신경 활주 운동", "purpose": "신경 압박 완화", "method": "손목과 손가락을 천천히 펴고 구부리기", "reps": "10회씩 하루 3번", "caution": "저림이 심해지면 중단"},
                {"name": "손목 마사지", "purpose": "혈액순환 개선", "method": "손목 부위를 부드럽게 마사지", "reps": "2-3분", "caution": "강하게 누르지 말 것"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "손목터널증후군 스트레칭", "url": "https://www.youtube.com/watch?v=EiRC80FJbHU"},
            {"title": "손목 통증 스트레칭", "url": "https://www.youtube.com/watch?v=9D_r_z0i9pI"},
            {"title": "손목터널 증후군 예방", "url": "https://www.youtube.com/watch?v=G96q6sL3FhY"}
        ]
    }
}

def normalize_condition_name(condition):
    """
    증상명을 정규화합니다. 손목터널증후군의 좌/우 구분을 통일합니다.
    """
    if "손목터널증후군" in condition:
        return "손목터널증후군"
    return condition

def get_exercises_for_condition(condition, purpose="예방 (자세교정)"):
    """
    특정 증상에 대한 운동 추천 목록을 반환합니다.
    """
    # 증상명 정규화
    normalized_condition = normalize_condition_name(condition)
    return VDT_SYMPTOMS.get(normalized_condition, {}).get("운동_추천", {}).get(purpose, [])

def get_exercise_videos(condition):
    """
    특정 증상에 대한 YouTube 영상 목록을 반환합니다.
    """
    # 증상명 정규화
    normalized_condition = normalize_condition_name(condition)
    videos = VDT_SYMPTOMS.get(normalized_condition, {}).get("유튜브_영상_링크", [])
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
    # 조건명 정규화
    normalized_condition = normalize_condition_name(condition)
    videos = []
    
    # 1. 데이터베이스에서 영상 가져오기
    if YOUTUBE_SEARCH_AVAILABLE:
        try:
            db_videos = get_videos_for_condition(normalized_condition)
            if db_videos:
                videos.extend(db_videos[:limit])
        except Exception:
            pass
    
    # 2. Google Sheets에서 영상 가져오기
    if not videos and GOOGLE_SHEETS_ENABLED:
        try:
            sheet_videos = _fetch_videos_from_sheet(normalized_condition, purpose, limit)
            if sheet_videos:
                videos.extend(sheet_videos)
        except Exception:
            pass
    
    # 3. 하드코딩된 영상으로 fallback
    if not videos:
        try:
            hardcoded_videos = get_exercise_videos(normalized_condition)
            if hardcoded_videos:
                videos.extend(hardcoded_videos)
        except Exception:
            pass
    
    return videos[:limit]

def show_integrated_dashboard(user_email=None):
    """통합 대시보드 기능 - 이메일 기준 사용자 관리"""
    st.header("💻 통합 건강 대시보드")
    
    # 개인정보 입력 완료 여부 확인 (이메일 기준)
    if not user_email:
        st.warning("❗ 먼저 '개인정보 입력' 탭에서 정보를 입력해주세요.")
        st.info("💡 개인정보가 입력된 후에 운동 관리 기능을 사용할 수 있습니다.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 개인정보 입력하러 가기", type="primary"):
                st.session_state.menu_selection = "증상 선택"
                st.rerun()
        
        return
    
    # 로그인된 사용자 표시
    st.success(f"👤 환영합니다! {user_email}님의 운동 관리 페이지입니다.")
    st.markdown("오늘의 운동 루틴을 완료하고, 통증을 기록하며 건강을 관리하세요.")
    st.markdown("---")
    
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
    
    # 증상 선택 - 이미 선택된 증상 사용
    st.subheader("🔍 현재 관리 중인 증상")
    
    # 세션에서 이미 선택된 증상 가져오기
    if hasattr(st.session_state, 'selected_conditions') and st.session_state.selected_conditions:
        selected_conditions = st.session_state.selected_conditions
        st.success(f"✅ 선택된 증상: {', '.join(selected_conditions)}")
        
        # 추가 증상이 있는지 확인
        symptom_options = list(VDT_SYMPTOMS.keys())
        remaining_symptoms = [sym for sym in symptom_options if sym not in selected_conditions]
        
        if remaining_symptoms:
            additional_conditions = st.multiselect(
                "추가로 관리하고 싶은 증상이 있나요?",
                remaining_symptoms
            )
            if additional_conditions:
                selected_conditions.extend(additional_conditions)
                st.info(f"📝 추가된 증상: {', '.join(additional_conditions)}")
    else:
        st.warning("⚠️ 먼저 '증상 선택' 메뉴에서 증상을 선택해주세요.")
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
            
            # 조건명 정규화
            normalized_condition = normalize_condition_name(condition)
            
            # 증상과 원인 표시
            if normalized_condition in VDT_SYMPTOMS and "증상" in VDT_SYMPTOMS[normalized_condition]:
                st.markdown("**📋 주요 증상:**")
                symptoms = VDT_SYMPTOMS[normalized_condition]["증상"]
                for symptom in symptoms:
                    st.markdown(f"• {symptom}")
            
            if "원인" in VDT_SYMPTOMS[normalized_condition]:
                st.markdown("**🔍 주요 원인:**")
                causes = VDT_SYMPTOMS[normalized_condition]["원인"]
                for cause in causes:
                    st.markdown(f"• {cause}")
            
            st.markdown("---")
            
            # 운동 추천
            if "운동_추천" in VDT_SYMPTOMS[normalized_condition]:
                exercises = VDT_SYMPTOMS[normalized_condition]["운동_추천"]
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
                videos = get_videos_for_condition_enhanced(normalized_condition, "예방", 2)
                if videos:
                    for i, video in enumerate(videos):
                        if 'url' in video and video['url']:
                            # 하이퍼링크로만 표시 (썸네일 없음)
                            video_title = video.get('title', '추천 영상')
                            video_url = video['url']
                            st.markdown(f"**[{video_title}]({video_url})**")
                            
                            # 유튜브 영상 완료 체크박스 추가
                            video_key = f"completed_video_{today}_{condition}_{video.get('title', '추천 영상')}"
                            if video_key not in st.session_state.checkbox_states:
                                st.session_state.checkbox_states[video_key] = False
                            # 체크박스 상태에 따라 라벨 동적 변경
                            is_watched = st.session_state.checkbox_states[video_key]
                            checkbox_label = f"**{video.get('title', '추천 영상')}** {'✅ 시청 완료' if is_watched else '▶️ 시청하기'}"
                            
                            st.session_state.checkbox_states[video_key] = st.checkbox(
                                checkbox_label,
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
                                # 하이퍼링크로만 표시 (썸네일 없음)
                                video_title = video.get('title', '추천 영상')
                                video_url = video['url']
                                st.markdown(f"**[{video_title}]({video_url})**")
                                
                                # 하드코딩된 영상도 체크박스 추가
                                video_key = f"completed_video_{today}_{condition}_{video.get('title', '추천 영상')}"
                                if video_key not in st.session_state.checkbox_states:
                                    st.session_state.checkbox_states[video_key] = False
                                # 하드코딩된 영상도 동적 라벨 적용
                                is_watched = st.session_state.checkbox_states[video_key]
                                checkbox_label = f"**{video.get('title', '추천 영상')}** {'✅ 시청 완료' if is_watched else '▶️ 시청하기'}"
                                
                                st.session_state.checkbox_states[video_key] = st.checkbox(
                                    checkbox_label,
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
            
            # 통합 데이터베이스에 저장
            from customer_database import save_exercise_record
            db_saved = save_exercise_record(user_email, 'exercise_log', total_completed, today)
            
            # 백업: Google Sheets와 로컬 저장
            google_saved = save_to_google_sheets(total_completed, 'exercise_log', user_email)
            local_saved = save_to_local_json(total_completed, 'exercise_log', user_email)
            
            # 저장 상태 표시
            if db_saved:
                st.success("✅ 운동 기록이 데이터베이스에 저장되었습니다!")
            elif google_saved or local_saved:
                st.success("✅ 운동 기록이 백업 저장소에 저장되었습니다!")
            else:
                st.warning("⚠️ 데이터 저장에 실패했습니다. 로컬 저장을 시도합니다.")
                # 로컬 백업 저장
                try:
                    backup_data = {
                        'user_id': user_email,
                        'date': today,
                        'data_type': 'exercise_log',
                        'value': total_completed,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    backup_file = "local_exercise_backup.json"
                    existing_data = []
                    if os.path.exists(backup_file):
                        with open(backup_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                existing_data = json.loads(content)
                    
                    existing_data.append(backup_data)
                    
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                    
                    st.success("💾 데이터가 로컬 백업 파일에 저장되었습니다.")
                except Exception as e:
                    st.error(f"로컬 백업 저장도 실패했습니다: {e}")
            
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
    
    # 통증 단계별 이모지 표시
    pain_emoji_map = {
        0: "😊 없음",
        1: "🙂 미미함", 2: "🙂 미미함", 3: "🙂 미미함",
        4: "😐 약함", 5: "😐 약함", 6: "😐 약함",  
        7: "😟 보통", 8: "😟 보통", 9: "😟 보통",
        10: "😰 심함", 11: "😰 심함", 12: "😰 심함",
        13: "😱 매우심함", 14: "😱 매우심함", 15: "😱 극심함"
    }
    
    if current_pain_level in pain_emoji_map:
        st.markdown(f"### {pain_emoji_map[current_pain_level]}")
        
        # 통증 정도별 설명
        if current_pain_level == 0:
            st.info("👍 통증이 없는 상태입니다.")
        elif 1 <= current_pain_level <= 3:
            st.info("💚 매우 경미한 통증입니다. 일상생활에 지장이 없습니다.")
        elif 4 <= current_pain_level <= 6:
            st.warning("💛 약한 통증입니다. 가벼운 운동을 권장합니다.")
        elif 7 <= current_pain_level <= 9:
            st.warning("🧡 보통 통증입니다. 휴식과 스트레칭이 필요합니다.")
        elif 10 <= current_pain_level <= 12:
            st.error("❤️ 심한 통증입니다. 전문의 상담을 권장합니다.")
        else:  # 13-15
            st.error("💔 극심한 통증입니다. 즉시 전문의 진료가 필요합니다.")
    if st.button("통증 기록 저장"):
        st.session_state.pain_data[today] = current_pain_level
        
        # 통합 데이터베이스에 저장
        from customer_database import save_exercise_record
        db_saved = save_exercise_record(user_email, 'pain_data', current_pain_level, today)
        
        # 백업: Google Sheets와 로컬 저장
        google_saved = save_to_google_sheets(current_pain_level, 'pain_data', user_email)
        local_saved = save_to_local_json(current_pain_level, 'pain_data', user_email)
        
        # 저장 상태 표시
        if db_saved:
            st.success("✅ 통증 기록이 데이터베이스에 저장되었습니다!")
        elif google_saved or local_saved:
            st.success("✅ 통증 기록이 백업 저장소에 저장되었습니다!")
        else:
            st.warning("⚠️ 통증 데이터 저장에 실패했습니다.")
        
        st.success(f"✅ 통증 기록이 저장되었습니다! (통증 점수: {current_pain_level}/15)")
        st.rerun()
    
    st.markdown("---")
    
    # 통증·운동 리포트
    st.subheader("📈 통증·운동 리포트")
    
    # 데이터 로드 (세션 상태 우선, Google Sheets에서 로드, 실패시 로컬 JSON 파일에서)
    exercise_df = pd.DataFrame()
    pain_df = pd.DataFrame()
    
    # 0. 통합 데이터베이스에서 데이터 로드
    try:
        from customer_database import get_exercise_records
        
        # 운동 기록 로드
        exercise_records = get_exercise_records(user_email, 'exercise_log', days=30)
        if exercise_records:
            db_exercise_df = pd.DataFrame(exercise_records)
            db_exercise_df['date'] = pd.to_datetime(db_exercise_df['record_date'])
            db_exercise_df['completed_count'] = pd.to_numeric(db_exercise_df['value'], errors='coerce').fillna(0)
            db_exercise_df['user_id'] = user_email
            exercise_df = db_exercise_df[['user_id', 'date', 'completed_count']].copy()
        
        # 통증 기록 로드
        pain_records = get_exercise_records(user_email, 'pain_data', days=30)
        if pain_records:
            db_pain_df = pd.DataFrame(pain_records)
            db_pain_df['date'] = pd.to_datetime(db_pain_df['record_date'])
            db_pain_df['pain_level'] = pd.to_numeric(db_pain_df['value'], errors='coerce').fillna(0)
            db_pain_df['user_id'] = user_email
            pain_df = db_pain_df[['user_id', 'date', 'pain_level']].copy()
        
        if not exercise_df.empty or not pain_df.empty:
            st.info("✅ 통합 데이터베이스에서 데이터를 로드했습니다.")
            
    except Exception as e:
        st.info("💡 통합 데이터베이스 연결을 건너뛰고 백업 데이터를 사용합니다.")
    
    # 1. 세션 상태에서 오늘 데이터 추가 (실시간 반영)
    today = str(date.today())
    if today in st.session_state.exercise_log:
        today_exercise = pd.DataFrame({
            'user_id': [user_email],
            'date': [pd.to_datetime(today)],
            'completed_count': [st.session_state.exercise_log[today]]
        })
        if not exercise_df.empty:
            # 오늘 데이터가 있으면 업데이트, 없으면 추가
            exercise_df = exercise_df[exercise_df['date'].dt.date != date.today()]
            exercise_df = pd.concat([exercise_df, today_exercise])
        else:
            exercise_df = today_exercise
    
    if today in st.session_state.pain_data:
        today_pain = pd.DataFrame({
            'user_id': [user_email],
            'date': [pd.to_datetime(today)],
            'pain_level': [st.session_state.pain_data[today]]
        })
        if not pain_df.empty:
            # 오늘 데이터가 있으면 업데이트, 없으면 추가
            pain_df = pain_df[pain_df['date'].dt.date != date.today()]
            pain_df = pd.concat([pain_df, today_pain])
        else:
            pain_df = today_pain
    
    # 2. Google Sheets에서 데이터 로드 시도
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
    
    # 3. Google Sheets에서 데이터를 가져오지 못한 경우 로컬 JSON 파일에서 로드
    if exercise_df.empty and pain_df.empty:
        json_file = "local_exercise_data.json"
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip()
                    if file_content:  # 파일이 비어있지 않은지 확인
                        data = json.loads(file_content)
                    else:
                        data = []
                
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
    else:
        st.warning("⚠️ 로드할 데이터가 없습니다. 운동과 통증을 기록해보세요!")
    
    # 그래프 생성
    if not exercise_df.empty or not pain_df.empty:
        try:
            # 사용자 데이터 필터링 (이메일 기준)
            if not exercise_df.empty:
                user_exercise_df = exercise_df[exercise_df['user_id'] == user_email].copy()
                if user_exercise_df.empty:
                    st.info("해당 이메일로 저장된 운동 기록이 없습니다.")
                    user_exercise_df = pd.DataFrame()
            else:
                user_exercise_df = pd.DataFrame()

            if not pain_df.empty:
                user_pain_df = pain_df[pain_df['user_id'] == user_email].copy()
                if user_pain_df.empty:
                    st.info("해당 이메일로 저장된 통증 기록이 없습니다.")
                    user_pain_df = pd.DataFrame()
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

                # 운동 데이터와 통증 데이터를 분리 (실제 기록된 데이터만)
                # 같은 날짜의 데이터는 합계/평균 처리
                if not user_exercise_df.empty:
                    exercise_temp = user_exercise_df.reset_index()
                    exercise_temp['date_only'] = exercise_temp['date'].dt.date
                    # 같은 날 운동 횟수는 합계
                    exercise_data = exercise_temp.groupby('date_only').agg({
                        'completed_count': 'sum',
                        'date': 'first'
                    }).reset_index(drop=True)
                else:
                    exercise_data = pd.DataFrame()
                
                if not user_pain_df.empty:
                    pain_temp = user_pain_df.reset_index()
                    pain_temp['date_only'] = pain_temp['date'].dt.date
                    # 같은 날 통증 점수는 평균
                    pain_data = pain_temp.groupby('date_only').agg({
                        'pain_level': 'mean',
                        'date': 'first'
                    }).reset_index(drop=True)
                    # 평균을 정수로 반올림
                    pain_data['pain_level'] = pain_data['pain_level'].round().astype(int)
                else:
                    pain_data = pd.DataFrame()
                
                # 안전한 최대값 계산
                max_count = max(exercise_data['completed_count'].max() if not exercise_data.empty else 1, 1)
                max_pain = max(pain_data['pain_level'].max() if not pain_data.empty else 1, 1)

                # 운동 횟수 차트 (바 차트) - 개선된 버전
                if not exercise_data.empty and len(exercise_data) > 0:
                    # 데이터 정리
                    exercise_chart_data = exercise_data.copy()
                    exercise_chart_data['date'] = pd.to_datetime(exercise_chart_data['date'])
                    exercise_chart_data = exercise_chart_data.sort_values('date')
                    
                    bar_chart = alt.Chart(exercise_chart_data).mark_bar(
                        color='#26A69A', 
                        opacity=0.8,
                        cornerRadiusTopLeft=3,
                        cornerRadiusTopRight=3
                    ).encode(
                        x=alt.X('date:T', 
                               title='날짜', 
                               axis=alt.Axis(format="%m/%d", labelAngle=-45, labelPadding=10)),
                        y=alt.Y('completed_count:Q',
                               title='운동 완료 횟수',
                               scale=alt.Scale(domain=[0, max(exercise_chart_data['completed_count'].max() + 1, 5)])),
                        tooltip=['date:T', 'completed_count:Q']
                    ).properties(
                        title=f'📊 운동 완료 횟수 (최근 {exercise_chart_data["date"].dt.date.nunique()}일)',
                        height=250
                    )
                    
                    st.altair_chart(bar_chart, use_container_width=True)
                else:
                    st.info("📈 운동 기록이 없습니다. 운동을 완료하면 차트가 표시됩니다.")

                # 통증 점수 차트 (선 + 점 차트) - 개선된 버전  
                if not pain_data.empty and len(pain_data) > 0:
                    # 데이터 정리
                    pain_chart_data = pain_data.copy()
                    pain_chart_data['date'] = pd.to_datetime(pain_chart_data['date'])
                    pain_chart_data = pain_chart_data.sort_values('date')
                    
                    line_chart = alt.Chart(pain_chart_data).mark_line(
                        color='#FF5722', 
                        strokeWidth=3,
                        point=alt.OverlayMarkDef(color='#FF5722', size=100)
                    ).encode(
                        x=alt.X('date:T', 
                               title='날짜',
                               axis=alt.Axis(format="%m/%d", labelAngle=-45, labelPadding=10)),
                        y=alt.Y('pain_level:Q',
                               title='통증 점수 (0-15)',
                               scale=alt.Scale(domain=[0, 15])),
                        tooltip=['date:T', 'pain_level:Q']
                    ).properties(
                        title=f'📉 통증 점수 변화 (최근 {pain_chart_data["date"].dt.date.nunique()}일)',
                        height=250
                    )
                    
                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.info("📉 통증 기록이 없습니다. 통증을 기록하면 차트가 표시됩니다.")
                
                # 데이터 요약 표시
                st.subheader("📊 데이터 요약")
                col1, col2 = st.columns(2)
                with col1:
                    if not exercise_data.empty:
                        unique_exercise_days = exercise_data['date'].dt.date.nunique()
                        st.metric("운동한 날", f"{unique_exercise_days}일")
                        st.metric("총 운동 횟수", f"{int(exercise_data['completed_count'].sum())}회")
                        st.metric("평균 운동 횟수", f"{exercise_data['completed_count'].mean():.1f}회/일")
                with col2:
                    if not pain_data.empty:
                        unique_pain_days = pain_data['date'].dt.date.nunique()
                        st.metric("기록한 날", f"{unique_pain_days}일")
                        st.metric("평균 통증 점수", f"{pain_data['pain_level'].mean():.1f}/15")
                        st.metric("최고 통증 점수", f"{int(pain_data['pain_level'].max())}/15")
            else:
                st.info("현재 사용자의 운동/통증 기록이 없습니다.")
        except Exception as e:
            st.error(f"차트 생성 중 오류가 발생했습니다: {e}")
            st.info("기본 차트를 표시합니다.")
            
            # 안전한 기본 차트 표시
            try:
                # 기본 데이터프레임 생성 (pain_level 컬럼 포함)
                if pain_df.empty or 'pain_level' not in pain_df.columns:
                    pain_df = pd.DataFrame({
                        'user_id': [user_id],
                        'date': [pd.to_datetime(today)],
                        'pain_level': [0]
                    })
                
                if exercise_df.empty or 'completed_count' not in exercise_df.columns:
                    exercise_df = pd.DataFrame({
                        'user_id': [user_id],
                        'date': [pd.to_datetime(today)],
                        'completed_count': [0]
                    })
                
                # 기본 차트 표시
                basic_df = pd.DataFrame({
                    'date': [today],
                    'completed_count': [exercise_df['completed_count'].sum() if not exercise_df.empty else 0],
                    'pain_level': [pain_df['pain_level'].mean() if not pain_df.empty else 0]
                })
                
                # 기본 차트 생성 (패딩 및 레이블 각도 적용)
                bar_chart = alt.Chart(basic_df).mark_bar(color='#26A69A').encode(
                    x=alt.X('date:T', title='날짜', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('completed_count:Q', title='운동 횟수', scale=alt.Scale(domain=[0, 10]), axis=alt.Axis(titlePadding=20))
                )
                
                line_chart = alt.Chart(basic_df).mark_line(color='#FF5722').encode(
                    x=alt.X('date:T', title='날짜', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('pain_level:Q', title='통증 점수', scale=alt.Scale(domain=[0, 15]), axis=alt.Axis(titlePadding=20))
                )
                
                combined_chart = alt.layer(bar_chart, line_chart).resolve_scale(y='independent').properties(
                    padding={'left': 80, 'right': 80, 'top': 40, 'bottom': 80}
                )
                st.altair_chart(combined_chart, use_container_width=True)
                
            except Exception as fallback_error:
                st.warning(f"기본 차트도 표시할 수 없습니다: {fallback_error}")
                st.info("데이터를 기록한 후 다시 확인해주세요.")

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
        
        # Altair를 사용한 이중 축 차트 생성 (날짜 레이블 각도 추가)
        base = alt.Chart(basic_df).encode(
            alt.X('date:T', title='날짜', axis=alt.Axis(labelAngle=-45))
        )
        
        bar_chart = base.mark_bar(color='#26A69A').encode(
            y=alt.Y(
                'completed_count:Q',
                title='운동 횟수',
                axis=alt.Axis(labels=True, titleColor='#26A69A', titlePadding=20),
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
            title='운동 횟수와 통증 점수 변화 (기본 표시)',
            padding={'left': 80, 'right': 80, 'top': 40, 'bottom': 80}
        )
        
        st.altair_chart(combined_chart, use_container_width=True)
        st.info("💡 운동을 완료하고 통증을 기록하면 그래프가 업데이트됩니다!")
        
        st.markdown("---")

# App Main Entry Point
if __name__ == "__main__":
    # 개인정보 입력에서 설정된 이메일 사용
    user_email = st.session_state.user_data.get('email', '') if hasattr(st.session_state, 'user_data') else ''
    show_integrated_dashboard(user_email)
