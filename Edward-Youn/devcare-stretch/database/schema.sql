-- DevCare Stretch Database Schema for Supabase
-- 이 스크립트를 Supabase SQL Editor에서 실행하세요

-- 1. 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(100) NOT NULL,
    slack_id VARCHAR(50) UNIQUE NOT NULL,
    symptoms TEXT[] DEFAULT ARRAY[]::TEXT[],
    symptom_details TEXT DEFAULT '',
    pain_level INTEGER DEFAULT 0 CHECK (pain_level >= 0 AND pain_level <= 10),
    work_environment TEXT DEFAULT '',
    work_hours VARCHAR(50) DEFAULT '',
    daily_habits TEXT DEFAULT '',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 설문 응답 테이블
CREATE TABLE IF NOT EXISTS survey_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symptoms TEXT[] NOT NULL,
    symptom_details TEXT DEFAULT '',
    pain_level INTEGER DEFAULT 0 CHECK (pain_level >= 0 AND pain_level <= 10),
    work_environment TEXT DEFAULT '',
    work_hours VARCHAR(50) DEFAULT '',
    daily_habits TEXT DEFAULT '',
    screening_summary TEXT DEFAULT '',
    response_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 영상 테이블
CREATE TABLE IF NOT EXISTS videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id VARCHAR(20) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    thumbnail_url TEXT DEFAULT '',
    channel_title VARCHAR(200) DEFAULT '',
    published_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    has_caption BOOLEAN DEFAULT FALSE,
    category VARCHAR(50) DEFAULT 'general',
    approach_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 영상 댓글 요약 테이블
CREATE TABLE IF NOT EXISTS video_comment_summary (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id) ON DELETE CASCADE,
    total_comments INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    positive_ratio DECIMAL(5,4) DEFAULT 0.0,
    negative_ratio DECIMAL(5,4) DEFAULT 0.0,
    effect_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    side_effect_keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    representative_positive TEXT DEFAULT '',
    representative_negative TEXT DEFAULT '',
    overall_sentiment VARCHAR(20) DEFAULT 'neutral',
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 증상-영상 연관도 인덱스
CREATE TABLE IF NOT EXISTS symptom_index (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id VARCHAR(20) REFERENCES videos(video_id) ON DELETE CASCADE,
    symptom_name VARCHAR(100) NOT NULL,
    relevance_score DECIMAL(5,4) DEFAULT 0.0,
    indexed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, symptom_name)
);

-- 6. 운동 루틴 테이블
CREATE TABLE IF NOT EXISTS workout_routines (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    routine_name VARCHAR(200) DEFAULT 'My Routine',
    time_slots TEXT[] DEFAULT ARRAY[]::TEXT[],
    weekdays INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    session_duration INTEGER DEFAULT 30,
    selected_videos JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- 7. 운동 이벤트 테이블
CREATE TABLE IF NOT EXISTS workout_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(20) NOT NULL,
    video_ids TEXT[] DEFAULT ARRAY[]::TEXT[],
    duration_minutes INTEGER DEFAULT 0,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_users_slack_id ON users(slack_id);
CREATE INDEX IF NOT EXISTS idx_videos_video_id ON videos(video_id);
CREATE INDEX IF NOT EXISTS idx_symptom_index_symptom_name ON symptom_index(symptom_name);
CREATE INDEX IF NOT EXISTS idx_workout_events_user_id ON workout_events(user_id);

-- 샘플 데이터 삽입
INSERT INTO users (name, contact, slack_id, symptoms, pain_level) 
VALUES 
    ('김개발', 'kim@example.com', 'U01234567', ARRAY['거북목', '라운드숄더'], 6),
    ('이디자인', 'lee@example.com', 'U01234568', ARRAY['허리통증'], 4),
    ('박기획', 'park@example.com', 'U01234569', ARRAY['손목통증'], 3)
ON CONFLICT (slack_id) DO NOTHING;

-- 샘플 영상 데이터
INSERT INTO videos (video_id, title, description, channel_title, duration_seconds, view_count, category)
VALUES 
    ('dQw4w9WgXcQ', '거북목 교정 운동 5분', '간단한 거북목 교정 스트레칭', '헬스채널', 300, 125000, 'stretching'),
    ('abc123xyz', '라운드숄더 개선 운동', '어깨 근육 강화 운동', '피트니스TV', 480, 89000, 'strengthening'),
    ('def456uvw', '허리 통증 완화 스트레칭', '요추 스트레칭 루틴', '요가마스터', 720, 156000, 'stretching')
ON CONFLICT (video_id) DO NOTHING;

-- 증상 인덱스 데이터
INSERT INTO symptom_index (video_id, symptom_name, relevance_score)
VALUES 
    ('dQw4w9WgXcQ', '거북목', 0.95),
    ('abc123xyz', '라운드숄더', 0.92),
    ('def456uvw', '허리통증', 0.94)
ON CONFLICT (video_id, symptom_name) DO NOTHING;

SELECT 'DevCare Stretch 데이터베이스 스키마가 성공적으로 생성되었습니다!' as message;