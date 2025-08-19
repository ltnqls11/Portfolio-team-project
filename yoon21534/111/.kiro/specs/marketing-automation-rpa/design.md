# 설계 문서

## 개요

마케팅 자동화 RPA 시스템은 마이크로서비스 아키텍처를 기반으로 한 풀스택 웹 애플리케이션입니다. React 기반 프론트엔드와 Node.js/Express 백엔드, PostgreSQL 데이터베이스로 구성되며, 인플루언서 데이터 수집, AI 기반 콘텐츠 생성, 이메일 자동화 기능을 제공합니다.

## 아키텍처

### 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React SPA]
        B[Redux Store]
        C[React Router]
    end
    
    subgraph "API Gateway"
        D[Express.js Server]
        E[Authentication Middleware]
        F[Rate Limiting]
    end
    
    subgraph "Service Layer"
        G[Influencer Service]
        H[Email Service]
        I[Template Service]
        J[Analytics Service]
    end
    
    subgraph "External APIs"
        K[Instagram API]
        L[YouTube API]
        M[TikTok API]
        N[OpenAI API]
        O[Email Provider API]
    end
    
    subgraph "Data Layer"
        P[PostgreSQL]
        Q[Redis Cache]
        R[File Storage]
    end
    
    A --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    
    G --> K
    G --> L
    G --> M
    H --> N
    H --> O
    
    G --> P
    H --> P
    I --> P
    J --> P
    
    G --> Q
    H --> Q`
``

### 기술 스택

**프론트엔드:**
- React 18 (최신 버전)
- Redux Toolkit (상태 관리)
- React Router v6 (라우팅)
- Material-UI v5 (UI 컴포넌트)
- Axios (HTTP 클라이언트)
- React Query (서버 상태 관리)

**백엔드:**
- Node.js 18+
- Express.js 4.x
- TypeScript
- Prisma ORM
- Passport.js (OAuth 2.0)
- Bull Queue (작업 큐)
- Winston (로깅)

**데이터베이스 및 캐시:**
- PostgreSQL 14+
- Redis 6+
- AWS S3 (파일 저장소)

**외부 서비스:**
- OpenAI GPT-4 API
- SendGrid/Mailgun (이메일 발송)
- Instagram Basic Display API
- YouTube Data API v3
- TikTok Business API

## 컴포넌트 및 인터페이스

### 프론트엔드 컴포넌트 구조

```
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   ├── influencer/
│   │   ├── InfluencerList.tsx
│   │   ├── InfluencerCard.tsx
│   │   ├── InfluencerFilter.tsx
│   │   └── InfluencerSearch.tsx
│   ├── email/
│   │   ├── EmailTemplateEditor.tsx
│   │   ├── EmailPreview.tsx
│   │   ├── BulkEmailSender.tsx
│   │   └── EmailStatusTracker.tsx
│   └── dashboard/
│       ├── AnalyticsDashboard.tsx
│       ├── CampaignMetrics.tsx
│       └── RealtimeStats.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── InfluencerManagement.tsx
│   ├── EmailCampaigns.tsx
│   └── Settings.tsx
├── hooks/
│   ├── useInfluencers.ts
│   ├── useEmailCampaigns.ts
│   └── useAuth.ts
├── store/
│   ├── slices/
│   │   ├── authSlice.ts
│   │   ├── influencerSlice.ts
│   │   └── emailSlice.ts
│   └── store.ts
└── services/
    ├── api.ts
    ├── authService.ts
    └── websocketService.ts
```

### 백엔드 API 구조

```
src/
├── controllers/
│   ├── authController.ts
│   ├── influencerController.ts
│   ├── emailController.ts
│   └── analyticsController.ts
├── services/
│   ├── influencerService.ts
│   ├── emailService.ts
│   ├── aiService.ts
│   └── platformServices/
│       ├── instagramService.ts
│       ├── youtubeService.ts
│       └── tiktokService.ts
├── models/
│   ├── User.ts
│   ├── Influencer.ts
│   ├── EmailTemplate.ts
│   └── Campaign.ts
├── middleware/
│   ├── auth.ts
│   ├── rateLimiter.ts
│   └── errorHandler.ts
├── routes/
│   ├── auth.ts
│   ├── influencers.ts
│   ├── emails.ts
│   └── analytics.ts
└── utils/
    ├── logger.ts
    ├── validator.ts
    └── apiClient.ts
```

## 데이터 모델

### 데이터베이스 스키마

```sql
-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인플루언서 테이블
CREATE TABLE influencers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    username VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    email VARCHAR(255),
    followers_count INTEGER,
    engagement_rate DECIMAL(5,2),
    category VARCHAR(100),
    bio TEXT,
    profile_image_url TEXT,
    external_id VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, external_id)
);

-- 이메일 템플릿 테이블
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB,
    user_id UUID REFERENCES users(id),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 캠페인 테이블
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_id UUID REFERENCES email_templates(id),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft',
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 이메일 발송 로그 테이블
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    influencer_id UUID REFERENCES influencers(id),
    email_address VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    content TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_influencers_platform ON influencers(platform);
CREATE INDEX idx_influencers_followers ON influencers(followers_count);
CREATE INDEX idx_email_logs_campaign ON email_logs(campaign_id);
CREATE INDEX idx_email_logs_status ON email_logs(status);
```

### TypeScript 인터페이스

```typescript
// 사용자 인터페이스
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  oauthProvider?: string;
  oauthId?: string;
  createdAt: Date;
  updatedAt: Date;
}

// 인플루언서 인터페이스
interface Influencer {
  id: string;
  platform: 'instagram' | 'youtube' | 'tiktok' | 'blog';
  username: string;
  displayName?: string;
  email?: string;
  followersCount: number;
  engagementRate: number;
  category: string;
  bio?: string;
  profileImageUrl?: string;
  externalId: string;
  lastUpdated: Date;
  createdAt: Date;
}

// 이메일 템플릿 인터페이스
interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  content: string;
  variables: Record<string, any>;
  userId: string;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// 캠페인 인터페이스
interface Campaign {
  id: string;
  name: string;
  description?: string;
  templateId: string;
  userId: string;
  status: 'draft' | 'scheduled' | 'running' | 'completed' | 'failed';
  scheduledAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// 이메일 로그 인터페이스
interface EmailLog {
  id: string;
  campaignId: string;
  influencerId: string;
  emailAddress: string;
  subject: string;
  content: string;
  status: 'pending' | 'sent' | 'failed' | 'bounced';
  sentAt?: Date;
  errorMessage?: string;
  createdAt: Date;
}
```

## 오류 처리

### 오류 처리 전략

1. **프론트엔드 오류 처리:**
   - React Error Boundary를 사용한 컴포넌트 레벨 오류 처리
   - Redux에서 비동기 작업 오류 상태 관리
   - 사용자 친화적인 오류 메시지 표시
   - 자동 재시도 메커니즘

2. **백엔드 오류 처리:**
   - 중앙화된 오류 처리 미들웨어
   - HTTP 상태 코드별 표준화된 응답 형식
   - 상세한 로깅 및 모니터링
   - 외부 API 호출 실패 시 fallback 처리

3. **API 제한 처리:**
   - 지수 백오프 알고리즘을 사용한 재시도
   - 플랫폼별 API 제한 추적 및 관리
   - 큐 시스템을 통한 요청 분산
   - 사용자에게 진행 상황 실시간 알림

### 오류 코드 정의

```typescript
enum ErrorCodes {
  // 인증 관련
  UNAUTHORIZED = 'AUTH_001',
  TOKEN_EXPIRED = 'AUTH_002',
  INVALID_CREDENTIALS = 'AUTH_003',
  
  // 인플루언서 관련
  INFLUENCER_NOT_FOUND = 'INF_001',
  PLATFORM_API_ERROR = 'INF_002',
  RATE_LIMIT_EXCEEDED = 'INF_003',
  
  // 이메일 관련
  EMAIL_SEND_FAILED = 'EMAIL_001',
  TEMPLATE_NOT_FOUND = 'EMAIL_002',
  AI_GENERATION_FAILED = 'EMAIL_003',
  
  // 시스템 관련
  DATABASE_ERROR = 'SYS_001',
  EXTERNAL_SERVICE_ERROR = 'SYS_002',
  VALIDATION_ERROR = 'SYS_003'
}
```

## 테스트 전략

### 테스트 피라미드

1. **단위 테스트 (70%)**
   - Jest + React Testing Library (프론트엔드)
   - Jest + Supertest (백엔드)
   - 모든 유틸리티 함수 및 서비스 로직 테스트
   - 컴포넌트 렌더링 및 상호작용 테스트

2. **통합 테스트 (20%)**
   - API 엔드포인트 테스트
   - 데이터베이스 연동 테스트
   - 외부 서비스 모킹 테스트
   - Redux 스토어 통합 테스트

3. **E2E 테스트 (10%)**
   - Cypress를 사용한 주요 사용자 플로우 테스트
   - 인플루언서 검색 → 이메일 생성 → 발송 전체 플로우
   - 크로스 브라우저 테스트

### 테스트 환경 설정

```typescript
// 테스트 설정 예시
describe('InfluencerService', () => {
  beforeEach(async () => {
    await setupTestDatabase();
    mockExternalAPIs();
  });

  afterEach(async () => {
    await cleanupTestDatabase();
    restoreAPIMocks();
  });

  it('should fetch influencers from multiple platforms', async () => {
    // 테스트 구현
  });
});
```

### 성능 테스트

- 대량 데이터 처리 성능 테스트
- API 응답 시간 모니터링
- 메모리 사용량 프로파일링
- 동시 사용자 부하 테스트

이 설계는 확장 가능하고 유지보수가 용이한 아키텍처를 제공하며, 모든 요구사항을 충족하는 견고한 시스템을 구축할 수 있는 기반을 제공합니다.