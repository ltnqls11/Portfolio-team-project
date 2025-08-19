# API 가이드

온라인 마케팅 연계 플랫폼의 REST API 사용 가이드입니다.

## 기본 정보

- **Base URL**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 인증

현재 버전에서는 인증이 구현되지 않았습니다. 향후 JWT 토큰 기반 인증을 추가할 예정입니다.

## API 엔드포인트

### 1. 헬스 체크

```http
GET /health
```

서버 상태를 확인합니다.

**응답 예시:**
```json
{
  "status": "healthy",
  "service": "marketing-platform-api"
}
```

### 2. 클라이언트 관리

#### 클라이언트 생성
```http
POST /api/clients/
```

**요청 본문:**
```json
{
  "name": "테스트 회사",
  "industry": "뷰티",
  "contact_email": "test@example.com",
  "contact_phone": "010-1234-5678",
  "company_url": "https://test-company.com",
  "description": "테스트용 클라이언트입니다."
}
```

#### 클라이언트 목록 조회
```http
GET /api/clients/
```

**쿼리 파라미터:**
- `industry`: 업종 필터
- `skip`: 건너뛸 개수 (기본값: 0)
- `limit`: 최대 개수 (기본값: 100)

### 3. 캠페인 관리

#### 캠페인 생성
```http
POST /api/campaigns/
```

**요청 본문:**
```json
{
  "client_id": 1,
  "title": "신제품 런칭 캠페인",
  "objective": "새로운 스킨케어 제품의 인지도 향상 및 구매 유도",
  "budget": 1000000.0,
  "keywords": "[\"스킨케어\", \"보습\", \"안티에이징\"]",
  "reference_urls": "[\"https://example.com/product1\"]",
  "channels": "[\"naver_blog\", \"instagram\"]"
}
```

#### 캠페인 목록 조회
```http
GET /api/campaigns/
```

**쿼리 파라미터:**
- `client_id`: 클라이언트 ID 필터
- `status`: 상태 필터 (draft, active, paused, completed, cancelled)
- `skip`: 건너뛸 개수
- `limit`: 최대 개수

### 4. 크리에이터 관리

#### 크리에이터 등록
```http
POST /api/creators/
```

**요청 본문:**
```json
{
  "platform": "naver_blog",
  "handle": "beauty_blogger_123",
  "category": "뷰티",
  "followers": 15000,
  "engagement_rate": 0.035,
  "email": "blogger@example.com",
  "notes": "뷰티 전문 블로거"
}
```

#### 크리에이터 검색
```http
GET /api/creators/
```

**쿼리 파라미터:**
- `platform`: 플랫폼 필터 (naver_blog, instagram, tistory, kakao_channel)
- `category`: 카테고리 필터
- `min_followers`: 최소 팔로워 수
- `max_followers`: 최대 팔로워 수
- `min_engagement`: 최소 참여율
- `active_days`: 최근 활동일 기준 (일)

### 5. 문구 생성

#### 홍보 문구 생성
```http
POST /api/copy/generate/{campaign_id}
```

**요청 본문:**
```json
["naver_blog", "instagram"]
```

#### 캠페인 문구 조회
```http
GET /api/copy/campaign/{campaign_id}
```

**쿼리 파라미터:**
- `channel`: 채널 필터
- `approved_only`: 승인된 문구만 조회 (true/false)

#### 문구 승인/거부
```http
PATCH /api/copy/{variant_id}/approve
PATCH /api/copy/{variant_id}/reject
```

### 6. 크롤링

#### 네이버 블로그 크롤링
```http
POST /api/crawling/naver/search
```

**쿼리 파라미터:**
- `keyword`: 검색 키워드 (필수)
- `category`: 카테고리 (선택)
- `page_count`: 크롤링할 페이지 수 (기본값: 3)

#### 인스타그램 해시태그 크롤링
```http
POST /api/crawling/instagram/hashtag
```

**쿼리 파라미터:**
- `hashtag`: 해시태그 (필수)
- `limit`: 최대 계정 수 (기본값: 50)

#### 크롤링 상태 조회
```http
GET /api/crawling/status
```

#### 트렌딩 데이터 조회
```http
GET /api/crawling/trending
```

## 에러 코드

| 상태 코드 | 설명 |
|----------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 404 | 리소스를 찾을 수 없음 |
| 422 | 유효성 검사 실패 |
| 500 | 서버 내부 오류 |

## 사용 예시

### Python 예시

```python
import requests

# 클라이언트 생성
client_data = {
    "name": "테스트 회사",
    "industry": "뷰티",
    "contact_email": "test@example.com"
}

response = requests.post(
    "http://localhost:8000/api/clients/",
    json=client_data
)

client = response.json()
print(f"클라이언트 생성됨: {client['id']}")

# 캠페인 생성
campaign_data = {
    "client_id": client['id'],
    "title": "신제품 캠페인",
    "objective": "제품 홍보",
    "keywords": '["뷰티", "스킨케어"]'
}

response = requests.post(
    "http://localhost:8000/api/campaigns/",
    json=campaign_data
)

campaign = response.json()
print(f"캠페인 생성됨: {campaign['id']}")
```

### JavaScript 예시

```javascript
// 클라이언트 생성
const clientData = {
  name: "테스트 회사",
  industry: "뷰티",
  contact_email: "test@example.com"
};

const response = await fetch("http://localhost:8000/api/clients/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(clientData)
});

const client = await response.json();
console.log(`클라이언트 생성됨: ${client.id}`);
```

## 개발 팁

1. **API 문서 활용**: `/docs` 엔드포인트에서 Swagger UI를 통해 API를 테스트할 수 있습니다.

2. **에러 처리**: 모든 API 응답에는 적절한 HTTP 상태 코드가 포함됩니다.

3. **페이지네이션**: 목록 조회 API는 `skip`과 `limit` 파라미터를 지원합니다.

4. **필터링**: 대부분의 목록 API는 다양한 필터 옵션을 제공합니다.

5. **백그라운드 작업**: 크롤링과 같은 시간이 오래 걸리는 작업은 백그라운드에서 실행됩니다.