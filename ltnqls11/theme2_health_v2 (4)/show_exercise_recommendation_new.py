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
    
    exercise_purpose = st.selectbox("운동 목적을 선택하세요", ["예방 (자세교정)", "운동 (근력 및 체력 증진)", "재활 (통증감소)"])
    rest_time = calculate_rest_time(st.session_state.user_data.get('work_intensity', '보통'))
    st.info(f"⏰ **권장 휴식시간**: {rest_time}분마다")
    
    # 2개 탭만 사용: 전문 AI 상담, 추천 영상
    tab1, tab2 = st.tabs(["🤖 전문 AI와 상담하기", "📺 맞춤 운동 영상 추천"])
    
    with tab1:
        st.subheader("👩‍⚕️ 전문 재활의학과 전문의와 실시간 상담")
        st.info("🎯 위 분석 결과를 바탕으로 더 자세한 상담을 원하시면 아래 채팅을 이용해주세요.")
        
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
            
            # AI 응답 생성
            if GEMINI_AVAILABLE and GEMINI_API_KEY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # 전문의 역할 프롬프트
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
                    st.warning("🤖 AI 상담 기능을 사용하려면 Gemini API 키를 설정해주세요.")
        
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
                # 다음 탭으로 이동 (실제로는 상단 탭 클릭을 강제할 수 없으므로 메시지로 안내)
                st.success("👆 위의 '맞춤 운동 영상 추천' 탭을 클릭해주세요!")
        
        with col2:
            if st.button("🎆 상담 완료 - 다음 단계로", key="consultation_complete"):
                st.session_state.steps_completed[4] = True  # 5번째 단계 완료
                st.session_state.current_step = 5
                st.session_state.next_menu = "휴식 알리미 설정"
                st.success("✅ 맞춤형 운동 상담이 완료되었습니다!")
                st.rerun()
    
    with tab2:
        st.subheader("📺 YouTube 영상 기반 주간 운동 계획")
        
        # 운동 스케줄 기반 주간 계획 생성
        exercise_schedule = st.session_state.get('exercise_schedule', {})
        if exercise_schedule:
            weekly_plan = create_video_based_weekly_schedule(
                exercise_schedule, 
                st.session_state.selected_conditions, 
                pain_scores, 
                exercise_purpose
            )
            
            if weekly_plan:
                st.success("✅ 개인 맞춤 주간 운동 계획이 생성되었습니다!")
                
                # 주간 계획 표시
                for day, plan in weekly_plan.items():
                    with st.expander(f"📅 {day} 운동 계획 ({plan['total_minutes']}분)"):
                        st.markdown(f"**🏃‍♀️ 메인 운동 ({plan['main_exercise_minutes']}분):**")
                        
                        for i, video in enumerate(plan['main_videos'], 1):
                            st.markdown(f"""
                            **{i}. {video['condition']} - [{video['title']}]({video['url']})**
                            - 📺 채널: {video['channel']}
                            - ⏱️ 시간: {video['duration']} ({video['minutes']}분)
                            """)
                        
                        st.markdown(f"**🧘‍♀️ 마무리 스트레칭 ({plan['stretching_minutes']}분):**")
                        st.markdown("- 5분: 워밍업 스트레칭")
                        st.markdown(f"- {plan['cool_down_minutes']}분: 마무리 스트레칭 및 이완")
                
                # 주간 총 운동량 요약
                total_videos = sum([len(plan['main_videos']) for plan in weekly_plan.values()])
                total_minutes = sum([plan['total_minutes'] for plan in weekly_plan.values()])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("주간 운동 일수", f"{len(weekly_plan)}일")
                with col2:
                    st.metric("주간 총 영상 수", f"{total_videos}개")
                with col3:
                    st.metric("주간 총 운동 시간", f"{total_minutes}분")
        
        # 각 증상별 추천 영상도 추가로 표시
        st.markdown("---")
        st.subheader("📋 증상별 추가 추천 영상")
        
        for condition in st.session_state.selected_conditions:
            st.write(f"### {condition} 관련 영상")
            
            # Supabase에서 전체 비디오 가져오기 (최대 10개)
            all_videos = get_enhanced_exercise_videos(condition, exercise_purpose, limit=10)
            
            if all_videos:
                # 총 영상 개수 표시
                st.info(f"🎯 현재 상태를 바탕으로 추천하는 영상은 총 **{len(all_videos)}개** 입니다.")
                
                # 상위 3개 영상 강조 표시
                st.success(f"⭐ 이 중 가장 우선적으로 추천하는 영상 3개:")
                
                # 상위 3개 영상 표시
                top_videos = all_videos[:3]
                for i, video in enumerate(top_videos, 1):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                            duration = video.get('duration', video.get('duration_seconds', '정보없음'))
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
                            st.markdown(f"**{i}. [{video.get('title', '제목 없음')}]({video.get('url', '#')})**")
                            duration = video.get('duration', video.get('duration_seconds', '정보없음'))
                            if isinstance(duration, int):
                                duration = format_duration(duration)
                            channel = video.get('channel_name', '알 수 없음')
                            st.caption(f"📺 {channel} | ⏱️ {duration}")
            else:
                st.warning("🔍 현재 조건에 맞는 영상을 찾을 수 없습니다. 다른 운동 목적을 선택해보세요.")
        
        # 영상 추천 완료 후 다음 단계로
        st.markdown("---")
        if st.button("✅ 영상 추천 완료 - 다음 단계로", key="video_complete", type="primary"):
            st.session_state.steps_completed[4] = True
            st.session_state.current_step = 5
            st.session_state.next_menu = "휴식 알리미 설정"
            st.success("✅ 맞춤 운동 영상 추천이 완료되었습니다!")
            st.rerun()