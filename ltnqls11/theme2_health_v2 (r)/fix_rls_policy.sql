-- 🔧 Supabase RLS 정책 수정 스크립트
-- Row Level Security 오류 해결

-- ========================================
-- 1. 기존 정책 삭제
-- ========================================
DROP POLICY IF EXISTS "Users can view own exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can insert exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can update own exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can delete own exercise data" ON exercise_management;

-- ========================================
-- 2. RLS 비활성화 (개발 환경용)
-- ========================================
ALTER TABLE exercise_management DISABLE ROW LEVEL SECURITY;

-- 또는 모든 권한 허용 정책 생성 (선택적)
-- ALTER TABLE exercise_management ENABLE ROW LEVEL SECURITY;

-- ========================================
-- 3. 새로운 허용 정책 생성 (개발 환경용)
-- ========================================
-- 모든 사용자가 모든 데이터에 접근 가능하도록 설정

CREATE POLICY "Allow all access to exercise_management" ON exercise_management
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ========================================
-- 4. 익명 사용자 권한 부여
-- ========================================
-- 익명 사용자(anon)와 인증된 사용자(authenticated)에게 모든 권한 부여
GRANT ALL ON exercise_management TO anon;
GRANT ALL ON exercise_management TO authenticated;

-- 시퀀스 권한 부여 (UUID 사용 시 필요없지만 안전하게)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ========================================
-- 5. 테이블 소유자 권한 확인
-- ========================================
-- 현재 사용자에게 테이블 소유권 부여
ALTER TABLE exercise_management OWNER TO postgres;

-- ========================================
-- 6. 정책 확인
-- ========================================
-- 적용된 정책 확인
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'exercise_management';

-- ========================================
-- 7. 테이블 권한 확인
-- ========================================
SELECT 
    table_name,
    privilege_type,
    grantee
FROM information_schema.role_table_grants 
WHERE table_name = 'exercise_management';

-- ========================================
-- 8. 테스트 쿼리
-- ========================================
-- 데이터 삽입 테스트
INSERT INTO exercise_management (
    data_type, 
    user_email, 
    date, 
    value, 
    details
) VALUES (
    'test',
    'test@example.com',
    CURRENT_DATE,
    '1',
    '{"test": true}'
);

-- 테스트 데이터 확인
SELECT * FROM exercise_management WHERE data_type = 'test';

-- 테스트 데이터 삭제
DELETE FROM exercise_management WHERE data_type = 'test';

-- ========================================
-- 완료 메시지
-- ========================================
SELECT 'RLS 정책이 수정되었습니다. 이제 데이터 삽입이 가능합니다.' AS message;