# 마케팅 플랫폼 백엔드 API 명세서

## 기술 스택
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy/SQLModel
- **Authentication**: JWT
- **Task Queue**: Celery + Redis
- **File Storage**: AWS S3 또는 로컬 스토리지

## 데이터베이스 스키마

### 1. clients (클라이언트/광고주)
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    contact_email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 2. campaigns (캠페인)
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    title VARCHAR(255) NOT NULL,
    objective TEXT,
    budget DECIMAL(12,2),
    start_at TIMESTAMP,
    end_at TIMESTAMP,
    channels TEXT[], -- JSON array of channel names
    keywords TEXT[], -- JSON array of keywords
    reference_urls TEXT[], -- JSON array of URLs
    status VARCHAR(20) DEFAULT 'draft', -- draft, active, paused, completed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3. copy_variants (문구 변형)
```sql
CREATE TABLE copy_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    channel VARCHAR(50) NOT NULL,
    tone VARCHAR(50),
    length INTEGER,
    text TEXT NOT NULL,
    score DECIMAL(3,2), -- 0.00 to 1.00
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. creators (크리에이터/인플루언서)
```sql
CREATE TABLE creators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(50) NOT NULL,
    handle VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    followers INTEGER,
    engagement_rate DECIMAL(5,4), -- 0.0000 to 1.0000
    email VARCHAR(255),
    dm_url VARCHAR(500),
    active_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 5. outreach (아웃리치/연락)
```sql
CREATE TABLE outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    creator_id UUID REFERENCES creators(id),
    channel VARCHAR(50),
    method VARCHAR(20), -- email, dm
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, replied, accepted, rejected
    last_event_at TIMESTAMP DEFAULT NOW(),
    message_template_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. deliverables (결과물)
```sql
CREATE TABLE deliverables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    creator_id UUID REFERENCES creators(id),
    url VARCHAR(500) NOT NULL,
    posted_at TIMESTAMP,
    metrics JSONB, -- views, likes, comments, shares, clicks
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7. events (이벤트 로그)
```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API 엔드포인트

### 인증
```
POST /auth/login
POST /auth/register
POST /auth/refresh
POST /auth/logout
```

### 클라이언트 관리
```
GET    /api/clients
POST   /api/clients
GET    /api/clients/{client_id}
PUT    /api/clients/{client_id}
DELETE /api/clients/{client_id}
```

### 캠페인 관리
```
GET    /api/campaigns
POST   /api/campaigns
GET    /api/campaigns/{campaign_id}
PUT    /api/campaigns/{campaign_id}
DELETE /api/campaigns/{campaign_id}
GET    /api/campaigns/{campaign_id}/stats
```

### 문구 생성
```
POST   /api/copy/generate
GET    /api/campaigns/{campaign_id}/copy-variants
POST   /api/campaigns/{campaign_id}/copy-variants
PATCH  /api/copy-variants/{variant_id}/approve
DELETE /api/copy-variants/{variant_id}
```

### 크리에이터 관리
```
GET    /api/creators
POST   /api/creators
GET    /api/creators/{creator_id}
PUT    /api/creators/{creator_id}
DELETE /api/creators/{creator_id}
GET    /api/creators/search
```

### 아웃리치 관리
```
GET    /api/outreach
POST   /api/outreach
GET    /api/campaigns/{campaign_id}/outreach
PATCH  /api/outreach/{outreach_id}/status
GET    /api/outreach/{outreach_id}/messages
```

### 결과물 관리
```
GET    /api/campaigns/{campaign_id}/deliverables
POST   /api/deliverables
PUT    /api/deliverables/{deliverable_id}
DELETE /api/deliverables/{deliverable_id}
```

### 분석 및 리포트
```
GET    /api/campaigns/{campaign_id}/analytics
GET    /api/campaigns/{campaign_id}/report
GET    /api/dashboard/stats
```

## API 응답 예시

### 캠페인 생성 요청
```json
POST /api/campaigns
{
  "client_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "신제품 런칭 캠페인",
  "objective": "신제품 인지도 향상 및 초기 판매 촉진",
  "budget": 5000000,
  "start_at": "2024-01-01T00:00:00Z",
  "end_at": "2024-01-31T23:59:59Z",
  "channels": ["naver_blog", "instagram_feed", "kakao_channel"],
  "keywords": ["신제품", "혁신", "편리함", "가성비"],
  "reference_urls": ["https://example.com/product"]
}
```

### 문구 생성 요청
```json
POST /api/copy/generate
{
  "campaign_id": "123e4567-e89b-12d3-a456-426614174001",
  "product_description": "혁신적인 스마트 홈 디바이스",
  "benefits": ["편리함", "에너지 절약", "스마트 제어"],
  "target": {
    "age": "25-40",
    "interests": ["기술", "홈인테리어", "라이프스타일"]
  },
  "keywords": ["스마트홈", "IoT", "편리함"],
  "channel": "naver_blog"
}
```

### 문구 생성 응답
```json
{
  "variants": [
    {
      "title": "집이 똑똑해진다! 혁신적인 스마트홈 디바이스 체험기",
      "content": "안녕하세요! 오늘은 정말 신기한 스마트홈 디바이스를 소개해드리려고 해요...",
      "hashtags": ["#스마트홈", "#IoT", "#편리함", "#기술", "#라이프스타일"],
      "cta": "지금 바로 체험해보세요!",
      "length": 1850,
      "score": 0.92
    }
  ]
}
```

### 크리에이터 검색 응답
```json
GET /api/creators/search?category=lifestyle&min_followers=1000&max_followers=50000
{
  "creators": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "platform": "instagram",
      "handle": "@lifestyle_blogger",
      "category": "lifestyle",
      "followers": 25000,
      "engagement_rate": 0.0450,
      "email": "contact@blogger.com",
      "active_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

## 백그라운드 작업

### Celery 태스크
```python
# 문구 생성 태스크
@celery.task
def generate_copy_variants(campaign_id: str, generation_request: dict):
    # OpenAI API 호출하여 문구 생성
    pass

# 크리에이터 데이터 수집 태스크
@celery.task
def crawl_creator_data(platform: str, category: str):
    # 웹 크롤링으로 크리에이터 정보 수집
    pass

# 이메일 발송 태스크
@celery.task
def send_outreach_email(outreach_id: str):
    # SMTP를 통한 이메일 발송
    pass

# 성과 데이터 수집 태스크
@celery.task
def collect_performance_metrics(deliverable_id: str):
    # 소셜 미디어 API를 통한 성과 데이터 수집
    pass
```

## 보안 고려사항

1. **API 키 관리**: 환경 변수로 관리, 암호화 저장
2. **Rate Limiting**: 각 엔드포인트별 요청 제한
3. **데이터 검증**: Pydantic 모델을 통한 입력 검증
4. **CORS 설정**: 프론트엔드 도메인만 허용
5. **SQL Injection 방지**: ORM 사용, 파라미터화된 쿼리
6. **개인정보 보호**: 크리에이터 연락처 암호화 저장

## 배포 및 인프라

### Docker 구성
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/marketing_platform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=marketing_platform
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```