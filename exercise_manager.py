import streamlit as st
import pandas as pd
from datetime import date
import random
import altair as alt

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
# 페이지 함수
# ====================================================================

def show_integrated_dashboard():
    """
    통합 대시보드 기능을 보여주는 페이지입니다.
    """
    st.header("💻 통합 건강 대시보드")
    st.markdown("오늘의 운동 루틴을 완료하고, 통증을 기록하며 건강을 관리하세요.")
    
    # 세션 상태에 운동 기록을 저장할 딕셔너리 초기화
    if 'exercise_log' not in st.session_state:
        st.session_state.exercise_log = {}
    if 'selected_conditions' not in st.session_state:
        st.session_state.selected_conditions = []
    if 'pain_data' not in st.session_state:
        st.session_state.pain_data = {}
    if 'checkbox_states' not in st.session_state:
        st.session_state.checkbox_states = {}

    today_date = str(date.today())

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
        
        # 오늘 날짜로 완료된 운동 목록을 저장
        st.session_state.exercise_log[today_date] = completed_exercises
        
        st.success(f"오늘({today_date}) 총 {len(completed_exercises)}개의 운동을 완료했습니다!")

    # ====================================================================
    # 통증 기록 섹션
    # ====================================================================
    st.subheader("🏥 나의 통증 기록하기")
    current_pain_level = st.slider(
        "오늘의 통증 점수 (0: 없음, 15: 심함)",
        0, 15, key="pain_slider"
    )
    if st.button("통증 기록 저장"):
        st.session_state.pain_data[today_date] = {'pain_level': current_pain_level}
        st.success(f"오늘({today_date})의 통증 점수 {current_pain_level}점이 기록되었습니다.")

    st.markdown("---")

    # ====================================================================
    # 통증·운동 리포트 시각화 (하나의 차트로 통합)
    # ====================================================================
    st.subheader("📈 통증·운동 리포트")
    
    if st.session_state.exercise_log or st.session_state.pain_data:
        # 운동 기록 DataFrame 생성
        exercise_dates = list(st.session_state.exercise_log.keys())
        exercise_df = pd.DataFrame(
            {'date': pd.to_datetime(exercise_dates), 'completed_count': [len(v) for v in st.session_state.exercise_log.values()]}
        )
        if not exercise_df.empty:
            exercise_df = exercise_df.set_index('date').sort_index()

        # 통증 기록 DataFrame 생성
        if st.session_state.pain_data:
            pain_series = pd.Series({pd.to_datetime(k): v['pain_level'] for k, v in st.session_state.pain_data.items()})
            pain_df = pain_series.to_frame(name='pain_level')
            
        else:
            pain_df = pd.DataFrame()
        
        # 데이터프레임 결합 및 차트 표시
        if not exercise_df.empty or not pain_df.empty:
            combined_df = pain_df.join(exercise_df, how='outer').fillna(0)
            combined_df = combined_df.reset_index()

            # 이중 축 차트 생성 (Altair 사용)
            base = alt.Chart(combined_df).encode(
                alt.X('index:T', title='날짜')
            )

            bar_chart = base.mark_bar(color='#26A69A').encode(
                y=alt.Y('completed_count:Q', title='운동 횟수', axis=alt.Axis(labels=True, titleColor='#26A69A'), scale=alt.Scale(domain=[0, 15]))
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
                tooltip=[alt.Tooltip('index:T', title='날짜'), alt.Tooltip('pain_level:Q', title='통증 점수')]
            )

            combined_chart = alt.layer(bar_chart, line_chart, point_chart).resolve_scale(
                y='independent'
            ).properties(
                title='운동 횟수와 통증 점수 변화'
            )
            
            st.altair_chart(combined_chart, use_container_width=True)

        else:
            st.info("운동 기록 및 통증 기록이 부족합니다. 루틴을 완료하고 통증을 기록해 보세요.")
    else:
        st.info("운동 기록 및 통증 기록이 부족합니다. 루틴을 완료하고 통증을 기록해 보세요.")

# ====================================================================
# App Main Entry Point
# ====================================================================
if __name__ == "__main__":
    show_integrated_dashboard()
