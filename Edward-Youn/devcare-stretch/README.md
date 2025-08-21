# DevCare Stretch 
🏃‍♂️\n\n개발자와 사무직 근로자를 위한 AI 기반 맞춤형 운동 추천 시스템

## 🎯 프로젝트 개요
DevCare Stretch는 개발자들의 건강 문제(거북목, 라운드숄더, 허리통증 등)를 해결하기 위한 종합적인 헬스케어 플랫폼입니다.

### 주요 기능
- 🤖 **AI 증상 분석**: GPT 기반 전문의 수준의 스크리닝 분석
- 📹 **맞춤 운동 추천**: YouTube 영상 기반 개인화된 운동 프로그램
- 💬 **Slack 알림**: 업무 시간에 맞춘 자동 운동 리마인더
- 📊 **진행도 추적**: 운동 기록 및 개선 상황 모니터링
- 🔄 **자동화**: n8n 기반 데이터 수집 및 워크플로우 자동화

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │────│   Node.js API   │────│   Supabase DB   │
│   Frontend      │    │   Backend       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │      n8n        │              │
         │              │  Automation     │              │
         │              └─────────────────┘              │
         │                       │                       │
┌─────────────────┐     ┌─────────────────┐    ┌─────────────────┐
│   Slack API     │     │  YouTube API    │    │   OpenAI API    │
│   Notifications │     │  Data Collection│    │   GPT Analysis  │
└─────────────────┘     └─────────────────┘    └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   Gemini API    │
                        │ Comment Analysis│
                        └─────────────────┘

```

## 🚀 빠른 시작

###
 1. 레포지토리 클론
 ``` bash\ngit clone https://github.com/your-username/devcare-stretch.git\ncd devcare-stretch
 ```
 
 ### 2. 백엔드 설정
 ```bash\ncd backend
 npm install\ncp .env.example .env
 # .env 파일에 API 키들을 설정하세요
 npm run dev
 ```
 
 ### 3. 프론트엔드 설정
 ```bash\ncd frontend\nnpm install
 npm start
 ```
 
 ### 4. 데이터베이스 설정
 1. [Supabase](https://supabase.com)에서 새 프로젝트 생성
 2. `database/schema.sql` 파일을 Supabase SQL Editor에서 실행
 3. `.env` 파일에 Supabase 연결 정보 입력
 
 ### 5. n8n 자동화 워크플로우 설정

**🌟 권장: n8n 클라우드 사용 (Windows 친화적)**
```bash
# 1. n8n.io 클라우드 가입 (무료 5000회/월)
# 2. JSON 파일 복사/붙여넣기로 워크플로우 import
# 3. 환경 변수 설정 및 활성화
# 📖 상세 가이드: docs/n8n-cloud-setup-guide.md
```

**⚙️ 대안: 로컬 Docker 설치**
```bash
# Linux/Mac
chmod +x setup-n8n.sh
./setup-n8n.sh

# Windows
setup-n8n.bat

# 📖 상세 가이드: docs/n8n-setup-guide.md
```
 
 ## 🔧 환경 변수 설정
 
 ### 백엔드 (.env)
 ```env

 # 서버 설정
 PORT=5000
 NODE_ENV=development
 
 
 # Supabase
 SUPABASE_URL=your_supabase_url
 SUPABASE_ANON_KEY=your_supabase_anon_key
 SUPABASE_SERVICE_KEY=your_supabase_service_key
 
 # API Keys
 YOUTUBE_API_KEY=your_youtube_api_key
 OPENAI_API_KEY=your_openai_api_key
 GEMINI_API_KEY=your_gemini_api_key
 SLACK_BOT_TOKEN=your_slack_bot_token
 SLACK_SIGNING_SECRET=your_slack_signing_secret
 
 # n8n
 N8N_WEBHOOK_URL=your_n8n_webhook_url
 ```
 
 ### 프론트엔드 (.env)
 ```env
 REACT_APP_API_URL=http://localhost:5000/api
 ```
 
 ## 📋 API 키 발급 가이드
 
 ### 1. YouTube Data API
 1. Google Cloud Console 접속
 2. 새 프로젝트 생성 또는 기존 프로젝트 선택
 3. YouTube Data API v3 활성화
 4. API 키 생성
 
 ### 2. OpenAI API
 1. OpenAI Platform 가입
 2. API Keys 메뉴에서 새 키 생성
 
 ### 3. Google Gemini API
 1. Google AI Studio 접속
 2. API 키 발급
 
 ### 4. Slack API
 1. Slack API 접속
 2. 새 앱 생성
 3. Bot Token Scopes 설정
 4. Bot User OAuth Token 복사
 
 ## 🗂️ 프로젝트 구조
 
 ```\ndevcare-stretch/
 ├── backend/                 # Node.js API 서버
 │   ├── config/             # 데이터베이스 및 설정
 │   ├── models/             # 데이터 모델
 │   ├── routes/             # API 라우트
 │   ├── services/           # 외부 API 연동
 │   └── server.js           # 메인 서버 파일
 ├── frontend/               # React 웹 앱
 │   ├── src/
 │   │   ├── components/     # 재사용 컴포넌트
 │   │   ├── pages/          # 페이지 컴포넌트
 │   │   ├── services/       # API 클라이언트
 │   │   └── App.js          # 메인 앱 컴포넌트
 │   └── public/
 ├── database/               # 데이터베이스 스키마
 │   └── schema.sql          # Supabase 스키마
 ├── n8n-workflows/          # 자동화 워크플로우
 │   ├── youtube-data-ingestion.json
 │   └── slack-notifications.json
 └── docs/                   # 문서
 ```
 
 ## 🛠️ 개발 워크플로우
 
 ### 데이터 수집 자동화
 1. **매일 새벽 6시 (KST)**: n8n이 증상별 키워드로 YouTube 검색
 2. **영상 상세 정보 수집**: 제목, 설명, 조회수, 댓글 등
 3. **Gemini AI 댓글 분석**: 효과성 및 부작용 키워드 추출
 4. **Supabase 저장**: 분석된 데이터를 데이터베이스에 업서트
 
 ### 사용자 플로우
 1. **온보딩**: 5단계 설문조사 (증상, 통증도, 근무환경 등)
 2. **AI 분석**: GPT가 전문의 수준의 스크리닝 요약 생성
 3. **운동 추천**: 개인 상태에 맞는 Top 3 영상 추천
 4. **루틴 설정**: 시간대/요일 선택하여 Slack 알림 스케줄링
 5. **진행도 추적**: 운동 완료 기록 및 통계 분석
 
 ## 🎨 주요 기술 스택
 
 ### Frontend
 - **React 18**: 컴포넌트 기반 UI 프레임워크
 - **React Router**: 클라이언트 사이드 라우팅
 - **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
 - **React Hook Form**: 폼 상태 관리
 - **React Hot Toast**: 알림 컴포넌트
 
 ### Backend
 - **Node.js**: JavaScript 런타임
 - **Express.js**: 웹 프레임워크
 - **Supabase**: PostgreSQL 데이터베이스 및 인증
 - **OpenAI SDK**: GPT API 연동
 - **Google Generative AI**: Gemini API 연동
 
 ### 자동화 & 외부 연동
 - **n8n**: 워크플로우 자동화 플랫폼
 - **YouTube Data API v3**: 영상 검색 및 댓글 수집
 - **Slack Web API**: 메시지 발송 및 인터랙션
 - **OpenAI GPT-3.5**: 스크리닝 요약 생성
 - **Google Gemini Pro**: 댓글 분석 및 분류
 
 ## 📊 데이터베이스 스키마
 
 ### 주요 테이블
 - **users**: 사용자 기본 정보
 - **survey_responses**: 설문 응답 및 스크리닝 요약
 - **videos**: YouTube 영상 메타데이터
 - **video_comment_summary**: 댓글 분석 결과
 - **symptom_index**: 증상-영상 연관도 인덱스
 - **workout_routines**: 사용자별 운동 루틴
 - **workout_events**: 운동 완료 기록
 
 ## 🚀 배포 가이드
 
 ### Vercel (Frontend)
 ```bash
 cd frontend
 npm run build
 # Vercel CLI 또는 GitHub 연동으로 배포
 ```
 
 ### Railway/Heroku (Backend)
 ```bash
 cd backend
 # Git 연동 자동 배포 설정
 ```
 
 ### n8n Cloud
 1. n8n Cloud 계정 생성
 2. 워크플로우 JSON 파일 import
 3. 환경 변수 및 웹훅 URL 설정
 
 ## 🤝 기여 가이드
 
 1. Fork the repository
 2. Create a feature branch
 3. Commit your changes
 4. Push to the branch
 5. Open a Pull Request
 
 ## 📄 라이센스
 
 MIT License
 
 ## ⚠️ 의학적 면책조
 
 이 시스템은 의학적 진단이나 치료를 대체하지 않습니다. 심각한 통증이나 건강 문제가 있는 경우 전문의와 상담하시기 바랍니다."