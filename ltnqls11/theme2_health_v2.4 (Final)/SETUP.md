# VDT 증후군 관리 시스템 v2.0 설치 및 설정 가이드

## 🚀 빠른 시작

### 1. 시스템 요구사항
- Python 3.8 이상
- Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- 최소 4GB RAM, 1GB 디스크 공간

### 2. 설치
```bash
# 1. 저장소 클론
git clone <repository-url>
cd theme2_health_v1

# 2. 가상환경 생성 (권장)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt
```

### 3. 기본 실행
```bash
# 시스템 테스트
python test_system.py

# Streamlit 앱 실행
streamlit run app.py
```

## 🔧 상세 설정

### API 키 설정

#### 1. YouTube Data API v3 (필수)
```bash
# Google Cloud Console에서 발급
# https://console.cloud.google.com/

1. 새 프로젝트 생성
2. YouTube Data API v3 활성화
3. API 키 생성
4. .env 파일에 추가:
   YOUTUBE_API_KEY=your_api_key_here
```

#### 2. Google Gemini AI API (필수)
```bash
# Google AI Studio에서 발급
# https://aistudio.google.com/

1. API 키 생성
2. .env 파일에 추가:
   GEMINI_API_KEY=your_api_key_here
```

#### 3. Supabase 데이터베이스 (필수)
```bash
# Supabase 프로젝트 생성
# https://supabase.com/

1. 새 프로젝트 생성
2. 프로젝트 URL과 anon key 복사
3. .env 파일에 추가:
   SUPABASE_URL=your_project_url
   SUPABASE_ANON_KEY=your_anon_key
```

#### 4. Google Sheets 연동 (선택)
```bash
# Google Cloud Console에서 설정

1. Google Sheets API 활성화
2. 서비스 계정 생성
3. JSON 키 파일 다운로드 → credentials.json으로 저장
4. Google Sheets 문서 생성 후 서비스 계정에 편집 권한 부여
5. .env 파일에 추가:
   SPREADSHEET_ID=your_spreadsheet_id
```

### .env 파일 구성
```bash
# 필수 설정
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# 선택 설정
SPREADSHEET_ID=your_google_sheets_id

# 기타 설정
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## 📊 Supabase 데이터베이스 스키마 설정

### video_analysis 테이블 생성
```sql
-- Supabase SQL 편집기에서 실행

CREATE TABLE IF NOT EXISTS public.video_analysis (
    id BIGSERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    channel_name VARCHAR(200),
    upload_date DATE,
    duration_seconds INTEGER,
    
    -- 의료/운동 분류
    target_condition VARCHAR(50) NOT NULL,
    exercise_purpose VARCHAR(50) NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    exercise_type VARCHAR(50),
    body_parts TEXT[], -- JSON 배열
    intensity VARCHAR(20),
    equipment_needed VARCHAR(50),
    
    -- 품질 지표
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- 전문성 검증
    creator_type VARCHAR(50),
    credential_verified BOOLEAN DEFAULT FALSE,
    medical_accuracy DECIMAL(3,2) CHECK (medical_accuracy >= 0 AND medical_accuracy <= 5),
    
    -- 사용자 맞춤화
    age_group VARCHAR(20),
    fitness_level VARCHAR(20),
    pain_level_range VARCHAR(10),
    
    -- 효과성 추적
    effectiveness_score DECIMAL(3,2) DEFAULT 0.0,
    completion_rate DECIMAL(5,4) DEFAULT 0.0,
    user_rating DECIMAL(3,2) DEFAULT 0.0,
    
    -- 추가 의학적 정보
    contraindications TEXT,
    expected_benefits TEXT,
    safety_level VARCHAR(20) DEFAULT '안전',
    analysis_date TIMESTAMP DEFAULT NOW(),
    
    -- 메타데이터
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_video_analysis_condition ON public.video_analysis(target_condition);
CREATE INDEX IF NOT EXISTS idx_video_analysis_purpose ON public.video_analysis(exercise_purpose);
CREATE INDEX IF NOT EXISTS idx_video_analysis_effectiveness ON public.video_analysis(effectiveness_score DESC);
CREATE INDEX IF NOT EXISTS idx_video_analysis_medical_accuracy ON public.video_analysis(medical_accuracy DESC);

-- RLS (Row Level Security) 활성화
ALTER TABLE public.video_analysis ENABLE ROW LEVEL SECURITY;

-- 읽기 권한 정책
CREATE POLICY "video_analysis_select_policy" ON public.video_analysis
    FOR SELECT USING (true);

-- 쓰기 권한 정책 (anon 키로도 쓰기 가능)
CREATE POLICY "video_analysis_insert_policy" ON public.video_analysis
    FOR INSERT WITH CHECK (true);

CREATE POLICY "video_analysis_update_policy" ON public.video_analysis
    FOR UPDATE USING (true);
```

## 🧪 시스템 테스트

### 전체 시스템 테스트
```bash
python test_system.py
```

### 헬스 체크
```bash
python test_system.py health
```

### 개별 기능 테스트
```bash
# YouTube 검색 테스트
python -c "from youtube_collector import search_youtube_videos; print(len(search_youtube_videos('목 스트레칭', 3)))"

# AI 분석 테스트
python -c "from video_analyzer import analyze_single_video; print('OK' if analyze_single_video({'video_id': 'test', 'title': '목 운동', 'channel_name': '테스트', 'description': '목 스트레칭', 'duration_seconds': 300, 'view_count': 1000, 'like_count': 50, 'comment_count': 10}) else 'FAIL')"
```

## 🚀 운영 모드 실행

### 1. Streamlit 앱 실행
```bash
streamlit run app.py --server.port 8501
```

### 2. 영상 수집 파이프라인 실행
```bash
# 전체 수집
python main_pipeline.py

# 테스트 모드
python main_pipeline.py test
```

### 3. 휴식 알리미 실행
```bash
# 포그라운드 실행
python notification_scheduler.py

# 백그라운드 실행 (Windows)
start /B python notification_scheduler.py

# 백그라운드 실행 (macOS/Linux)
nohup python notification_scheduler.py &
```

## 🔧 문제 해결

### 일반적인 문제

#### 1. ImportError: No module named 'xxx'
```bash
pip install -r requirements.txt
```

#### 2. YouTube API 할당량 초과
```bash
# .env 파일에서 API 키 확인
# Google Cloud Console에서 할당량 확인
# 다음날까지 대기 또는 유료 플랜 고려
```

#### 3. Gemini API 오류
```bash
# API 키 유효성 확인
# 월 요청 제한 확인 (무료: 60회/월)
# 네트워크 연결 확인
```

#### 4. Supabase 연결 실패
```bash
# URL과 anon key 확인
# 테이블 생성 여부 확인
# RLS 정책 설정 확인
```

#### 5. Google Sheets 연동 실패
```bash
# credentials.json 파일 존재 확인
# 서비스 계정 권한 확인
# SPREADSHEET_ID 정확성 확인
```

### 로그 확인
```bash
# 일반 로그
tail -f vdt_pipeline.log

# 알림 스케줄러 로그
tail -f notification_scheduler.log
```

### 성능 최적화
```bash
# 1. API 호출 제한 설정
# config.py에서 배치 크기 조정

# 2. 데이터베이스 연결 풀 설정
# Supabase 연결 최적화

# 3. 캐싱 활용
# Streamlit 캐싱 기능 사용
```

## 📈 모니터링

### 시스템 상태 확인
```bash
# 일일 헬스 체크
python test_system.py health

# 데이터베이스 통계
python -c "from database import get_database_analytics; print(get_database_analytics())"
```

### 로그 분석
```bash
# 오류 로그 확인
grep -i error vdt_pipeline.log

# API 사용량 확인
grep -i "api" vdt_pipeline.log | wc -l
```

## 🔄 업데이트 및 백업

### 시스템 업데이트
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 데이터 백업
```bash
# Supabase 데이터 백업
# 대시보드에서 SQL 덤프 다운로드

# 설정 파일 백업
cp .env .env.backup
cp notification_config.json notification_config.backup.json
```

## 📞 지원

### 문제 보고
- GitHub Issues를 통해 버그 리포트
- 로그 파일과 함께 상세한 재현 방법 제공

### 기능 요청
- GitHub Discussions를 통해 새로운 기능 제안
- 사용 사례와 함께 구체적인 요구사항 명시

### 커뮤니티
- 사용자 가이드 및 팁 공유
- 의료 전문가 검증 요청

---

## 📝 부록

### A. API 할당량 관리
- YouTube Data API: 일일 10,000 쿼터 (무료)
- Gemini AI: 월 60회 요청 (무료)
- Supabase: 월 500MB 저장소 (무료)

### B. 보안 고려사항
- API 키는 반드시 .env 파일에서 관리
- credentials.json은 Git에 커밋하지 않음
- 프로덕션 환경에서는 환경변수 사용 권장

### C. 성능 벤치마크
- 영상 수집: 키워드당 10-15개, 총 5-10분 소요
- AI 분석: 영상당 2-5초, API 제한으로 배치 처리
- 데이터베이스 저장: 영상당 100-200ms

### D. 라이선스
- 오픈소스 라이브러리: 각 라이브러리의 라이선스 준수
- YouTube 콘텐츠: 공정 사용 원칙 적용
- AI 분석 결과: 참고용으로만 사용, 의료 조언 아님
