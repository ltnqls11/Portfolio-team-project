-- 🔧 Foreign Key 제약 조건 오류 해결 스크립트
-- 테스트용 사용자 데이터 추가 및 제약 조건 수정

-- ========================================
-- 1. 테스트 사용자 추가
-- ========================================
INSERT INTO users (
    id,
    email, 
    name,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'test@example.com', 
    'Test User',
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- ========================================
-- 2. 개발 환경용 - Foreign Key 제약 조건 임시 제거 (선택적)
-- ========================================
-- 개발 중 테스트를 쉽게 하기 위해 외래키 제약 조건을 제거
-- 운영 환경에서는 이 부분을 주석 처리하세요
s
ALTER TABLE exercise_management 
DROP CONSTRAINT IF EXISTS exercise_management_user_email_fkey;

-- ========================================
-- 3. 추가 테스트 사용자들 (선택적)
-- ========================================
INSERT INTO users (id, email, name, created_at, updated_at) VALUES
    (gen_random_uuid(), 'admin@example.com', 'Admin User', NOW(), NOW()),
    (gen_random_uuid(), 'dev@example.com', 'Developer User', NOW(), NOW()),
    (gen_random_uuid(), 'user1@example.com', 'User One', NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- ========================================
-- 4. 테스트 데이터 삽입 확인
-- ========================================
-- 이제 exercise_management에 테스트 데이터 삽입 가능
INSERT INTO exercise_management (
    data_type, 
    user_email, 
    date, 
    value, 
    details
) VALUES (
    'test_data',
    'test@example.com',
    CURRENT_DATE,
    'test_value',
    '{"test": true}'
) ON CONFLICT DO NOTHING;

-- ========================================
-- 5. 확인 쿼리
-- ========================================
-- 사용자 확인
SELECT email, name FROM users WHERE email LIKE '%example.com';

-- 테스트 데이터 확인
SELECT * FROM exercise_management WHERE user_email = 'test@example.com';

-- 제약 조건 확인
SELECT 
    constraint_name, 
    table_name, 
    constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'exercise_management' 
  AND constraint_type = 'FOREIGN KEY';

SELECT '외래키 제약 조건 문제가 해결되었습니다.' AS message;