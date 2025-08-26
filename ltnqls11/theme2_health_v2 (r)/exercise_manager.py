# 구글시트로 관리
# exercise_manager.py
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import random
import altair as alt

# Google Sheets 라이브러리 추가
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets 설정 ---
# Google Sheets URL을 입력하세요.
# https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"

# Google Sheets API 활성화 여부를 확인하는 플래그
# credentials.json 파일이 있어야만 True로 설정됩니다.
try:
    with open("credentials.json", "r") as f:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json",
            scopes=['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        )
    gc = gspread.authorize(credentials)
    # Google Sheet가 유효한지 확인합니다.
    worksheet = gc.open_by_url(GOOGLE_SHEET_URL).sheet1
    GOOGLE_SHEETS_ENABLED = True
    st.success("Google Sheets와 성공적으로 연결되었습니다.")
except Exception as e:
    st.error(f"Google Sheets 연결 오류: {e}. Google Sheets 기능을 비활성화합니다.")
    GOOGLE_SHEETS_ENABLED = False

# ====================================================================
# Data and Helper Functions
# ====================================================================

# VDT 증후군 증상 데이터
VDT_SYMPTOMS = {
    "거북목 증후군": {
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
    "라운드 숄더": {
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
            {"title": "라운드 숄더 교정 운동", "url": "https://www.youtube.com/watch?v=4dJ4K1z7n5o"}
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
    "손목터널 증후군": {
        "증상": ["손목 통증", "손가락 저림", "손 근력 약화"],
        "원인": ["반복적인 손목 사용", "부자연스러운 손목 각도"],
        "운동_추천": {
            "예방 (자세교정)": [
                {"name": "손목 스트레칭", "purpose": "손목 근육 이완", "method": "손목을 위아래로 구부리기", "reps": "10회씩 3세트", "caution": "통증 시 중단"},
                {"name": "손가락 펴기", "purpose": "손가락 근육 이완", "method": "손가락을 쭉 펴고 5초간 유지", "reps": "10회", "caution": "부드럽게 실시"}
            ],
            "운동 (근력 및 체력 증진)": [
                {"name": "손목 근력 강화", "purpose": "손목 주변 근육 강화", "method": "가벼운 무게로 손목 굽히기 운동", "reps": "15회 2세트", "caution": "무리하지 말 것"}
            ],
            "재활 (통증감소)": [
                {"name": "신경 활주 운동", "purpose": "신경 압박 완화", "method": "손목과 손가락을 천천히 펴고 구부리기", "reps": "10회씩 하루 3번", "caution": "저림이 심해지면 중단"}
            ]
        },
        "유튜브_영상_링크": [
            {"title": "손목 통증 스트레칭", "url": "https://www.youtube.com/watch?v=9D_r_z0i9pI"},
            {"title": "손목터널 증후군 예방", "url": "https://www.youtube.com/watch?v=G96q6sL3FhY"}
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

    # Get the current day of the year (1-366)
    day_of_year = date.today().timetuple().tm_yday
    
    # Use the day of the year to seed the random choice for deterministic daily selection
    random.seed(day_of_year)
    
    # Return a randomly selected video from the list
    return [random.choice(videos)]

# ====================================================================
# Google Sheets 로드 및 저장 함수
# ====================================================================

def load_data_from_google_sheets():
    """Google Sheets에서 모든 데이터를 불러와서 DataFrame으로 반환합니다."""
    if not GOOGLE_SHEETS_ENABLED:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        # 모든 데이터 가져오기
        all_data = worksheet.get_all_records()
        df = pd.DataFrame(all_data)

        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # 데이터프레임 분리
        exercise_df = df[df['data_type'] == 'exercise_log'].copy()
        pain_df = df[df['data_type'] == 'pain_data'].copy()
        point_df = df[df['data_type'] == 'point_data'].copy()

        # 필요한 열만 선택하고 인덱스 재설정
        if not exercise_df.empty:
            exercise_df = exercise_df[['user_id', 'date', 'completed_count']]
        if not pain_df.empty:
            pain_df = pain_df[['user_id', 'date', 'pain_level']]
        if not point_df.empty:
            point_df = point_df[['user_id', 'date', 'points_gained']]

        return exercise_df, pain_df, point_df

    except Exception as e:
        st.error(f"Google Sheets에서 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def save_to_google_sheets(data, data_type, user_id):
    """데이터를 Google Sheets에 저장합니다."""
    if not GOOGLE_SHEETS_ENABLED:
        st.error("Google Sheets가 비활성화되어 데이터를 저장할 수 없습니다.")
        return

    try:
        df = pd.DataFrame(worksheet.get_all_records())
        today = str(date.today())

        # 기존 데이터 찾기
        existing_row = df[(df['date'] == today) & (df['user_id'] == user_id) & (df['data_type'] == data_type)]

        if not existing_row.empty:
            # 기존 데이터 업데이트
            row_index = existing_row.index[0] + 2 # Google Sheets는 1부터 시작하고, 헤더 행이 1행
            for key, value in data.items():
                worksheet.update_cell(row_index, df.columns.get_loc(key) + 1, value)
        else:
            # 새 데이터 추가
            row_to_add = {**data, 'data_type': data_type, 'user_id': user_id, 'date': today}
            # DataFrame을 사용하여 열 순서 맞추기
            headers = worksheet.get_all_values()[0]
            new_row_list = [row_to_add.get(header, '') for header in headers]
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
    
    # 세션 상태에 운동 기록을 저장할 딕셔너리 초기화
    if 'selected_conditions' not in st.session_state:
        st.session_state.selected_conditions = []
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {}
    
    # 🌟 포인트 및 챌린지 관련 세션 상태 초기화
    if 'total_points' not in st.session_state:
        st.session_state.total_points = 0
    if 'last_exercise_date' not in st.session_state:
        st.session_state.last_exercise_date = None
    if 'consecutive_days' not in st.session_state:
        st.session_state.consecutive_days = 0

    today_date = str(date.today())

    # Google Sheets에서 데이터 로드
    exercise_df, pain_df, point_df = load_data_from_google_sheets()

    # 🌟 누적 포인트 계산
    if not point_df.empty:
        total_points = point_df['points_gained'].astype(int).sum()
        st.session_state.total_points = total_points
    else:
        st.session_state.total_points = 0

    # ====================================================================
    # 포인트 및 챌린지 현황
    # ====================================================================
    st.subheader("🎉 나의 건강 목표")
    st.markdown(f"**현재까지 누적 포인트:** **{st.session_state.total_points}** 점")
    st.markdown(f"**연속 운동일:** **{st.session_state.consecutive_days}** 일")
    st.markdown("---")

    # ====================================================================
    # 증상 선택 섹션
    # ====================================================================
    st.subheader("🔎 현재 겪고 있는 증상을 선택해주세요")
    symptom_options = list(VDT_SYMPTOMS.keys())
    selected_conditions = st.multiselect(
        "증상을 선택해주세요:",
        symptom_options,
        default=st.session_state.selected_conditions
    )
    st.session_state.selected_conditions = selected_conditions
    
    st.markdown("---")

    # ====================================================================
    # 오늘의 루틴 섹션 (사용자가 선택한 증상에 따라 동적으로 생성)
    # ====================================================================
    st.subheader("🏃‍♂️ 오늘의 루틴")
    if not st.session_state.selected_conditions:
        st.info("먼저 위에서 증상을 하나 이상 선택해 주세요.")
    else:
        for condition in st.session_state.selected_conditions:
            st.markdown(f"**🔹 {condition}**")
            
            # YouTube 영상 추천 (매일 다른 영상)
            videos = get_exercise_videos(condition)
            if videos:
                st.markdown("**📹 오늘의 추천 영상:**")
                for video in videos:
                    st.video(video['url'])
                    # 유튜브 영상 완료 체크박스 추가
                    video_key = f"completed_video_{today_date}_{video['title']}"
                    if video_key not in st.session_state.checkbox_states:
                        st.session_state.checkbox_states[video_key] = False
                    st.session_state.checkbox_states[video_key] = st.checkbox(
                        f"**{video['title']}** 영상 시청 완료",
                        value=st.session_state.checkbox_states[video_key],
                        key=video_key
                    )
            
            # 운동 루틴 (VDT_SYMPTOMS에서 가져온 상세 정보 표시)
            if "운동_추천" in VDT_SYMPTOMS[condition]:
                exercises = VDT_SYMPTOMS[condition]["운동_추천"]
                for purpose, exercise_list in exercises.items():
                    st.markdown(f"**✨ {purpose} 운동**")
                    for exercise in exercise_list:
                        # 고유한 체크박스 키 생성
                        unique_key = f"completed_exercise_{today_date}_{condition}_{exercise['name']}"
                        
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
                            - **주의:** {exercise['caution']}
                            """
                        )
            
            st.markdown("---")
            
    # 운동 완료 버튼
    if st.button("💪 운동 완료 기록"):
        completed_exercises = []
        # 모든 체크박스를 순회하며 완료된 운동을 기록
        for key, value in st.session_state.checkbox_states.items():
            if value and key.startswith(f"completed_exercise_{today_date}"):
                completed_exercises.append(key)
        
        # 유튜브 영상 체크박스도 포함
        for key, value in st.session_state.checkbox_states.items():
            if value and key.startswith(f"completed_video_{today_date}"):
                completed_exercises.append(key)
        
        if completed_exercises:
            # 🌟 운동 완료 시 포인트 적립
            points_gained = len(completed_exercises) * 5 # 운동 1개당 5포인트
            st.success(f"운동 완료! 🎉 {points_gained} 포인트를 획득했습니다.")
            
            # 🌟 연속 운동 챌린지 확인
            today = date.today()
            if st.session_state.last_exercise_date:
                last_date = datetime.strptime(st.session_state.last_exercise_date, '%Y-%m-%d').date()
                if last_date == today - timedelta(days=1):
                    # 연속 운동 성공!
                    st.session_state.consecutive_days = st.session_state.get('consecutive_days', 0) + 1
                    if st.session_state.consecutive_days >= 3:
                        st.balloons()
                        st.info(f"축하합니다! 🏆 {st.session_state.consecutive_days}일 연속 운동 챌린지 성공!")
                elif last_date != today:
                    # 연속 운동 실패
                    st.session_state.consecutive_days = 1
            else:
                st.session_state.consecutive_days = 1
            
            st.session_state.last_exercise_date = str(today)

            # Google Sheets에 운동 기록 및 포인트 저장
            save_to_google_sheets({'completed_count': len(completed_exercises)}, 'exercise_log', user_id)
            save_to_google_sheets({'points_gained': points_gained}, 'point_data', user_id)

    # ====================================================================
    # 통증 기록 섹션
    # ====================================================================
    st.subheader("🏥 나의 통증 기록하기")
    current_pain_level = st.slider(
        "오늘의 통증 점수 (0: 없음, 15: 심함)",
        0, 15, key="pain_slider"
    )
    if st.button("통증 기록 저장"):
        # Google Sheets에 통증 점수 및 포인트 저장
        save_to_google_sheets({'pain_level': current_pain_level}, 'pain_data', user_id)
        st.success(f"통증 기록이 저장되었습니다.")
        save_to_google_sheets({'points_gained': 2}, 'point_data', user_id) # 통증 기록 시 2포인트 추가

    st.markdown("---")

    # ====================================================================
    # 통증·운동 리포트 시각화
    # ====================================================================
    st.subheader("📈 통증·운동 리포트")
    
    if not exercise_df.empty or not pain_df.empty:
        # 두 데이터프레임의 인덱스를 통합하여 결합
        exercise_df['date'] = pd.to_datetime(exercise_df['date'])
        pain_df['date'] = pd.to_datetime(pain_df['date'])
        
        exercise_df = exercise_df.set_index('date')
        pain_df = pain_df.set_index('date')
        
        combined_index = exercise_df.index.union(pain_df.index)
        combined_df = pd.DataFrame(index=combined_index)
        
        combined_df = combined_df.join(exercise_df[['completed_count']]).join(pain_df[['pain_level']]).fillna(0)
        combined_df = combined_df.reset_index()
        combined_df = combined_df.rename(columns={'index': 'date'})

        # 이중 축 차트 생성 (Altair 사용)
        base = alt.Chart(combined_df).encode(
            alt.X('date:T', title='날짜')
        )

        bar_chart = base.mark_bar(color='#26A69A').encode(
            y=alt.Y('completed_count:Q', title='운동 횟수', axis=alt.Axis(labels=True, titleColor='#26A69A'), scale=alt.Scale(domain=[0, combined_df['completed_count'].max() + 2]))
        )
        
        line_chart = base.mark_line(color='#FF5722').encode(
            y=alt.Y('pain_level:Q', title='통증 점수', axis=alt.Axis(labels=True, titleColor='#FF5722'), scale=alt.Scale(domain=[0, 15]))
        )

        point_chart = base.mark_point(
            color='#FF5722',
            size=100,
            filled=True,
        ).encode(
            y=alt.Y('pain_level:Q', title='통증 점수', axis=alt.Axis(labels=True, titleColor='#FF5722'), scale=alt.Scale(domain=[0, 15])),
            tooltip=[alt.Tooltip('date:T', title='날짜'), alt.Tooltip('pain_level:Q', title='통증 점수')]
        )

        combined_chart = alt.layer(bar_chart, line_chart, point_chart).resolve_scale(
            y='independent'
        ).properties(
            title='운동 횟수와 통증 점수 변화'
        )
        
        st.altair_chart(combined_chart, use_container_width=True)

    else:
        st.info("운동 기록 및 통증 기록이 부족합니다. 루틴을 완료하고 통증을 기록해 보세요.")

    st.markdown("---")

    # ====================================================================
    # 🌟 일별 포인트 리포트 시각화
    # ====================================================================
    st.subheader("💰 포인트 획득 리포트")
    
    if not point_df.empty:
        point_df['date'] = pd.to_datetime(point_df['date'])
        
        # 일별 획득 포인트 막대 차트
        point_chart = alt.Chart(point_df).mark_bar(color='#4CAF50').encode(
            x=alt.X('date:T', title='날짜'),
            y=alt.Y('points_gained:Q', title='획득 포인트', axis=alt.Axis(labels=True, titleColor='#4CAF50')),
            tooltip=[alt.Tooltip('date:T', title='날짜'), alt.Tooltip('points_gained:Q', title='획득 포인트')]
        ).properties(
            title='일별 획득 포인트 변화'
        )
        
        st.altair_chart(point_chart, use_container_width=True)
    else:
        st.info("획득 포인트 기록이 부족합니다. 운동을 완료하고 포인트를 쌓아보세요.")

# ====================================================================
# App Main Entry Point
# ====================================================================
if __name__ == "__main__":
    # 실제 앱에서는 인증 후 얻은 user_id를 여기에 전달해야 합니다.
    user_id = "your_authenticated_user_id"
    show_integrated_dashboard(user_id)
