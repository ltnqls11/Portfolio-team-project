# Blog Influencer RPA API 문서

## 기본 정보
- Base URL: `http://localhost:5000/api`
- 인증: JWT Bearer Token
- Content-Type: `application/json`

## 인증 API

### POST /auth/login
사용자 로그인

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "사용자명"
  }
}
```

## 인플루언서 API

### GET /influencers
인플루언서 목록 조회

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 항목 수 (기본값: 20)
- `platform`: 플랫폼 필터 (naver, tistory, wordpress, medium, velog)
- `category`: 카테고리 필터
- `minScore`: 최소 점수 필터

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "인플루언서명",
      "blogUrl": "https://blog.example.com",
      "platform": "naver",
      "email": "influencer@example.com",
      "metrics": {
        "trafficScore": 85,
        "engagementRate": 4.2,
        "postingFrequency": 12
      },
      "score": {
        "overallScore": 87.5,
        "engagementScore": 90.0,
        "contentQualityScore": 85.0
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

### GET /influencers/:id
특정 인플루언서 상세 정보

**Response:**
```json
{
  "id": 1,
  "name": "인플루언서명",
  "blogUrl": "https://blog.example.com",
  "platform": "naver",
  "email": "influencer@example.com",
  "contactInfo": {
    "phone": "010-1234-5678",
    "instagram": "@username"
  },
  "metrics": {
    "trafficScore": 85,
    "engagementRate": 4.2,
    "postingFrequency": 12,
    "domainAuthority": 45,
    "followerCount": 15000
  },
  "categories": [
    {
      "id": 1,
      "name": "기술",
      "relevanceScore": 0.95
    }
  ],
  "recentPosts": [
    {
      "id": 1,
      "title": "최신 포스트 제목",
      "url": "https://blog.example.com/post1",
      "publishedAt": "2024-01-15T10:00:00Z",
      "viewCount": 1250,
      "likeCount": 45,
      "commentCount": 12
    }
  ],
  "socialConnections": [
    {
      "platform": "instagram",
      "username": "@username",
      "followerCount": 25000,
      "verified": true
    }
  ]
}
```

## 스크래핑 API

### POST /scraping/start
스크래핑 작업 시작

**Request Body:**
```json
{
  "platform": "naver",
  "targetUrl": "https://blog.naver.com",
  "options": {
    "maxPages": 10,
    "categories": ["기술", "라이프스타일"],
    "minFollowers": 1000
  }
}
```

**Response:**
```json
{
  "jobId": "job_12345",
  "status": "started",
  "message": "스크래핑 작업이 시작되었습니다."
}
```

### GET /scraping/status/:jobId
스크래핑 작업 상태 확인

**Response:**
```json
{
  "jobId": "job_12345",
  "status": "running",
  "progress": 65,
  "startedAt": "2024-01-15T10:00:00Z",
  "estimatedCompletion": "2024-01-15T10:30:00Z",
  "resultsCount": 45
}
```

## 분석 API

### POST /analytics/content
콘텐츠 분석

**Request Body:**
```json
{
  "content": "분석할 블로그 콘텐츠 텍스트"
}
```

**Response:**
```json
{
  "categories": [
    {
      "name": "기술",
      "confidence": 0.92
    }
  ],
  "sentiment": {
    "score": 0.75,
    "label": "positive"
  },
  "keywords": ["React", "JavaScript", "프론트엔드"],
  "readabilityScore": 78,
  "wordCount": 1250
}
```

### GET /analytics/dashboard
대시보드 데이터

**Response:**
```json
{
  "summary": {
    "totalInfluencers": 1250,
    "activeInfluencers": 890,
    "totalPosts": 15600,
    "avgEngagementRate": 3.8
  },
  "platformDistribution": {
    "naver": 450,
    "tistory": 320,
    "wordpress": 280,
    "medium": 150,
    "velog": 50
  },
  "categoryDistribution": {
    "기술": 380,
    "라이프스타일": 290,
    "뷰티": 220,
    "요리": 180,
    "기타": 180
  },
  "engagementTrends": [
    {
      "date": "2024-01-01",
      "avgEngagement": 3.2
    }
  ]
}
```

## 에러 응답

모든 API는 다음과 같은 형식의 에러 응답을 반환합니다:

```json
{
  "error": "에러 메시지",
  "code": "ERROR_CODE",
  "details": "상세 에러 정보"
}
```

### 상태 코드
- `200`: 성공
- `201`: 생성 성공
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `429`: 요청 제한 초과
- `500`: 서버 에러