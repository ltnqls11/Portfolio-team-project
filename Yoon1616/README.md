# 마케팅 플랫폼

기업이 블로그를 이용해 제품을 홍보하도록 돕는 온라인 마케팅 플랫폼입니다.

## 주요 기능

### 1. 인플루언서 발굴
- 제품 카테고리별 인플루언서 검색 및 필터링
- 팔로워 수, 참여율, 가격 등 다양한 기준으로 정렬
- 성과 기반 추천 시스템
- 예산 기반 최적 인플루언서 조합 추천

### 2. 홍보 문구 자동 생성
- 채널별 템플릿 기반 홍보 문구 생성
- 제품 정보 자동 치환
- 톤앤매너 조정
- 채널별 최적화 (인스타그램, 유튜브, 블로그 등)
- 해시태그 자동 생성

### 3. 연락 자동화
- 이메일 및 DM 자동 발송
- 연락 상태 추적 (대기/전송/회신/수락/거절)
- 대량 연락 발송
- 후속 연락 자동화

### 4. 캠페인 관리
- 캠페인 생성 및 관리
- 인플루언서 할당
- 예산 관리
- 진행 상황 추적

### 5. 성과 분석
- 실시간 성과 지표 대시보드
- 인플루언서별 성과 비교
- ROI, CTR, 전환율 분석
- 차트 및 그래프 시각화

## 기술 스택

- **Frontend**: React 18, TypeScript
- **UI Framework**: Material-UI (MUI)
- **Charts**: Recharts
- **Routing**: React Router DOM
- **Build Tool**: Vite

## 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build
```

## 프로젝트 구조

```
src/
├── components/          # 재사용 가능한 컴포넌트
│   └── Layout/         # 레이아웃 컴포넌트
├── pages/              # 페이지 컴포넌트
│   ├── Dashboard/      # 대시보드
│   ├── InfluencerDiscovery/  # 인플루언서 발굴
│   ├── CampaignManagement/   # 캠페인 관리
│   ├── PromotionGenerator/   # 홍보 문구 생성
│   ├── ContactAutomation/    # 연락 자동화
│   └── PerformanceAnalytics/ # 성과 분석
├── services/           # 비즈니스 로직 서비스
│   ├── promotionGenerator.ts    # 홍보 문구 생성 서비스
│   ├── influencerRecommender.ts # 인플루언서 추천 서비스
│   ├── contactAutomation.ts     # 연락 자동화 서비스
│   └── performanceTracker.ts    # 성과 관리 서비스
├── types/              # TypeScript 타입 정의
├── data/               # 더미 데이터
└── App.tsx            # 메인 앱 컴포넌트
```

## 주요 서비스

### PromotionGenerator
- 템플릿 기반 홍보 문구 생성
- 제품 정보 자동 치환
- 채널별 최적화
- 해시태그 자동 생성

### InfluencerRecommender
- 카테고리 기반 추천
- 성과 기반 추천
- 예산 기반 최적화
- 필터링 및 정렬

### ContactAutomation
- 이메일/DM 템플릿 생성
- 자동 발송 시스템
- 상태 추적
- 후속 연락 관리

### PerformanceTracker
- 실시간 성과 계산
- 데이터 수집 및 분석
- 리포트 생성
- 예측 모델링

## 사용법

1. **대시보드**: 전체 성과 현황 확인
2. **인플루언서 발굴**: 제품에 맞는 인플루언서 검색 및 선택
3. **홍보 문구 생성**: 제품 정보 입력 후 자동 생성
4. **연락 자동화**: 선택된 인플루언서에게 자동 연락
5. **캠페인 관리**: 캠페인 생성 및 관리
6. **성과 분석**: 상세한 성과 분석 및 인사이트

## 라이선스

MIT License 