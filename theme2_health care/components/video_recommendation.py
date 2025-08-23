import streamlit as st
import pandas as pd
from datetime import datetime
import json

def show_video_recommendations(condition, purpose="예방", user_data=None):
    """향상된 추천 영상 표시 시스템"""
    
    st.subheader("📹 추천 영상")
    
    # Supabase에서 분석된 데이터 가져오기 시도
    try:
        from database import get_analyzed_videos_for_condition
        analyzed_videos = get_analyzed_videos_for_condition(condition, purpose, limit=10)
        
        if analyzed_videos:
            # 분석된 비디오가 있는 경우
            st.success(f"✨ **당신을 위한 최적의 운동**은 총 {len(analyzed_videos)}개가 검색되었습니다.")
            st.info("🏆 **이 중 다음 3개를 가장 추천합니다:**")
            
            # 상위 3개 추천 영상 표시
            top_3_videos = analyzed_videos[:3]
            
            for i, video in enumerate(top_3_videos, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # 제목과 하이퍼링크
                        video_title = video.get('title', '제목 없음')
                        video_url = video.get('url', '#')
                        
                        st.markdown(f"**{i}. [{video_title}]({video_url})**")
                        
                        # 채널명, 시간, 조회수 정보
                        channel = video.get('channel_name', '알 수 없음')
                        duration = format_duration_korean(video.get('duration_seconds', 0))
                        views = format_view_count_korean(video.get('view_count', 0))
                        
                        st.caption(f"📺 {channel} | ⏱️ {duration} | 👀 {views}")
                        
                        # AI 분석 점수가 있는 경우
                        if video.get('quality_score'):
                            quality_score = video.get('quality_score', 0)
                            st.progress(quality_score / 100, text=f"품질 점수: {quality_score}/100")
                    
                    with col2:
                        # 썸네일 또는 추가 정보
                        if video.get('thumbnail_url'):
                            st.image(video['thumbnail_url'], width=120)
                        else:
                            st.info("🎥")
                    
                    st.markdown("---")
            
            # 추가 영상 보기 옵션
            if len(analyzed_videos) > 3:
                with st.expander(f"🔍 추가 영상 {len(analyzed_videos) - 3}개 더 보기"):
                    for video in analyzed_videos[3:]:
                        video_title = video.get('title', '제목 없음')
                        video_url = video.get('url', '#')
                        channel = video.get('channel_name', '알 수 없음')
                        duration = format_duration_korean(video.get('duration_seconds', 0))
                        views = format_view_count_korean(video.get('view_count', 0))
                        
                        st.markdown(f"• [{video_title}]({video_url})")
                        st.caption(f"📺 {channel} | ⏱️ {duration} | 👀 {views}")
        else:
            # 분석된 데이터가 없는 경우 기본 추천
            show_fallback_recommendations(condition, purpose)
            
    except Exception as e:
        # 데이터베이스 연결 실패 시 기본 추천
        st.warning("⚠️ 개인화된 추천을 가져올 수 없어 기본 추천을 표시합니다.")
        show_fallback_recommendations(condition, purpose)

def show_fallback_recommendations(condition, purpose):
    """기본 추천 영상 (백업용)"""
    
    # YouTube 실시간 검색 시도
    try:
        from youtube_collector import search_youtube_videos
        from app import generate_search_keywords
        
        search_keywords = generate_search_keywords(condition, purpose)
        youtube_videos = []
        
        for keyword in search_keywords[:2]:
            videos = search_youtube_videos(keyword, max_results=5)
            youtube_videos.extend(videos)
        
        if youtube_videos:
            st.success(f"🔍 **실시간 검색**으로 총 {len(youtube_videos)}개의 운동 영상을 찾았습니다.")
            st.info("🎯 **추천 영상 3개:**")
            
            for i, video in enumerate(youtube_videos[:3], 1):
                video_title = video.get('title', '제목 없음')
                video_url = f"https://www.youtube.com/watch?v={video.get('video_id', '')}"
                channel = video.get('channel_name', '알 수 없음')
                duration = format_duration_korean(video.get('duration_seconds', 0))
                views = format_view_count_korean(video.get('view_count', 0))
                
                st.markdown(f"**{i}. [{video_title}]({video_url})**")
                st.caption(f"📺 {channel} | ⏱️ {duration} | 👀 {views}")
                st.markdown("---")
        else:
            # 최종 백업: 정적 추천
            show_static_recommendations(condition)
            
    except Exception:
        show_static_recommendations(condition)

def show_static_recommendations(condition):
    """정적 추천 영상 (최종 백업)"""
    
    static_videos = {
        "거북목": [
            {
                "title": "거북목 교정 운동 5분 루틴",
                "url": "https://youtu.be/8hlp5u8m_Ao",
                "channel": "핏블리",
                "duration": "5:23",
                "views": "120만"
            },
            {
                "title": "목 스트레칭 완벽 가이드",
                "url": "https://youtu.be/2NOJ1RKqvzI",
                "channel": "힐링요가",
                "duration": "8:15",
                "views": "85만"
            },
            {
                "title": "거북목 교정 운동법",
                "url": "https://youtu.be/4QhQZr6Qb6E",
                "channel": "김계란",
                "duration": "10:30",
                "views": "200만"
            }
        ],
        "라운드숄더": [
            {
                "title": "라운드숄더 교정 운동",
                "url": "https://youtu.be/oLwTC-lAJws",
                "channel": "바디체크",
                "duration": "7:45",
                "views": "95만"
            },
            {
                "title": "어깨 스트레칭 루틴",
                "url": "https://youtu.be/akgQbxhrhOc",
                "channel": "필라테스TV",
                "duration": "6:20",
                "views": "67만"
            },
            {
                "title": "라운드숄더 교정법",
                "url": "https://youtu.be/4QhQZr6Qb6E",
                "channel": "김계란",
                "duration": "12:15",
                "views": "180만"
            }
        ]
    }
    
    videos = static_videos.get(condition, static_videos["거북목"])
    
    st.info("📚 **기본 추천 영상:**")
    
    for i, video in enumerate(videos, 1):
        st.markdown(f"**{i}. [{video['title']}]({video['url']})**")
        st.caption(f"📺 {video['channel']} | ⏱️ {video['duration']} | 👀 {video['views']} 조회")
        st.markdown("---")

def format_duration_korean(seconds):
    """초를 한국어 시간 형식으로 변환"""
    if seconds == 0:
        return "정보 없음"
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}시간 {minutes}분"
    else:
        return f"{minutes}분 {seconds}초"

def format_view_count_korean(count):
    """조회수를 한국어 형식으로 변환"""
    if count >= 100000000:  # 1억 이상
        return f"{count/100000000:.1f}억"
    elif count >= 10000:    # 1만 이상
        return f"{count/10000:.1f}만"
    elif count >= 1000:     # 1천 이상
        return f"{count/1000:.1f}천"
    else:
        return str(count)

def get_video_recommendations_data(condition, purpose, user_data=None):
    """추천 영상 데이터를 반환하는 함수 (다른 모듈에서 사용)"""
    try:
        from database import get_analyzed_videos_for_condition
        return get_analyzed_videos_for_condition(condition, purpose, limit=10)
    except:
        return []
