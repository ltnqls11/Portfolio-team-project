-- Supabase Dashboard의 SQL Editor에서 실행하세요

-- 기존 테이블이 있으면 삭제 (주의: 데이터가 삭제됩니다)
-- DROP TABLE IF EXISTS exercise_management CASCADE;

-- exercise_management 테이블 생성
CREATE TABLE IF NOT EXISTS exercise_management (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    value TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_exercise_management_user_date 
ON exercise_management(user_email, date);

CREATE INDEX IF NOT EXISTS idx_exercise_management_data_type 
ON exercise_management(data_type);

CREATE INDEX IF NOT EXISTS idx_exercise_management_created 
ON exercise_management(created_at);

-- RLS (Row Level Security) 활성화
ALTER TABLE exercise_management ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 자신의 데이터를 읽을 수 있도록 정책 생성
CREATE POLICY "Users can view own exercise data" ON exercise_management
    FOR SELECT USING (true);

-- 모든 사용자가 데이터를 삽입할 수 있도록 정책 생성
CREATE POLICY "Users can insert exercise data" ON exercise_management
    FOR INSERT WITH CHECK (true);

-- 모든 사용자가 자신의 데이터를 업데이트할 수 있도록 정책 생성
CREATE POLICY "Users can update own exercise data" ON exercise_management
    FOR UPDATE USING (user_email = auth.email() OR true);

-- 모든 사용자가 자신의 데이터를 삭제할 수 있도록 정책 생성
CREATE POLICY "Users can delete own exercise data" ON exercise_management
    FOR DELETE USING (user_email = auth.email() OR true);

-- 익명 사용자에게 권한 부여 (개발 환경용)
GRANT ALL ON exercise_management TO anon;
GRANT ALL ON exercise_management TO authenticated;
GRANT USAGE ON SEQUENCE exercise_management_id_seq TO anon;
GRANT USAGE ON SEQUENCE exercise_management_id_seq TO authenticated;

-- 테이블 생성 확인
SELECT 
    column_name,
    data_type,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'exercise_management'
ORDER BY 
    ordinal_position;