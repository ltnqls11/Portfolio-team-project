import streamlit as st
import pandas as pd
from datetime import date, timedelta

# ====================================================================
# Main App Function
# ====================================================================
def main():
    """Main function to run the Streamlit app with advanced pain tracking."""
    st.set_page_config(
        page_title="개발자 헬스케어 - 통증 추이 상세 분석",
        layout="wide"
    )

    st.title("💻 개발자 헬스케어 대시보드")
    st.markdown("---")

    # Initialize session state for pain data
    # The data structure now includes details: {'date': {'pain_level': int, 'body_part': str, 'pain_type': str}}
    if 'pain_data' not in st.session_state:
        st.session_state.pain_data = {}

    # ====================================================================
    # Pain Tracking Section
    # ====================================================================
    st.header("나의 통증 상세 기록하기")
    st.markdown("오늘의 통증 점수, 부위, 성질을 기록하고 변화를 확인하세요.")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Slider for pain level input (0-10 scale)
        if 'current_pain_level' not in st.session_state:
            st.session_state.current_pain_level = 0
            
        current_pain_level = st.slider(
            "오늘의 통증 점수 (0: 없음, 10: 심함)",
            0, 10, st.session_state.current_pain_level, key="level_slider"
        )
        st.session_state.current_pain_level = current_pain_level

    with col2:
        # Selectbox for body part
        body_part = st.selectbox(
            "통증 부위",
            ["선택", "목", "어깨", "허리", "손목", "손가락", "팔꿈치", "기타"]
        )

    with col3:
        # Selectbox for pain type
        pain_type = st.selectbox(
            "통증의 성질",
            ["선택", "뻐근함", "찌릿함", "묵직함", "쑤심", "저림", "화끈거림"]
        )

    # Button to save the pain level
    today_date = str(date.today())
    if st.button("통증 기록하기"):
        if body_part != "선택" and pain_type != "선택":
            st.session_state.pain_data[today_date] = {
                'pain_level': current_pain_level,
                'body_part': body_part,
                'pain_type': pain_type
            }
            st.success(f"오늘({today_date})의 통증 기록이 완료되었습니다! (점수: {current_pain_level}, 부위: {body_part}, 성질: {pain_type})")
        else:
            st.error("통증 부위와 성질을 모두 선택해 주세요.")
            
    st.markdown("---")

    # ====================================================================
    # Pain Trend Analysis Chart
    # ====================================================================
    st.header("나의 통증 분석 리포트")

    if st.session_state.pain_data:
        # Convert the dictionary to a pandas DataFrame for plotting
        pain_df = pd.DataFrame.from_dict(st.session_state.pain_data, orient='index')
        pain_df.index = pd.to_datetime(pain_df.index)
        pain_df = pain_df.sort_index()

        st.subheader("일별 통증 점수 추이")
        st.line_chart(pain_df, y='pain_level')
        
        # Provide some text feedback based on the trend
        if len(pain_df) > 1:
            last_pain = pain_df['pain_level'].iloc[-1]
            prev_pain = pain_df['pain_level'].iloc[-2]
            
            st.markdown("### 간단 분석")
            if last_pain > prev_pain:
                st.warning("어제보다 통증 점수가 올랐어요. 자세를 확인하거나 휴식 시간을 늘려보세요! 🚨")
            elif last_pain < prev_pain:
                st.success("통증 점수가 내려갔어요. 꾸준한 관리가 효과를 보고 있네요! 👍")
            else:
                st.info("통증 점수가 비슷합니다. 현재 상태를 유지하며 꾸준히 관리하세요. ✨")
        
        st.markdown("---")
        
        # ====================================================================
        # Weekly Average Pain Chart
        # ====================================================================
        st.subheader("주간 통증 평균")
        # Ensure there is enough data for weekly analysis
        if len(pain_df) > 6:
            # Resample daily data to weekly average
            weekly_avg_pain = pain_df['pain_level'].resample('W').mean().dropna()
            weekly_avg_pain.index = [f"{d.month}/{d.day}" for d in weekly_avg_pain.index]
            
            # Create a DataFrame for the bar chart
            weekly_df = pd.DataFrame(
                {'주간 평균 통증': weekly_avg_pain.values},
                index=weekly_avg_pain.index
            )
            st.bar_chart(weekly_df)
        else:
            st.info("주간 통증 평균을 보려면 7일 이상의 데이터가 필요합니다.")

    else:
        st.info("아직 기록된 통증 데이터가 없습니다. 위의 기록 항목을 채워 통증을 기록해 보세요.")

if __name__ == "__main__":
    main()
