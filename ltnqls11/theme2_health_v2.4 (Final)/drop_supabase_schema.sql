-- ⚠️ 주의: 이 스크립트는 모든 VDT 관리 시스템 테이블과 데이터를 삭제합니다!
-- 실행 전 반드시 백업을 수행하세요.

-- Supabase Dashboard의 SQL Editor에서 실행하세요

-- ========================================
-- 1. 뷰(Views) 삭제
-- ========================================
DROP VIEW IF EXISTS user_comprehensive_view CASCADE;
DROP VIEW IF EXISTS weekly_progress_view CASCADE;

-- ========================================
-- 2. 함수(Functions) 삭제
-- ========================================
DROP FUNCTION IF EXISTS calculate_pain_improvement(VARCHAR) CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ========================================
-- 3. 트리거(Triggers) 삭제 (테이블 삭제 전에 실행)
-- ========================================
-- 트리거는 테이블과 함께 자동 삭제되지만, 명시적으로 삭제
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_user_conditions_updated_at ON user_conditions;
DROP TRIGGER IF EXISTS update_exercise_survey_updated_at ON exercise_survey;
DROP TRIGGER IF EXISTS update_notification_settings_updated_at ON notification_settings;

-- ========================================
-- 4. 정책(Policies) 삭제
-- ========================================
-- Users 테이블 정책
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;

-- Exercise Management 테이블 정책
DROP POLICY IF EXISTS "Users can view own exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can insert exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can update own exercise data" ON exercise_management;
DROP POLICY IF EXISTS "Users can delete own exercise data" ON exercise_management;

-- ========================================
-- 5. 인덱스(Indexes) 삭제 (테이블과 함께 자동 삭제되지만 명시적으로)
-- ========================================
DROP INDEX IF EXISTS idx_users_email;
DROP INDEX IF EXISTS idx_user_conditions_email;
DROP INDEX IF EXISTS idx_exercise_management_user_date;
DROP INDEX IF EXISTS idx_exercise_management_data_type;
DROP INDEX IF EXISTS idx_exercise_management_created;
DROP INDEX IF EXISTS idx_pain_tracking_user_date;
DROP INDEX IF EXISTS idx_video_history_user;
DROP INDEX IF EXISTS idx_routines_user_date;
DROP INDEX IF EXISTS idx_consultation_user;

-- ========================================
-- 6. 테이블(Tables) 삭제 - 종속성 순서대로
-- ========================================

-- 종속 테이블부터 삭제
DROP TABLE IF EXISTS usage_statistics CASCADE;
DROP TABLE IF EXISTS exercise_effectiveness CASCADE;
DROP TABLE IF EXISTS consultation_history CASCADE;
DROP TABLE IF EXISTS notification_settings CASCADE;
DROP TABLE IF EXISTS pain_tracking CASCADE;
DROP TABLE IF EXISTS video_watch_history CASCADE;
DROP TABLE IF EXISTS exercise_routines CASCADE;
DROP TABLE IF EXISTS exercise_management CASCADE;
DROP TABLE IF EXISTS exercise_survey CASCADE;
DROP TABLE IF EXISTS work_environment CASCADE;
DROP TABLE IF EXISTS user_conditions CASCADE;

-- 마지막으로 기본 테이블 삭제
DROP TABLE IF EXISTS users CASCADE;

-- ========================================
-- 7. 시퀀스(Sequences) 정리 (있는 경우)
-- ========================================
-- UUID를 사용하므로 대부분 시퀀스가 없지만, 혹시 있다면 삭제
DROP SEQUENCE IF EXISTS exercise_management_id_seq CASCADE;

-- ========================================
-- 삭제 확인
-- ========================================
-- 남은 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'users',
    'user_conditions',
    'work_environment',
    'exercise_survey',
    'exercise_management',
    'exercise_routines',
    'video_watch_history',
    'pain_tracking',
    'notification_settings',
    'consultation_history',
    'exercise_effectiveness',
    'usage_statistics'
  );

-- 결과가 비어있으면 모든 테이블이 성공적으로 삭제됨

-- ========================================
-- 선택적: customer_history 테이블 유지/삭제
-- ========================================
-- customer_history는 기존 시스템 테이블이므로 기본적으로 유지
-- 삭제하려면 아래 주석을 해제하세요:
-- DROP TABLE IF EXISTS customer_history CASCADE;

-- ========================================
-- 선택적: video_analysis 테이블 유지/삭제
-- ========================================
-- video_analysis는 YouTube 영상 분석 테이블이므로 기본적으로 유지
-- 삭제하려면 아래 주석을 해제하세요:
-- DROP TABLE IF EXISTS video_analysis CASCADE;

-- ========================================
-- 완료 메시지
-- ========================================
-- 이 쿼리가 실행되면 삭제 완료
SELECT 'VDT 관리 시스템 스키마가 성공적으로 삭제되었습니다.' AS message;