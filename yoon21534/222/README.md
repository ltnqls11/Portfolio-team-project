# Blog Influencer Marketing Automation RPA

## 프로젝트 개요
블로그 인플루언서 데이터 수집 및 마케팅 자동화 시스템

## 주요 기능
- 다중 플랫폼 블로그 데이터 수집 (네이버, 티스토리, 워드프레스, 미디엄, 벨로그)
- 인플루언서 자동 분류 및 점수 시스템
- AI 기반 콘텐츠 분석
- 자동화된 연락처 추출 및 이메일 템플릿 생성

## 기술 스택
- **Frontend**: React.js
- **Backend**: Node.js + Express
- **Database**: PostgreSQL
- **Web Scraping**: Puppeteer/Selenium
- **AI**: OpenAI API
- **Infrastructure**: Docker, CI/CD

## 프로젝트 구조
```
├── frontend/          # React.js 프론트엔드
├── backend/           # Node.js 백엔드 API
├── scraper/           # 웹 스크래핑 모듈
├── ml-service/        # 머신러닝 서비스
├── database/          # 데이터베이스 스키마
├── docker/            # Docker 설정
└── docs/              # 문서
```

## 시작하기
1. 의존성 설치: `npm install`
2. 데이터베이스 설정: `npm run db:setup`
3. 개발 서버 실행: `npm run dev`