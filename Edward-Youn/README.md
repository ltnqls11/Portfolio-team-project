# 온라인 마케팅 연계 플랫폼

## 📌 플랫폼 소개
기업이 자신의 제품 또는 서비스를 홍보할 수 있도록 최적화된 올인원 마케팅 자동화 플랫폼입니다.

### 🎯 한 줄 정의
**"기업이 채널/인플루언서를 고르고, 맞춤형 홍보 문구를 자동 생성·배포·관리하는 올인원 플랫폼"**

### 💡 핵심 가치
1. **문구 자동화**: 제품/경쟁사/사례를 학습해 채널별 톤·SEO 구조로 문구 생성
2. **매칭·연계**: 카테고리·도달·참여율에 맞춰 나노/마이크로 인플루언서를 추천 및 연락 자동화
3. **운영 자동화**: N8N으로 수집→정제→생성→발송→로그→리포트까지 파이프라인화

## 🚀 주요 기능

### 1. 인플루언서 연계 홍보 요청
- 카테고리별 인플루언서 탐색 (네이버 블로그, 인스타그램 등)
- 맞춤형 홍보 문구 자동 생성
- 일괄 메일/DM 발송
- 성과 모니터링

### 2. 기업 자체 홍보 채널 문구 생성
- 참고링크 학습을 통한 문구 생성
- 채널별 최적화 (SEO, 해시태그 등)
- 동일 카테고리 인플루언서 톤&매너 학습

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy / SQLModel
- **크롤링**: BeautifulSoup4, Selenium, Apify

### Frontend
- **Framework**: React + Vite
- **UI Library**: shadcn/ui
- **차트**: Recharts, Plotly.js
- **상태관리**: Redux Toolkit / Zustand

### Automation
- **오케스트레이션**: N8N
- **스케줄링**: APScheduler, Celery
- **메일**: SMTP / SendGrid
- **크롤링 자동화**: Apify

## 📂 프로젝트 구조
```
Edward-Youn/
├── backend/
│   ├── api/                 # FastAPI 엔드포인트
│   │   ├── campaigns/       # 캠페인 관리 API
│   │   ├── creators/        # 인플루언서 관리 API
│   │   ├── copy_generation/ # 문구 생성 API
│   │   └── analytics/       # 분석 및 리포트 API
│   ├── crawlers/            # 웹 크롤링 모듈
│   │   ├── naver/          # 네이버 블로그 크롤러
│   │   ├── instagram/      # 인스타그램 크롤러
│   │   └── common/         # 공통 크롤링 유틸
│   ├── data_processing/     # 데이터 처리
│   │   ├── nlp/           # 자연어 처리
│   │   └── analytics/     # 데이터 분석
│   ├── database/           # DB 모델 및 마이그레이션
│   └── services/           # 비즈니스 로직
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── pages/         # 페이지 컴포넌트
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── services/      # API 클라이언트
│   │   └── store/         # 상태 관리
├── automation/             # N8N 워크플로우
│   ├── workflows/         # N8N 워크플로우 JSON
│   └── scripts/          # 자동화 스크립트
├── data/                  # 데이터 저장소
│   ├── raw/              # 원본 데이터
│   ├── processed/        # 처리된 데이터
│   └── exports/          # 내보내기 데이터
└── docs/                 # 프로젝트 문서
    ├── api/              # API 문서
    ├── database/         # DB 스키마
    └── guides/           # 사용 가이드
```

## 📊 데이터베이스 스키마

### 주요 테이블
- **clients**: 광고주 정보
- **campaigns**: 캠페인 정보
- **copy_variants**: 생성된 홍보 문구
- **creators**: 인플루언서 정보
- **outreach**: 연락 이력
- **deliverables**: 게시물 및 성과
- **events**: 이벤트 로그

## 🎯 개발 로드맵

### Phase 1: 기초 설정
- [ ] 프로젝트 환경 설정
- [ ] 데이터베이스 스키마 설계
- [ ] 기본 API 구조 생성

### Phase 2: 크롤링 시스템
- [ ] 네이버 블로그 크롤러 개발
- [ ] 인스타그램 크롤러 개발
- [ ] 크롤링 데이터 정제 파이프라인

### Phase 3: 문구 생성 시스템
- [ ] 채널별 문구 템플릿 설계
- [ ] AI 기반 문구 생성 로직
- [ ] SEO 최적화 규칙 적용

### Phase 4: 매칭 시스템
- [ ] 인플루언서 추천 알고리즘
- [ ] 카테고리 매칭 로직
- [ ] 참여율 분석

### Phase 5: 자동화 시스템
- [ ] N8N 워크플로우 구축
- [ ] 메일/DM 자동 발송
- [ ] 스케줄링 시스템

### Phase 6: 프론트엔드
- [ ] 대시보드 개발
- [ ] 캠페인 관리 UI
- [ ] 리포트 시각화

## 📈 주요 지표
- 캠페인 응답률
- 인플루언서 수락률
- 문구 승인률
- ROI (투자 대비 수익률)

## ⚠️ 정책 및 리스크 관리
- 플랫폼별 이용약관 준수
- 스팸 방지 정책
- 개인정보 보호
- 저작권 및 표절 방지

## 📝 라이선스
MIT License