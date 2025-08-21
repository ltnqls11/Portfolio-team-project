import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# 광고 모듈 import (개발자용)
try:
    from ads import show_adsense_banner, show_healthcare_product_recommendation, show_general_healthcare_products
except ImportError:
    # 모듈이 없을 경우 더미 함수로 대체
    def show_adsense_banner():
        st.markdown("<!-- Google AdSense 광고 위치 -->")
        st.info("📢 광고 영역")
    
    def show_healthcare_product_recommendation(condition):
        st.info("🛒 헬스케어 제품 추천 기능을 사용하려면 ads.py 모듈이 필요합니다.")
    
    def show_general_healthcare_products():
        st.info("🛒 일반 헬스케어 제품 추천 기능을 사용하려면 ads.py 모듈이 필요합니다.")

# 페이지 설정
st.set_page_config(
    page_title="개발자 헬스케어 - VDT 증후군 관리",
    page_icon="💻",
    layout="wide"
)

# 세션 상태 초기화
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'selected_conditions' not in st.session_state:
    st.session_state.selected_conditions = []
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False

def calculate_rest_time(work_intensity):
    """Murrel의 공식을 적용한 휴식시간 계산"""
    intensity_map = {
        "가벼움": 30,  # 30분마다 휴식
        "보통": 25,    # 25분마다 휴식
        "높음": 20,    # 20분마다 휴식
        "매우 높음": 15 # 15분마다 휴식
    }
    return intensity_map.get(work_intensity, 25)

def get_exercises_for_condition(condition, purpose):
    """증상별 운동 추천"""
    exercises_db = {
        "거북목": {
            "예방 (자세교정)": [
                {
                    "name": "목 스트레칭",
                    "purpose": "목 근육 이완 및 자세 교정",
                    "method": "고개를 천천히 좌우로 돌리고, 앞뒤로 숙이기",
                    "reps": "각 방향 10초씩 3회",
                    "caution": "급격한 움직임 금지"
                },
                {
                    "name": "어깨 으쓱하기",
                    "purpose": "어깨 긴장 완화",
                    "method": "어깨를 귀 쪽으로 올렸다가 천천히 내리기",
                    "reps": "10회 3세트",
                    "caution": "천천히 부드럽게 실시"
                }
            ],
            "운동 (근력 및 체력 증진)": [
                {
                    "name": "목 근력 강화",
                    "purpose": "목 주변 근육 강화",
                    "method": "손으로 이마를 누르며 목으로 저항하기",
                    "reps": "10초씩 5회",
                    "caution": "과도한 힘 사용 금지"
                }
            ],
            "재활 (통증감소)": [
                {
                    "name": "온찜질 후 스트레칭",
                    "purpose": "통증 완화 및 혈액순환 개선",
                    "method": "따뜻한 수건으로 목을 찜질 후 가벼운 스트레칭",
                    "reps": "15분 찜질 후 스트레칭",
                    "caution": "통증이 심할 때는 중단"
                }
            ]
        },
        "라운드숄더": {
            "예방 (자세교정)": [
                {
                    "name": "가슴 스트레칭",
                    "purpose": "가슴 근육 이완으로 어깨 교정",
                    "method": "벽에 손을 대고 몸을 앞으로 기울이기",
                    "reps": "30초씩 3회",
                    "caution": "무리하지 않는 범위에서"
                },
                {
                    "name": "어깨날개 모으기",
                    "purpose": "등 근육 강화",
                    "method": "양쪽 어깨날개를 등 중앙으로 모으기",
                    "reps": "10초씩 10회",
                    "caution": "어깨를 올리지 말고 실시"
                }
            ],
            "운동 (근력 및 체력 증진)": [
                {
                    "name": "등 근력 강화",
                    "purpose": "등 근육 강화로 자세 개선",
                    "method": "양팔을 뒤로 당기며 어깨날개 모으기",
                    "reps": "15회 3세트",
                    "caution": "천천히 정확한 자세로"
                }
            ],
            "재활 (통증감소)": [
                {
                    "name": "부드러운 어깨 회전",
                    "purpose": "어깨 관절 가동성 개선",
                    "method": "어깨를 천천히 앞뒤로 회전시키기",
                    "reps": "각 방향 10회씩",
                    "caution": "통증 범위 내에서만"
                }
            ]
        },
        "허리디스크": {
            "예방 (자세교정)": [
                {
                    "name": "허리 스트레칭",
                    "purpose": "허리 근육 이완",
                    "method": "의자에 앉아 상체를 좌우로 비틀기",
                    "reps": "각 방향 15초씩",
                    "caution": "천천히 부드럽게"
                },
                {
                    "name": "골반 기울이기",
                    "purpose": "허리 곡선 정상화",
                    "method": "의자에 앉아 골반을 앞뒤로 기울이기",
                    "reps": "10회씩 3세트",
                    "caution": "과도하게 하지 말 것"
                }
            ],
            "운동 (근력 및 체력 증진)": [
                {
                    "name": "코어 강화",
                    "purpose": "허리 지지 근육 강화",
                    "method": "배에 힘을 주고 10초간 유지",
                    "reps": "10초씩 10회",
                    "caution": "호흡을 멈추지 말 것"
                }
            ],
            "재활 (통증감소)": [
                {
                    "name": "무릎 가슴으로 당기기",
                    "purpose": "허리 근육 이완",
                    "method": "앉아서 한쪽 무릎을 가슴으로 당기기",
                    "reps": "각 다리 30초씩",
                    "caution": "통증이 있으면 중단"
                }
            ]
        },
        "손목터널증후군_왼쪽": {
            "예방 (자세교정)": [
                {
                    "name": "손목 스트레칭",
                    "purpose": "손목 근육 이완",
                    "method": "손목을 위아래로 구부리기",
                    "reps": "10회씩 3세트",
                    "caution": "통증 시 중단"
                },
                {
                    "name": "손가락 펴기",
                    "purpose": "손가락 근육 이완",
                    "method": "손가락을 쭉 펴고 5초간 유지",
                    "reps": "10회",
                    "caution": "부드럽게 실시"
                }
            ],
            "운동 (근력 및 체력 증진)": [
                {
                    "name": "손목 근력 강화",
                    "purpose": "손목 주변 근육 강화",
                    "method": "가벼운 무게로 손목 굽히기 운동",
                    "reps": "15회 2세트",
                    "caution": "무리하지 말 것"
                }
            ],
            "재활 (통증감소)": [
                {
                    "name": "신경 활주 운동",
                    "purpose": "신경 압박 완화",
                    "method": "손목과 손가락을 천천히 펴고 구부리기",
                    "reps": "10회씩 하루 3번",
                    "caution": "저림이 심해지면 중단"
                }
            ]
        },
        "손목터널증후군_오른쪽": {
            "예방 (자세교정)": [
                {
                    "name": "손목 스트레칭",
                    "purpose": "손목 근육 이완",
                    "method": "손목을 위아래로 구부리기",
                    "reps": "10회씩 3세트",
                    "caution": "통증 시 중단"
                },
                {
                    "name": "손가락 펴기",
                    "purpose": "손가락 근육 이완",
                    "method": "손가락을 쭉 펴고 5초간 유지",
                    "reps": "10회",
                    "caution": "부드럽게 실시"
                }
            ],
            "운동 (근력 및 체력 증진)": [
                {
                    "name": "손목 근력 강화",
                    "purpose": "손목 주변 근육 강화",
                    "method": "가벼운 무게로 손목 굽히기 운동",
                    "reps": "15회 2세트",
                    "caution": "무리하지 말 것"
                }
            ],
            "재활 (통증감소)": [
                {
                    "name": "신경 활주 운동",
                    "purpose": "신경 압박 완화",
                    "method": "손목과 손가락을 천천히 펴고 구부리기",
                    "reps": "10회씩 하루 3번",
                    "caution": "저림이 심해지면 중단"
                }
            ]
        }
    }
    
    return exercises_db.get(condition, {}).get(purpose, [])

def get_exercise_videos(condition):
    """운동 영상 추천 (김계란 유튜브 포함)"""
    videos_db = {
        "거북목": [
            {"title": "거북목 교정 운동 5분", "url": "https://youtu.be/8hlp5u8m_Ao"},
            {"title": "목 스트레칭 완벽 가이드", "url": "https://youtu.be/2NOJ1RKqvzI"},
            {"title": "김계란 - 거북목 교정 루틴", "url": "https://youtu.be/4QhQZr6Qb6E"}
        ],
        "라운드숄더": [
            {"title": "라운드숄더 교정 운동", "url": "https://youtu.be/oLwTC-lAJws"},
            {"title": "어깨 스트레칭 루틴", "url": "https://youtu.be/akgQbxhrhOc"},
            {"title": "김계란 - 라운드숄더 교정법", "url": "https://youtu.be/4QhQZr6Qb6E"}
        ],
        "허리디스크": [
            {"title": "허리 강화 운동", "url": "https://youtu.be/4BOTvaRaDjI"},
            {"title": "허리 디스크 예방 운동", "url": "https://youtu.be/DWmGArQBtFI"},
            {"title": "김계란 - 허리 건강 루틴", "url": "https://youtu.be/4QhQZr6Qb6E"}
        ],
        "손목터널증후군_왼쪽": [
            {"title": "손목터널증후군 스트레칭", "url": "https://youtu.be/EiRC80FJbHU"},
            {"title": "손목 통증 완화 운동", "url": "https://youtu.be/wYGfDCGrJ4A"},
            {"title": "김계란 - 손목 통증 운동", "url": "https://youtu.be/4QhQZr6Qb6E"}
        ],
        "손목터널증후군_오른쪽": [
            {"title": "손목터널증후군 스트레칭", "url": "https://youtu.be/EiRC80FJbHU"},
            {"title": "손목 통증 완화 운동", "url": "https://youtu.be/wYGfDCGrJ4A"},
            {"title": "김계란 - 손목 통증 운동", "url": "https://youtu.be/4QhQZr6Qb6E"}
        ]
    }
    return videos_db.get(condition, [])

def show_posture_guide():
    """올바른 자세 가이드"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        **모니터 위치**
        - 눈높이와 같거나 약간 아래
        - 팔 길이만큼 거리 유지 (50-70cm)
        - 화면 상단이 눈높이보다 낮게
        """)
        
        st.write("""
        **의자 자세**
        - 등받이에 허리를 완전히 붙이기
        - 발바닥 전체가 바닥에 닿게
        - 무릎 각도 90도 유지
        """)
    
    with col2:
        st.write("""
        **키보드 & 마우스**
        - 팔꿈치 각도 90도
        - 손목은 일직선 유지
        - 어깨 힘 빼고 자연스럽게
        """)
        
        st.write("""
        **목과 어깨**
        - 턱을 살짝 당기기
        - 어깨는 자연스럽게 내리기
        - 목을 앞으로 빼지 않기
        """)

def create_exercise_routine(conditions, purpose, rest_time):
    """개인 맞춤 운동 루틴 생성"""
    routine = {
        "user_info": {
            "conditions": conditions,
            "purpose": purpose,
            "rest_interval": f"{rest_time}분마다"
        },
        "daily_routine": {},
        "break_exercises": []
    }
    
    # 휴식시간 운동
    for condition in conditions:
        exercises = get_exercises_for_condition(condition, purpose)
        if exercises:
            routine["break_exercises"].extend(exercises[:2])  # 상위 2개 운동만
    
    # 일일 루틴 (아침, 점심, 저녁)
    routine["daily_routine"] = {
        "morning": "목과 어깨 스트레칭 (5분)",
        "lunch": "전신 스트레칭 (10분)",
        "evening": "근력 강화 운동 (15분)"
    }
    
    return routine

def calculate_environment_score(desk_height, chair_support, monitor_height, keyboard_type, mouse_type, lighting):
    score = 0
    
    # 각 요소별 점수 계산
    if desk_height == "적절함": score += 15
    if chair_support in ["매우 좋음", "좋음"]: score += 20
    if monitor_height == "눈높이와 같음": score += 15
    if keyboard_type == "인체공학적": score += 15
    elif keyboard_type == "기계식": score += 10
    if mouse_type == "인체공학적": score += 15
    elif mouse_type == "트랙볼": score += 10
    if lighting == "적절함": score += 20
    
    return score

def send_test_email(email, password):
    """테스트 이메일 발송"""
    try:
        msg = MimeMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "VDT 관리 시스템 - 테스트 메일"
        
        body = "휴식 알리미 테스트 메일입니다. 설정이 정상적으로 완료되었습니다!"
        msg.attach(MimeText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"이메일 발송 실패: {str(e)}")
        return False

def send_test_slack(webhook_url):
    """테스트 Slack 메시지 발송"""
    try:
        payload = {
            "text": "🏃‍♂️ VDT 관리 시스템 - 휴식 알리미 테스트입니다!"
        }
        
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Slack 메시지 발송 실패: {str(e)}")
        return Falsedef 
# show_home()
# st.header("🏠 VDT 증후군이란?")
    
# col1, col2 = st.columns(2)
    
# with col1:
#     st.subheader("📊 주요 증상")
#     st.write("""
#     - **거북목 증후군**: 목이 앞으로 나온 자세로 인한 목과 어깨 통증
#     - **라운드 숄더**: 어깨가 앞으로 말린 자세로 인한 상체 불균형
#     - **허리 디스크**: 장시간 앉은 자세로 인한 허리 통증
#     - **손목터널 증후군**: 반복적인 키보드/마우스 사용으로 인한 손목 통증
#     """)
    
#     with col2:
#         st.subheader("🎯 시스템 기능")
#         st.write("""
#         - 개인 맞춤형 증상 평가
#         - 작업환경 분석
#         - 맞춤형 운동 루틴 제공
#         - 휴식시간 자동 알림
#         - 운동 영상 추천
#         """)
    
#     st.info("👈 왼쪽 메뉴에서 '증상 선택'부터 시작해주세요!")

def show_home():
    st.header("🏠 VDT 증후군이란?")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 주요 증상")
        st.write("""
        - **거북목 증후군**: 목이 앞으로 나온 자세로 인한 목과 어깨 통증
        - **라운드 숄더**: 어깨가 앞으로 말린 자세로 인한 상체 불균형
        - **허리 디스크**: 장시간 앉은 자세로 인한 허리 통증
        - **손목터널 증후군**: 반복적인 키보드/마우스 사용으로 인한 손목 통증
        """)

    with col2:
        st.subheader("🎯 시스템 기능")
        st.write("""
        - 개인 맞춤형 증상 평가
        - 작업환경 분석
        - 맞춤형 운동 루틴 제공
        - 휴식시간 자동 알림
        - 운동 영상 추천
        """)

    st.info("👈 왼쪽 메뉴에서 '증상 선택'부터 시작해주세요!")

def show_condition_selection():
    st.header("🔍 증상 선택")
    
    st.subheader("현재 겪고 있는 증상을 선택해주세요")
    
    conditions = {
        "거북목": "목이 앞으로 나오고 목, 어깨 통증이 있음",
        "라운드숄더": "어깨가 앞으로 말리고 상체가 구부정함",
        "허리디스크": "허리 통증, 다리 저림 등의 증상",
        "손목터널증후군_왼쪽": "왼쪽 손목, 손가락 저림 및 통증",
        "손목터널증후군_오른쪽": "오른쪽 손목, 손가락 저림 및 통증"
    }
    
    selected = []
    
    for condition, description in conditions.items():
        if st.checkbox(f"{condition.replace('_', ' - ')}", key=condition):
            selected.append(condition)
    
    if selected:
        st.session_state.selected_conditions = selected
        st.success(f"선택된 증상: {', '.join([c.replace('_', ' - ') for c in selected])}")
        
        # VAS 통증 척도 입력
        st.subheader("📊 통증 정도 평가 (VAS Scale)")
        
        # VAS 척도 설명 표시
        st.markdown("""
        **통증 집수표 VAS scale**
        
        각 증상별로 현재 느끼는 통증의 정도를 선택해주세요:
        - **0-1**: 통증 없음 😊 (No pain)
        - **2-3**: 약간의 통증 🙂 (Mild pain) - 약간의 통증 혹은 불편감이 있으나 일상생활에 문제없음
        - **4-5**: 보통 통증 😐 (Moderate pain) - 통증이 걱정을 야기할 정도이나 참을 수 있음 (TV, 독서, 대화 가능한 정도)
        - **6-7**: 심한 통증 😟 (Severe pain) - 통증이 상당히 불편하여 집중이 어려움
        - **8-9**: 매우 심한 통증 😣 (Very severe pain) - 통증이 심각하여 일상 생활에 지장
        - **10**: 극심한 통증 😵 (Worst pain possible) - 참을 수 없는 극심한 통증
        """)
        
        pain_scores = {}
        
        for condition in selected:
            st.write(f"**{condition.replace('_', ' - ')} 통증 정도**")
            
            # 통증 정도별 색상과 이모지
            pain_colors = {
                0: "🟢", 1: "🟢", 2: "🟡", 3: "🟡", 
                4: "🟠", 5: "🟠", 6: "🔴", 7: "🔴", 
                8: "🟣", 9: "🟣", 10: "⚫"
            }
            
            pain_level = st.slider(
                f"통증 정도 선택",
                0, 10, 0,
                key=f"pain_{condition}",
                help="0: 통증없음 → 10: 극심한 통증"
            )
            
            # 선택된 통증 수준에 따른 피드백 표시
            if pain_level == 0:
                st.success(f"{pain_colors[pain_level]} 통증 없음 - 좋은 상태입니다!")
            elif pain_level <= 3:
                st.info(f"{pain_colors[pain_level]} 약간의 통증 - 예방 운동을 권장합니다.")
            elif pain_level <= 5:
                st.warning(f"{pain_colors[pain_level]} 보통 통증 - 적극적인 관리가 필요합니다.")
            elif pain_level <= 7:
                st.error(f"{pain_colors[pain_level]} 심한 통증 - 전문의 상담을 고려해보세요.")
            else:
                st.error(f"{pain_colors[pain_level]} 매우 심한 통증 - 즉시 전문의 진료를 받으시기 바랍니다!")
            
            pain_scores[condition] = pain_level
            st.markdown("---")
        
        st.session_state.user_data['pain_scores'] = pain_scores
        
        # 증상 선택 후 관련 제품 추천
        st.markdown("---")
        st.subheader("💡 선택한 증상에 도움되는 제품들")
        st.info("증상 개선에 도움이 될 수 있는 제품들을 추천해드려요!")
        
        for condition in selected:
            show_healthcare_product_recommendation(condition)
    else:
        st.warning("최소 하나의 증상을 선택해주세요.")

def show_personal_info():
    st.header("👤 개인정보 입력")
    
    if not st.session_state.selected_conditions:
        st.warning("먼저 증상을 선택해주세요.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보")
        age = st.number_input("나이", min_value=20, max_value=70, value=30)
        gender = st.selectbox("성별", ["남성", "여성"])
        vision = st.selectbox("시력 상태", ["정상", "근시", "원시", "난시", "기타"])
        work_experience = st.number_input("개발 경력 (년)", min_value=0, max_value=30, value=3)
        
    with col2:
        st.subheader("생활 습관")
        exercise_habit = st.selectbox("운동 습관", ["전혀 안함", "주 1-2회", "주 3-4회", "주 5회 이상"])
        smoking = st.selectbox("흡연", ["비흡연", "과거 흡연", "현재 흡연"])
        drinking = st.selectbox("음주", ["안함", "주 1-2회", "주 3-4회", "거의 매일"])
        sleep_hours = st.slider("평균 수면시간", 4, 12, 7)
    
    st.subheader("작업 습관")
    daily_work_hours = st.slider("일일 컴퓨터 작업시간", 4, 16, 8)
    break_frequency = st.selectbox("휴식 빈도", ["거의 안함", "1-2시간마다", "30분-1시간마다", "30분마다"])
    work_intensity = st.selectbox("작업 강도", ["가벼움", "보통", "높음", "매우 높음"])
    
    # 데이터 저장
    personal_data = {
        'age': age, 'gender': gender, 'vision': vision, 'work_experience': work_experience,
        'exercise_habit': exercise_habit, 'smoking': smoking, 'drinking': drinking,
        'sleep_hours': sleep_hours, 'daily_work_hours': daily_work_hours,
        'break_frequency': break_frequency, 'work_intensity': work_intensity
    }
    
    st.session_state.user_data.update(personal_data)
    
    if st.button("저장하고 다음 단계로"):
        st.success("개인정보가 저장되었습니다!")

def show_work_environment():
    st.header("🖥️ 작업환경 평가")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("책상 및 의자")
        desk_height = st.selectbox("책상 높이", ["너무 높음", "적절함", "너무 낮음"])
        chair_support = st.selectbox("의자 허리 지지", ["매우 좋음", "좋음", "보통", "나쁨"])
        chair_armrest = st.selectbox("팔걸이", ["있음", "없음"])
        
        st.subheader("모니터 설정")
        monitor_distance = st.slider("모니터 거리 (cm)", 30, 100, 60)
        monitor_height = st.selectbox("모니터 높이", ["눈높이보다 높음", "눈높이와 같음", "눈높이보다 낮음"])
        monitor_size = st.number_input("모니터 크기 (인치)", 15, 35, 24)
    
    with col2:
        st.subheader("키보드 및 마우스")
        keyboard_type = st.selectbox("키보드 타입", ["일반", "인체공학적(vertical)", "기계식", "노트북"])
        mouse_type = st.selectbox("마우스 타입", ["일반", "인체공학적", "트랙볼", "터치패드"])
        wrist_support = st.selectbox("손목 받침대", ["있음", "없음"])
        
        st.subheader("환경 요인")
        lighting = st.selectbox("조명", ["매우 밝음", "적절함", "어두움"])
        temperature = st.slider("온도 (°C)", 15, 30, 22)
        noise_level = st.selectbox("소음 수준", ["조용함", "보통", "시끄러움"])
    
    # 환경 점수 계산
    env_score = calculate_environment_score(
        desk_height, chair_support, monitor_height, 
        keyboard_type, mouse_type, lighting
    )
    
    st.subheader("📊 작업환경 평가 결과")
    if env_score >= 80:
        st.success(f"우수한 작업환경입니다! (점수: {env_score}/100)")
    elif env_score >= 60:
        st.warning(f"개선이 필요한 작업환경입니다. (점수: {env_score}/100)")
    else:
        st.error(f"작업환경 개선이 시급합니다! (점수: {env_score}/100)")
    
    # 환경 데이터 저장
    env_data = {
        'desk_height': desk_height, 'chair_support': chair_support,
        'monitor_distance': monitor_distance, 'monitor_height': monitor_height,
        'keyboard_type': keyboard_type, 'mouse_type': mouse_type,
        'lighting': lighting, 'env_score': env_score
    }
    
    st.session_state.user_data.update(env_data)
    
    # 환경 개선 제품 추천
    if env_score < 80:
        st.markdown("---")
        st.subheader("🛒 작업환경 개선 제품 추천")
        st.warning("💡 작업환경 점수가 낮아서 개선이 필요합니다. 아래 제품들을 고려해보세요!")
        
        # 의자 관련 제품 추천
        if chair_support in ["보통", "나쁨"]:
            show_healthcare_product_recommendation("허리디스크")
        
        # 마우스 관련 제품 추천
        if mouse_type == "일반":
            show_healthcare_product_recommendation("손목터널증후군_오른쪽")
        
        # 모니터 높이 관련 제품 추천
        if monitor_height != "눈높이와 같음":
            show_healthcare_product_recommendation("거북목")
    else:
        st.success("🎉 우수한 작업환경입니다! 현재 환경을 유지하세요.")

def show_exercise_recommendation():
    st.header("🏃‍♂️ 맞춤형 운동 추천")
    
    if not st.session_state.selected_conditions:
        st.warning("먼저 증상을 선택해주세요.")
        return
    
    # 운동 목적 선택
    st.subheader("🎯 운동 목적 선택")
    exercise_purpose = st.selectbox(
        "주요 목적을 선택하세요",
        ["예방 (자세교정)", "운동 (근력 및 체력 증진)", "재활 (통증감소)"]
    )
    
    # 휴식시간 계산
    rest_time = calculate_rest_time(st.session_state.user_data.get('work_intensity', '보통'))
    
    st.subheader(f"⏰ 권장 휴식시간: {rest_time}분마다")
    
    # 각 증상별 운동 추천
    for condition in st.session_state.selected_conditions:
        st.subheader(f"📋 {condition.replace('_', ' - ')} 운동법")
        
        exercises = get_exercises_for_condition(condition, exercise_purpose)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for i, exercise in enumerate(exercises, 1):
                with st.expander(f"{i}. {exercise['name']}"):
                    st.write(f"**목적**: {exercise['purpose']}")
                    st.write(f"**방법**: {exercise['method']}")
                    st.write(f"**횟수**: {exercise['reps']}")
                    st.write(f"**주의사항**: {exercise['caution']}")
        
        with col2:
            st.subheader("📹 추천 영상")
            videos = get_exercise_videos(condition)
            for video in videos:
                st.markdown(f"[{video['title']}]({video['url']})")
    
    # 올바른 자세 가이드
    st.subheader("💺 올바른 컴퓨터 작업 자세")
    show_posture_guide()
    
    # 헬스케어 제품 추천 (각 증상별로)
    if st.session_state.selected_conditions:
        st.markdown("---")
        st.subheader("🛒 운동과 함께 사용하면 효과적인 제품들")
        st.info("💪 운동 효과를 높이고 증상 개선에 도움되는 제품들을 추천해드려요!")
        
        for condition in st.session_state.selected_conditions:
            show_healthcare_product_recommendation(condition)
    
    # 운동 루틴 생성
    if st.button("개인 맞춤 운동 루틴 생성"):
        routine = create_exercise_routine(
            st.session_state.selected_conditions, 
            exercise_purpose, 
            rest_time
        )
        
        st.subheader("📅 개인 맞춤 운동 루틴")
        st.json(routine)
        
        # 루틴을 파일로 저장
        try:
            with open("my_exercise_routine.json", "w", encoding="utf-8") as f:
                json.dump(routine, f, ensure_ascii=False, indent=2)
            
            st.success("운동 루틴이 생성되어 my_exercise_routine.json 파일로 저장되었습니다!")
        except Exception as e:
            st.error(f"파일 저장 중 오류가 발생했습니다: {str(e)}")

def show_notification_setup():
    st.header("🔔 휴식 알리미 설정")
    
    st.subheader("알림 방식 선택")
    notification_type = st.selectbox("알림 방식", ["이메일 (Gmail)", "Slack", "둘 다"])
    
    email = ""
    email_password = ""
    slack_webhook = ""
    
    if notification_type in ["이메일 (Gmail)", "둘 다"]:
        st.subheader("📧 Gmail 설정")
        email = st.text_input("Gmail 주소")
        email_password = st.text_input("앱 비밀번호", type="password", 
                                     help="Gmail 2단계 인증 후 앱 비밀번호를 생성해주세요")
        
        if st.button("이메일 테스트"):
            if email and email_password:
                success = send_test_email(email, email_password)
                if success:
                    st.success("이메일 테스트 성공!")
                else:
                    st.error("이메일 설정을 확인해주세요.")
    
    if notification_type in ["Slack", "둘 다"]:
        st.subheader("💬 Slack 설정")
        slack_webhook = st.text_input("Slack Webhook URL", 
                                    help="Slack 앱에서 Incoming Webhooks를 설정해주세요")
        
        if st.button("Slack 테스트"):
            if slack_webhook:
                success = send_test_slack(slack_webhook)
                if success:
                    st.success("Slack 테스트 성공!")
                else:
                    st.error("Slack 설정을 확인해주세요.")
    
    st.subheader("⏰ 알림 시간 설정")
    work_start = st.time_input("업무 시작 시간", value=datetime.strptime("09:00", "%H:%M").time())
    work_end = st.time_input("업무 종료 시간", value=datetime.strptime("18:00", "%H:%M").time())
    
    rest_interval = calculate_rest_time(st.session_state.user_data.get('work_intensity', '보통'))
    
    if st.button("알리미 활성화"):
        notification_config = {
            "type": notification_type,
            "email": email if email else None,
            "email_password": email_password if email_password else None,
            "slack_webhook": slack_webhook if slack_webhook else None,
            "work_start": work_start.strftime("%H:%M"),
            "work_end": work_end.strftime("%H:%M"),
            "interval": rest_interval
        }
        
        # 설정 저장
        try:
            with open("notification_config.json", "w", encoding="utf-8") as f:
                json.dump(notification_config, f, ensure_ascii=False, indent=2, default=str)
            
            st.success(f"알리미가 설정되었습니다! {rest_interval}분마다 휴식 알림을 받게 됩니다.")
            
            # 알림 스케줄러 실행 안내
            st.info("""
            **알리미 실행 방법:**
            1. 터미널에서 `python notification_scheduler.py` 실행
            2. 또는 백그라운드에서 실행: `python notification_scheduler.py &`
            """)
        except Exception as e:
            st.error(f"설정 저장 중 오류가 발생했습니다: {str(e)}")

def main():
    st.title("💻 개발자를 위한 VDT 증후군 관리 시스템")
    st.markdown("---")
    
    # 사이드바 메뉴
    menu = st.sidebar.selectbox(
        "메뉴 선택",
        ["홈", "증상 선택", "개인정보 입력", "작업환경 평가", "운동 추천", "휴식 알리미 설정"]
    )
    
    if menu == "홈":
        show_home()
    elif menu == "증상 선택":
        show_condition_selection()
    elif menu == "개인정보 입력":
        show_personal_info()
    elif menu == "작업환경 평가":
        show_work_environment()
    elif menu == "운동 추천":
        show_exercise_recommendation()
    elif menu == "휴식 알리미 설정":
        show_notification_setup()
    
    # 광고 표시 (사이드바 하단)
    st.sidebar.markdown("---")
    show_adsense_banner()

if __name__ == "__main__":
    main()