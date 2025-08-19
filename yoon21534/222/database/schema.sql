-- Blog Influencer RPA Database Schema

-- 인플루언서 기본 정보
CREATE TABLE influencers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    blog_url VARCHAR(500) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL, -- naver, tistory, wordpress, medium, velog
    email VARCHAR(255),
    contact_info JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 블로그 메트릭스
CREATE TABLE blog_metrics (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id) ON DELETE CASCADE,
    traffic_score INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    posting_frequency INTEGER DEFAULT 0, -- posts per month
    domain_authority INTEGER DEFAULT 0,
    follower_count INTEGER DEFAULT 0,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 콘텐츠 카테고리
CREATE TABLE content_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES content_categories(id)
);

-- 인플루언서-카테고리 매핑
CREATE TABLE influencer_categories (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES content_categories(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 0.00,
    UNIQUE(influencer_id, category_id)
);

-- 블로그 포스트
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    content TEXT,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    tags TEXT[],
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 소셜 미디어 연결
CREATE TABLE social_connections (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- instagram, youtube, twitter, etc.
    username VARCHAR(255),
    url VARCHAR(500),
    follower_count INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE
);

-- 인플루언서 점수
CREATE TABLE influencer_scores (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id) ON DELETE CASCADE,
    overall_score DECIMAL(5,2) DEFAULT 0.00,
    engagement_score DECIMAL(5,2) DEFAULT 0.00,
    content_quality_score DECIMAL(5,2) DEFAULT 0.00,
    reach_score DECIMAL(5,2) DEFAULT 0.00,
    relevance_score DECIMAL(5,2) DEFAULT 0.00,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 스크래핑 작업 로그
CREATE TABLE scraping_jobs (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    results_count INTEGER DEFAULT 0
);

-- 이메일 캠페인
CREATE TABLE email_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    template TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_count INTEGER DEFAULT 0
);

-- 이메일 발송 로그
CREATE TABLE email_logs (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES email_campaigns(id),
    influencer_id INTEGER REFERENCES influencers(id),
    email VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed, opened, replied
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    replied_at TIMESTAMP,
    error_message TEXT
);

-- 인덱스 생성
CREATE INDEX idx_influencers_platform ON influencers(platform);
CREATE INDEX idx_influencers_created_at ON influencers(created_at);
CREATE INDEX idx_blog_posts_influencer_id ON blog_posts(influencer_id);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at);
CREATE INDEX idx_blog_metrics_influencer_id ON blog_metrics(influencer_id);
CREATE INDEX idx_influencer_scores_overall_score ON influencer_scores(overall_score DESC);

-- 기본 카테고리 데이터 삽입
INSERT INTO content_categories (name, description) VALUES
('기술', 'IT, 프로그래밍, 소프트웨어 관련'),
('라이프스타일', '일상, 취미, 여행 관련'),
('뷰티', '화장품, 스킨케어, 패션 관련'),
('요리', '레시피, 맛집, 음식 관련'),
('육아', '임신, 출산, 육아 관련'),
('비즈니스', '창업, 마케팅, 경영 관련'),
('건강', '운동, 다이어트, 의료 관련'),
('교육', '학습, 자기계발, 강의 관련');