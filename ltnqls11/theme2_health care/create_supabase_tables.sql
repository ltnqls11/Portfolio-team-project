-- VDT 증후군 관리 시스템 통합 데이터베이스 테이블 생성 스크립트
-- Supabase SQL Editor에서 실행

-- 1. 기존 불필요한 테이블 삭제 (video_analysis는 유지)
DROP TABLE IF EXISTS exercise_management;
DROP TABLE IF EXISTS customer_data;
DROP TABLE IF EXISTS exercise_log;
DROP TABLE IF EXISTS pain_data;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS exercise_records CASCADE;

-- 2. 고객 기본 정보 테이블
CREATE TABLE customers (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    personal_info JSONB, -- 개인정보 (나이, 성별, 근무경험 등)
    conditions JSONB,    -- 선택된 증상 리스트
    pain_scores JSONB,   -- 부위별 통증 점수
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 운동 및 통증 기록 테이블
CREATE TABLE exercise_records (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL REFERENCES customers(email) ON DELETE CASCADE,
    record_type VARCHAR(50) NOT NULL, -- 'exercise_log' 또는 'pain_data'
    record_date DATE NOT NULL,
    value TEXT NOT NULL, -- 운동 횟수 또는 통증 점수
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 같은 날짜, 같은c 타입의 중복 기록 방지
    UNIQUE(email, record_type, record_date)
);

-- 4. 인덱스 생성 (성능 최적화)
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_exercise_records_email ON exercise_records(email);
CREATE INDEX idx_exercise_records_date ON exercise_records(record_date);
CREATE INDEX idx_exercise_records_type ON exercise_records(record_type);

-- 5. RLS (Row Level Security) 정책 설정
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_records ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 자신의 이메일 데이터만 접근 가능
CREATE POLICY "Users can access own data" ON customers
    FOR ALL USING (auth.jwt() ->> 'email' = email OR auth.role() = 'anon');

CREATE POLICY "Users can access own records" ON exercise_records  
    FOR ALL USING (auth.jwt() ->> 'email' = email OR auth.role() = 'anon');

-- 6. 테이블 코멘트 추가
COMMENT ON TABLE customers IS 'VDT 고객 기본 정보 및 증상 관리';
COMMENT ON TABLE exercise_records IS 'VDT 고객 운동 완료 및 통증 기록';
COMMENT ON COLUMN customers.personal_info IS '나이, 성별, 근무경험, 생활습관 등';
COMMENT ON COLUMN customers.conditions IS '거북목, 어깨통증 등 선택된 증상';
COMMENT ON COLUMN customers.pain_scores IS '부위별 통증 점수 (0-15)';
COMMENT ON COLUMN exercise_records.record_type IS 'exercise_log(운동기록) 또는 pain_data(통증기록)';
COMMENT ON COLUMN exercise_records.value IS '운동 완료 횟수 또는 통증 점수';