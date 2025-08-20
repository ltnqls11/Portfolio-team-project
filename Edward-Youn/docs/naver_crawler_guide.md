# 네이버 블로그 크롤러 실행 가이드

## 📋 사전 준비

### 1. 환경 변수 설정
`.env.supabase` 파일이 프로젝트 루트에 있는지 확인하세요.

```bash
# Supabase Configuration
SUPABASE_URL=https://ohemvgnzikgdzjkzipvy.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
```

### 2. Supabase 테이블 생성
Supabase 대시보드에서 다음 SQL을 실행하세요:

```sql
CREATE TABLE IF NOT EXISTS blogs (
    id SERIAL PRIMARY KEY,
    blog_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    post_count INTEGER DEFAULT 0,
    price DECIMAL(10, 2),
    blog_url VARCHAR(500) NOT NULL UNIQUE,
    platform VARCHAR(50) DEFAULT 'naver',
    followers INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2),
    last_post_date TIMESTAMP,
    crawled_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    notes TEXT
);

-- 인덱스 생성
CREATE INDEX idx_blogs_category ON blogs(category);
CREATE INDEX idx_blogs_platform ON blogs(platform);
CREATE INDEX idx_blogs_active ON blogs(active);
```

### 3. 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

## 🚀 실행 방법

### 1. API 서버 실행
```bash
cd backend
python main.py
```

서버가 실행되면 다음 주소에서 확인할 수 있습니다:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 테스트 실행
새 터미널을 열고:
```bash
cd backend
python test_naver_crawler.py
```

## 📌 주요 API 엔드포인트

### 블로그 검색 및 저장
```bash
POST /api/naver-blogs/search
```
파라미터:
- `keyword`: 검색 키워드 (필수)
- `category`: 카테고리 (선택)
- `max_results`: 최대 결과 수 (기본값: 30)

예시:
```bash
curl -X POST "http://localhost:8000/api/naver-blogs/search?keyword=맛집&category=맛집&max_results=10"
```

### 저장된 블로그 조회
```bash
GET /api/naver-blogs/blogs
```
파라미터:
- `category`: 카테고리 필터 (선택)
- `limit`: 조회 개수 (기본값: 50)
- `offset`: 시작 위치 (기본값: 0)

### 블로그 단가 업데이트
```bash
PATCH /api/naver-blogs/blogs/{blog_id}
```
Body:
```json
{
    "price": 50000
}
```

### 통계 조회
```bash
GET /api/naver-blogs/statistics
```

## 🔍 직접 크롤러 테스트

Python 콘솔에서 직접 테스트:

```python
from crawlers.naver_supabase_crawler import NaverBlogSupabaseCrawler

# 크롤러 인스턴스 생성
crawler = NaverBlogSupabaseCrawler()

# 블로그 검색 및 저장
stats = crawler.search_and_save_blogs(
    keyword="스킨케어",
    category="뷰티",
    max_results=10
)
print(stats)

# 저장된 블로그 조회
blogs = crawler.get_saved_blogs(category="뷰티", limit=5)
for blog in blogs:
    print(f"{blog['blog_name']}: {blog['post_count']}개 포스트")

# 통계 조회
stats = crawler.get_statistics()
print(f"전체 블로그: {stats['total_blogs']}개")
```

## 📊 카테고리 목록

지원하는 카테고리:
- 일상
- 맛집
- 여행
- 패션
- 뷰티
- IT
- 육아
- 인테리어
- 건강
- 반려동물

## 🐛 문제 해결

### 1. Supabase 연결 오류
```
ValueError: Supabase URL과 Service Key가 필요합니다.
```
**해결**: `.env.supabase` 파일이 있는지 확인하고, 올바른 키가 설정되어 있는지 확인하세요.

### 2. 테이블이 없음 오류
```
blogs 테이블이 없습니다
```
**해결**: Supabase 대시보드에서 위의 SQL을 실행하여 테이블을 생성하세요.

### 3. 크롤링 속도가 느림
크롤링 속도는 네이버 서버에 부담을 주지 않기 위해 의도적으로 제한됩니다.
- 기본 지연: 2초
- 조정 방법: `NaverBlogSupabaseCrawler(delay_seconds=1.5)`

### 4. 검색 결과가 없음
- 검색어가 너무 구체적이거나 특수한 경우 결과가 없을 수 있습니다.
- 더 일반적인 키워드로 시도해보세요.

## 📈 성능 최적화 팁

1. **배치 처리**: 여러 키워드를 한 번에 처리할 때는 순차적으로 실행
2. **캐싱**: 자주 조회하는 데이터는 Redis 캐싱 고려
3. **비동기 처리**: BackgroundTasks를 활용한 비동기 크롤링

## 🔒 보안 주의사항

1. **API 키 관리**: 
   - `.env.supabase` 파일을 절대 git에 커밋하지 마세요
   - `.gitignore`에 포함되어 있는지 확인

2. **Rate Limiting**:
   - 너무 빠른 속도로 크롤링하면 IP가 차단될 수 있습니다
   - 적절한 지연 시간을 유지하세요

3. **데이터 보호**:
   - 수집한 블로그 정보는 개인정보를 포함할 수 있습니다
   - 적절한 보안 조치를 취하세요

## 📝 추가 개발 계획

- [ ] 인스타그램 크롤러 연동
- [ ] 블로그 품질 평가 시스템
- [ ] 자동 가격 책정 알고리즘
- [ ] 대시보드 UI 개발
- [ ] 실시간 알림 시스템

## 📞 지원

문제가 발생하거나 추가 기능이 필요한 경우:
- 이슈 등록: GitHub Issues
- 이메일: younjc7450@gmail.com

---

*Last Updated: 2025-01-20*
