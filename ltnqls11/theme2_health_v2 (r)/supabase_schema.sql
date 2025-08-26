-- VDT 증후군 관리 시스템을 위한 포괄적인 Supabase 데이터베이스 스키마

-- 1. 사용자 정보 테이블
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    age INTEGER,
    gender VARCHAR(20),
    work_experience INTEGER,
    company VARCHAR(200),
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 사용자 증상 관리 테이블
CREATE TABLE IF NOT EXISTS user_conditions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    condition_name VARCHAR(100) NOT NULL,
    pain_score INTEGER DEFAULT 0,
    first_diagnosed_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, improved, resolved
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 작업 환경 평가 테이블
CREATE TABLE IF NOT EXISTS work_environment (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    daily_work_hours DECIMAL(3,1),
    monitor_distance INTEGER,
    monitor_height VARCHAR(50),
    chair_comfort INTEGER,
    keyboard_position VARCHAR(50),
    lighting_quality INTEGER,
    break_frequency VARCHAR(50),
    work_intensity VARCHAR(50),
    env_score INTEGER,
    evaluation_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 개인 운동 설문 데이터
CREATE TABLE IF NOT EXISTS exercise_survey (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    exercise_frequency VARCHAR(50),
    preferred_time VARCHAR(50),
    available_days TEXT[], -- 배열로 저장 ['월요일', '화요일', ...]
    preferred_duration INTEGER, -- 분 단위
    exercise_experience VARCHAR(50),
    health_conditions TEXT,
    subjective_status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 운동 관리 기록 (기존 테이블 개선)
CREATE TABLE IF NOT EXISTS exercise_management (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL, -- exercise_log, pain_data, routine_complete
    date DATE NOT NULL,
    value TEXT NOT NULL,
    details JSONB, -- 추가 상세 정보를 JSON으로 저장
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_email, data_type, date) -- 중복 방지
);

-- 6. 운동 루틴 추천 기록
CREATE TABLE IF NOT EXISTS exercise_routines (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    routine_date DATE NOT NULL,
    exercise_purpose VARCHAR(100), -- 예방, 운동, 재활
    recommended_exercises JSONB, -- 추천된 운동 목록
    completed_exercises JSONB, -- 완료한 운동 목록
    total_duration INTEGER, -- 총 운동 시간(분)
    completion_rate DECIMAL(5,2), -- 완료율
    ai_feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. YouTube 영상 시청 기록
CREATE TABLE IF NOT EXISTS video_watch_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    video_id VARCHAR(100),
    video_title TEXT,
    video_url TEXT,
    channel_name VARCHAR(200),
    duration_seconds INTEGER,
    watch_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completion_percentage DECIMAL(5,2),
    effectiveness_rating INTEGER, -- 1-5 평점
    notes TEXT
);

-- 8. 통증 변화 추적
CREATE TABLE IF NOT EXISTS pain_tracking (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    tracking_date DATE NOT NULL,
    condition_name VARCHAR(100),
    morning_pain_level INTEGER,
    afternoon_pain_level INTEGER,
    evening_pain_level INTEGER,
    average_pain_level DECIMAL(3,1),
    pain_triggers TEXT,
    relief_methods TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. 알림 설정
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    notification_type VARCHAR(50), -- email, slack
    work_start_time TIME,
    work_end_time TIME,
    break_interval INTEGER, -- 분 단위
    is_active BOOLEAN DEFAULT true,
    slack_webhook_url TEXT,
    notification_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. 고객 상담 기록 (AI 채팅)
CREATE TABLE IF NOT EXISTS consultation_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    consultation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_message TEXT,
    ai_response TEXT,
    consultation_type VARCHAR(50), -- symptom_analysis, exercise_advice, etc.
    satisfaction_rating INTEGER,
    follow_up_required BOOLEAN DEFAULT false
);

-- 11. 운동 효과 분석
CREATE TABLE IF NOT EXISTS exercise_effectiveness (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    analysis_period VARCHAR(50), -- weekly, monthly
    start_date DATE,
    end_date DATE,
    initial_pain_average DECIMAL(3,1),
    final_pain_average DECIMAL(3,1),
    pain_improvement_percentage DECIMAL(5,2),
    exercise_compliance_rate DECIMAL(5,2),
    most_effective_exercises JSONB,
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 12. 시스템 사용 통계
CREATE TABLE IF NOT EXISTS usage_statistics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email) ON DELETE CASCADE,
    feature_name VARCHAR(100),
    usage_count INTEGER DEFAULT 1,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_duration_minutes INTEGER,
    device_type VARCHAR(50),
    browser_info VARCHAR(200)
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_user_conditions_email ON user_conditions(user_email);
CREATE INDEX IF NOT EXISTS idx_exercise_management_user_date ON exercise_management(user_email, date);
CREATE INDEX IF NOT EXISTS idx_pain_tracking_user_date ON pain_tracking(user_email, tracking_date);
CREATE INDEX IF NOT EXISTS idx_video_history_user ON video_watch_history(user_email);
CREATE INDEX IF NOT EXISTS idx_routines_user_date ON exercise_routines(user_email, routine_date);
CREATE INDEX IF NOT EXISTS idx_consultation_user ON consultation_history(user_email);

-- 뷰 생성 (복잡한 쿼리 단순화)

-- 사용자 종합 정보 뷰
CREATE OR REPLACE VIEW user_comprehensive_view AS
SELECT 
    u.email,
    u.name,
    u.age,
    u.gender,
    u.work_experience,
    ARRAY_AGG(DISTINCT uc.condition_name) AS conditions,
    AVG(uc.pain_score) AS avg_pain_score,
    we.env_score,
    we.daily_work_hours,
    es.exercise_frequency,
    ns.notification_type,
    COUNT(DISTINCT em.date) AS total_exercise_days
FROM users u
LEFT JOIN user_conditions uc ON u.email = uc.user_email
LEFT JOIN work_environment we ON u.email = we.user_email
LEFT JOIN exercise_survey es ON u.email = es.user_email
LEFT JOIN notification_settings ns ON u.email = ns.user_email
LEFT JOIN exercise_management em ON u.email = em.user_email AND em.data_type = 'exercise_log'
GROUP BY u.email, u.name, u.age, u.gender, u.work_experience, 
         we.env_score, we.daily_work_hours, es.exercise_frequency, ns.notification_type;

-- 주간 운동 및 통증 추세 뷰
CREATE OR REPLACE VIEW weekly_progress_view AS
SELECT 
    user_email,
    DATE_TRUNC('week', date) AS week_start,
    COUNT(CASE WHEN data_type = 'exercise_log' THEN 1 END) AS exercise_count,
    AVG(CASE WHEN data_type = 'pain_data' THEN CAST(value AS INTEGER) END) AS avg_pain_level,
    MAX(date) AS last_activity_date
FROM exercise_management
WHERE date >= CURRENT_DATE - INTERVAL '4 weeks'
GROUP BY user_email, DATE_TRUNC('week', date)
ORDER BY user_email, week_start DESC;

-- 함수 생성

-- 사용자 통증 개선율 계산 함수
CREATE OR REPLACE FUNCTION calculate_pain_improvement(p_user_email VARCHAR)
RETURNS TABLE(
    improvement_rate DECIMAL,
    initial_pain DECIMAL,
    current_pain DECIMAL,
    days_tracked INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH pain_data AS (
        SELECT 
            user_email,
            tracking_date,
            average_pain_level,
            ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY tracking_date ASC) AS rn_asc,
            ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY tracking_date DESC) AS rn_desc
        FROM pain_tracking
        WHERE user_email = p_user_email
    )
    SELECT 
        CASE 
            WHEN MAX(CASE WHEN rn_asc = 1 THEN average_pain_level END) > 0 
            THEN ((MAX(CASE WHEN rn_asc = 1 THEN average_pain_level END) - 
                   MAX(CASE WHEN rn_desc = 1 THEN average_pain_level END)) / 
                   MAX(CASE WHEN rn_asc = 1 THEN average_pain_level END) * 100)::DECIMAL(5,2)
            ELSE 0
        END AS improvement_rate,
        MAX(CASE WHEN rn_asc = 1 THEN average_pain_level END) AS initial_pain,
        MAX(CASE WHEN rn_desc = 1 THEN average_pain_level END) AS current_pain,
        COUNT(DISTINCT tracking_date)::INTEGER AS days_tracked
    FROM pain_data;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성

-- updated_at 자동 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_conditions_updated_at BEFORE UPDATE ON user_conditions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercise_survey_updated_at BEFORE UPDATE ON exercise_survey
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 정책 설정
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_conditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_environment ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_survey ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_management ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_routines ENABLE ROW LEVEL SECURITY;
ALTER TABLE video_watch_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE pain_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE consultation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_effectiveness ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_statistics ENABLE ROW LEVEL SECURITY;

-- 기본 정책: 사용자는 자신의 데이터만 접근 가능
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.email() = email);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.email() = email);
CREATE POLICY "Users can insert own data" ON users FOR INSERT WITH CHECK (auth.email() = email);

-- 필요에 따라 각 테이블에 대해 유사한 정책 추가...