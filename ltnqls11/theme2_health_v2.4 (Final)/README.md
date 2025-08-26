# 💻 직장인 VDT 증후군 관리 시스템 v2.3

컴퓨터 작업으로 인한 VDT(Visual Display Terminal) 증후군을 예방하고 관리하기 위한 **AI 기반 맞춤형 헬스케어 시스템**입니다.

## 🌟 v2.3 최신 기능

### 📧 NEW! 자동 메일 스케줄러
- **🔥 Streamlit 종료 후에도 백그라운드에서 자동 실행**
- **⏰ 5분~55분 단위 맞춤 간격 설정**
- **📅 근무 시간/평일 자동 판단**
- **🎯 개인별 맞춤 운동 메시지 자동 발송**
- **📊 실시간 스케줄러 상태 모니터링**

### 📹 실시간 YouTube 동영상 검색
- YouTube Data API를 통한 실시간 운동 영상 검색
- VDT 증후군별 맞춤 운동 영상 자동 검색
- 채널명, 조회수, 영상 길이 정보 제공
- 최신 운동법 자동 업데이트

### 🤖 AI 맞춤 운동 추천
- Google Gemini AI 기반 개인 맞춤 분석
- 개인 정보와 증상을 종합한 전문적인 운동 계획
- 물리치료사 수준의 전문적인 건강 조언
- Google Sheets 연동으로 데이터 추적 및 관리

### 🗃️ 통합 데이터베이스 시스템
- Supabase PostgreSQL 기반 고성능 데이터베이스
- 운동 영상 데이터 자동 수집 및 AI 품질 분석
- 25개 파이썬 모듈의 유기적 통합
- 고객 이력 관리 및 재방문 고객 추적

## 🎯 주요 기능

### 1. 증상별 맞춤 관리
- **거북목 증후군**: 목과 어깨 통증 관리
- **라운드 숄더**: 어깨 자세 교정
- **허리 디스크**: 허리 통증 예방 및 관리
- **손목터널 증후군**: 좌우 구분 관리

### 2. 개인 맞춤 평가
- 개인적 요인 (나이, 성별, 작업경력 등)
- 작업환경 요인 (책상, 의자, 모니터 설정 등)
- 작업조건 요인 (작업시간, 강도, 휴식패턴)
- VAS 통증 척도 적용
- 사회심리적 요인 (스트레스, 만족도 등)

### 3. 맞춤형 운동 추천
- **예방 (자세교정)**: 올바른 자세 유지를 위한 운동
- **운동 (근력 및 체력 증진)**: 근력 강화 운동
- **재활 (통증감소)**: 통증 완화를 위한 치료적 운동

### 4. 과학적 휴식시간 계산
- Murrel의 공식 적용
- 작업강도(RMR)에 따른 개인별 휴식시간 산정
- 자동 휴식 알리미 (Gmail, Slack)

### 5. 스마트 운동 영상 시스템
- 실시간 YouTube 검색으로 최신 영상 제공
- AI 기반 영상 품질 평가 및 필터링
- 개인 운동 목적에 맞는 영상 자동 추천
- 백업용 기본 영상 데이터베이스

## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
`.env` 파일을 생성하고 다음 API 키들을 설정하세요:
```
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SPREADSHEET_ID=your_google_sheets_id
```

### 3. Streamlit 앱 실행
```bash
streamlit run app.py
```

### 4. 고급 기능 활용

#### YouTube 검색 활성화
- YouTube Data API v3 키 필요
- 하루 10,000 쿼터 제한 (무료)
- Google Cloud Console에서 발급 가능

#### AI 추천 활성화
- Google AI Studio에서 Gemini API 키 발급
- 월 60회 무료 요청 (무료 티어)

#### 데이터 저장 활성화
- Google Sheets API 연동
- `credentials.json` 서비스 계정 키 필요

### 5. 자동 메일 스케줄러 실행 (선택사항)
```bash
# 🔥 NEW! 독립 자동 스케줄러 (권장)
python start_auto_email.py

# 직접 스케줄러 제어
python email_scheduler.py start
python email_scheduler.py stop
python email_scheduler.py status

# 기존 방식 (별도 실행 필요)
python notification_scheduler.py
```

## 📱 사용 방법

### 1단계: 증상 선택
- 현재 겪고 있는 증상을 선택
- VAS 통증 척도로 통증 정도 평가 (0-10점)

### 2단계: 개인정보 입력
- 기본 정보 (나이, 성별, 시력 등)
- 생활 습관 (운동, 흡연, 음주, 수면)
- 작업 습관 (작업시간, 휴식빈도, 작업강도)

### 3단계: 작업환경 평가
- 책상 및 의자 설정
- 모니터 위치 및 크기
- 키보드, 마우스 타입
- 환경 요인 (조명, 온도, 소음)
- 자동 환경 점수 계산 (0-100점)

### 4단계: 운동 추천 받기
- 운동 목적 선택 (예방/운동/재활)
- 기본 운동법 확인
- **🆕 실시간 YouTube 영상 검색 결과 확인**
- **🆕 AI 맞춤 운동 계획 생성**
- 올바른 자세 가이드 학습

### 5단계: 자동 메일 알림 설정
- **📧 NEW! 자동 메일 스케줄러**: Streamlit 종료 후에도 백그라운드 자동 실행
- **⏰ 맞춤 간격**: 5분~55분 단위로 정밀 설정
- **🔔 기존 방식**: Gmail/Slack 즉시 알림 (별도 실행 필요)
- **📅 스마트 발송**: 근무 시간/평일 자동 판단
- **📊 실시간 모니터링**: 발송 상태 및 횟수 추적

## 🔧 고급 설정 가이드

### YouTube API 설정
1. Google Cloud Console 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성 및 제한 설정
5. `.env` 파일에 `YOUTUBE_API_KEY` 추가

### Gemini AI 설정
1. Google AI Studio (aistudio.google.com) 접속
2. API 키 생성
3. `.env` 파일에 `GEMINI_API_KEY` 추가

### Google Sheets 설정
1. Google Cloud Console에서 서비스 계정 생성
2. Google Sheets API 활성화
3. 서비스 계정 키를 `credentials.json`으로 저장
4. Google Sheets 문서 생성 후 서비스 계정에 편집 권한 부여
5. `.env` 파일에 `SPREADSHEET_ID` 추가

### Gmail 설정
1. Google 계정에서 2단계 인증 활성화
2. 앱 비밀번호 생성
3. Streamlit 앱에서 Gmail 주소와 앱 비밀번호 입력

### Slack 설정
1. Slack 워크스페이스에서 앱 생성
2. Incoming Webhooks 활성화
3. Webhook URL 복사하여 앱에 입력

## 📊 과학적 근거

### Murrel의 휴식시간 공식
작업강도에 따른 휴식시간을 과학적으로 계산:
- **가벼운 작업**: 30분마다 휴식
- **보통 작업**: 25분마다 휴식  
- **높은 강도**: 20분마다 휴식
- **매우 높은 강도**: 15분마다 휴식

### VAS 통증 척도
0-10점 척도로 주관적 통증 정도를 정량화하여 운동 강도 조절

### AI 추천 알고리즘
- 개인 특성, 증상, 환경 요인을 종합 분석
- 물리치료 전문 지식 기반 프롬프트 엔지니어링
- 실시간 개인화된 운동 처방

## 🏗️ 시스템 아키텍처

### 핵심 모듈 구조 (25개 파이썬 모듈)

#### 🎯 메인 애플리케이션
- `app.py` (2,500+ 라인): 메인 Streamlit 웹 애플리케이션
- `app_sb.py` / `app00.py`: Supabase 연동 및 백업 버전

#### 📧 스마트 알림 시스템  
- `email_scheduler.py` (NEW): **자동 백그라운드 메일 스케줄러**
- `start_auto_email.py` (NEW): **독립 실행 스크립트**
- `notification_scheduler.py`: 기존 휴식 알림 시스템
- `posture_tip_notifier.py`: 자세 교정 팁 알림

#### 🤖 AI & 데이터 처리
- `youtube_collector.py`: YouTube API 실시간 영상 수집
- `video_analyzer.py`: Gemini AI 기반 영상 품질 분석
- `database.py`: Supabase PostgreSQL 데이터베이스 연동
- `customer_database.py`: 고객 이력 관리 시스템

#### 🏃 운동 관리 시스템
- `exercise_manager6.py`: 통합 운동 관리 대시보드
- `exercise_manager.py`: 기본 운동 추천 엔진
- `main_pipeline.py`: 자동 데이터 수집 파이프라인

#### 📊 분석 & 광고
- `ads.py`: 건강 제품 추천 시스템
- `config.py`: 시스템 설정 및 상수 관리
- `test_system.py`: 전체 시스템 헬스 체크

#### 🔧 유틸리티 & 백업
- `migrate_data.py`: 데이터 마이그레이션 도구
- `check_user_visits.py`: 사용자 방문 추적
- `start_scheduler.py`: 스케줄러 시작 도구

### 데이터 플로우
1. **사용자 입력** → Streamlit 세션 상태 저장
2. **YouTube API** → 실시간 영상 수집 & AI 품질 분석
3. **Gemini AI** → 개인 맞춤 운동 추천 생성
4. **Supabase DB** → 데이터 저장 & 고객 이력 관리
5. **자동 스케줄러** → 백그라운드 메일 자동 발송
6. **Google Sheets** → 선택적 데이터 백업 & 추적

## 📁 프로젝트 파일 구조

### 🔧 설정 파일
- `.env`: API 키 및 환경변수 설정
- `credentials.json`: Google 서비스 계정 키 (사용자 생성)
- `requirements.txt`: Python 패키지 의존성 (24개 패키지)

### 📊 데이터 저장 파일
- `email_schedule_config.json` (NEW): 자동 메일 스케줄러 설정
- `notification_config.json`: 기존 알림 설정
- `my_exercise_routine.json`: 개인 맞춤 운동 루틴
- `customer_history.json`: 고객 이력 데이터
- `local_exercise_data.json`: 로컬 운동 데이터 백업

### 📝 로그 파일
- `email_scheduler.log` (NEW): 자동 메일 스케줄러 로그
- `notification_scheduler.log`: 기존 알림 시스템 로그
- `vdt_pipeline.log`: 데이터 수집 파이프라인 로그

### 📚 문서 파일
- `README.md`: 프로젝트 종합 가이드
- `README_EMAIL_SCHEDULER.md` (NEW): 자동 메일 스케줄러 상세 가이드
- `SETUP.md`: 설치 및 설정 가이드
- `gmail_setup_guide.md`: Gmail 설정 가이드
- `SUPABASE_SETUP.md`: Supabase 설정 가이드

### 🗄️ 데이터베이스 스키마
- `supabase_schema.sql`: 전체 데이터베이스 스키마
- `create_supabase_tables.sql`: 테이블 생성 스크립트
- `backup_supabase_data.sql`: 데이터 백업 스크립트

## 🎯 운동 카테고리

### 예방 (자세교정)
- 목, 어깨, 허리 스트레칭
- 올바른 자세 유지 운동
- 근육 이완 운동

### 운동 (근력 및 체력 증진)  
- 코어 근력 강화
- 목, 어깨 근력 운동
- 전신 체력 향상 운동

### 재활 (통증감소)
- 통증 완화 스트레칭
- 온찜질 요법
- 점진적 재활 운동

## 🔒 개인정보 보호

- 모든 개인정보는 로컬 세션에서만 처리
- Google Sheets 저장은 사용자 선택사항
- API 키는 환경변수로 안전하게 관리
- 외부 서버로 민감정보 전송 없음

## 🚧 제한사항

### API 제한
- YouTube Data API: 일일 10,000 쿼터
- Gemini AI: 월 60회 무료 요청
- Google Sheets: 분당 100회 요청

### 브라우저 호환성
- Chrome, Firefox, Safari, Edge 지원
- 모바일 브라우저 부분 지원

## 🔄 업데이트 내역

### v2.3 (2025.08.26) - 🔥 최신 버전
- **🆕 자동 메일 스케줄러**: Streamlit 종료 후에도 백그라운드 자동 실행
- **🆕 스마트 간격 설정**: 5분~55분 단위로 정밀한 알림 간격 조절
- **🆕 활성화 시작 알림**: 스케줄러 시작 시 환영 메일 자동 발송
- **🆕 실시간 상태 모니터링**: 사이드바에서 스케줄러 상태 실시간 확인
- **🆕 독립 실행 스크립트**: `start_auto_email.py`로 간편한 스케줄러 관리
- **📧 통합 알림 시스템**: 자동 스케줄러 + 기존 방식 선택 가능
- **🔧 UI/UX 개선**: 알림 설정 인터페이스 대폭 개선

### v2.0 (2025.08)
- 🆕 실시간 YouTube 검색 기능 추가
- 🆕 AI 맞춤 운동 추천 시스템
- 🆕 Supabase 데이터베이스 연동
- 🆕 Google Sheets 데이터 저장
- 🔧 사용자 인터페이스 개선
- 🔧 에러 처리 및 안정성 향상

### v1.0 (2025.07)
- 기본 VDT 증후군 관리 기능
- 정적 운동 추천 시스템
- 휴식 알림 기능
- 작업환경 평가

## 📞 문의사항

시스템 사용 중 문제가 발생하면 GitHub Issues를 통해 문의해주세요.

### 개발팀
- 프론트엔드: Streamlit 기반 반응형 웹 인터페이스
- 백엔드: Python 기반 AI/ML 파이프라인
- 데이터베이스: Supabase PostgreSQL
- API 통합: YouTube, Gemini AI, Google Workspace

---

**⚠️ 주의사항**: 
- 심각한 통증이나 증상이 있는 경우 반드시 의료진과 상담하시기 바랍니다.
- AI 추천은 참고용이며, 개인의 건강 상태에 따라 조절하여 사용하세요.
- 운동 중 통증이 악화되면 즉시 중단하고 전문의와 상담하세요.