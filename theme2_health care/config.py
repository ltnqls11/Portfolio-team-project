import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Supabase 설정

# YouTube Data API


# OpenAI API


# Google Gemini API


# 검색 키워드 설정
SEARCH_KEYWORDS = [
    "거북목 교정 운동",
    "목 스트레칭 사무직",
    "어깨 운동 컴퓨터",
    "라운드숄더 교정",
    "허리 디스크 운동",
    "허리 스트레칭 의자",
    "손목 터널 증후군 운동",
    "손목 스트레칭 마우스",
    "사무직 운동",
    "책상 앞 스트레칭",
    "VDT 증후군 운동",
    "목어깨 통증 운동",
    "개발자 운동",
    "프로그래머 스트레칭"
]

# VDT 증후군 관련 설정 (손목터널증후군 통일)
VDT_CONDITIONS = {
    "거북목": ["거북목", "목", "경추", "목통증", "목디스크", "스트레이트넥", "일자목"],
    "라운드숄더": ["라운드숄더", "어깨", "승모근", "등", "어깨통증", "굽은어깨"],
    "허리디스크": ["허리", "허리디스크", "요추", "허리통증", "골반", "요통"],
    "손목터널증후군": ["손목", "손목터널", "손목통증", "손목증후군", "손목염좌", "수근관"]
}

# 운동 목적별 키워드
EXERCISE_PURPOSES = {
    "예방": ["예방", "방지", "미리", "사전", "예방적", "자세교정"],
    "운동": ["강화", "근력", "체력", "운동", "피트니스", "근력강화"],
    "재활": ["재활", "치료", "회복", "완화", "치유", "개선", "통증감소"]
}

# 운동 유형별 키워드
EXERCISE_TYPES = {
    "스트레칭": ["스트레칭", "늘리기", "이완", "풀기", "스트레치"],
    "근력강화": ["근력", "강화", "운동", "트레이닝", "근육"],
    "마사지": ["마사지", "지압", "눌러주기", "문지르기", "셀프마사지"],
    "자세교정": ["자세", "교정", "바로잡기", "포스처", "정렬"]
}

# 데이터베이스 테이블 스키마
VIDEO_ANALYSIS_SCHEMA = {
    "table_name": "video_analysis",
    "columns": [
        "id",
        "video_id",
        "title", 
        "url",
        "channel_name",
        "upload_date",
        "duration_seconds",
        "target_condition",
        "exercise_purpose", 
        "difficulty_level",
        "exercise_type",
        "body_parts",
        "intensity",
        "equipment_needed",
        "view_count",
        "like_count", 
        "comment_count",
        "creator_type",
        "credential_verified",
        "medical_accuracy",
        "age_group",
        "fitness_level",
        "pain_level_range",
        "effectiveness_score",
        "completion_rate",
        "user_rating",
        "contraindications",
        "expected_benefits",
        "safety_level",
        "analysis_date",
        "created_at",
        "updated_at"
    ]
}

# 로그 설정
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "file": "vdt_pipeline.log",
        "console": True
    }
}
