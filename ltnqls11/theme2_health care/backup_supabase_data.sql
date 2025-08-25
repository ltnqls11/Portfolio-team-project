-- 📦 VDT 관리 시스템 데이터 백업 스크립트
-- 삭제 전에 먼저 이 스크립트로 데이터를 백업하세요

-- ========================================
-- 1. 백업 테이블 생성 (임시)
-- ========================================

-- Users 백업
CREATE TABLE IF NOT EXISTS backup_users AS 
SELECT * FROM users 
WHERE EXISTS (SELECT 1 FROM users LIMIT 1);

-- User Conditions 백업
CREATE TABLE IF NOT EXISTS backup_user_conditions AS 
SELECT * FROM user_conditions 
WHERE EXISTS (SELECT 1 FROM user_conditions LIMIT 1);

-- Work Environment 백업
CREATE TABLE IF NOT EXISTS backup_work_environment AS 
SELECT * FROM work_environment 
WHERE EXISTS (SELECT 1 FROM work_environment LIMIT 1);

-- Exercise Survey 백업
CREATE TABLE IF NOT EXISTS backup_exercise_survey AS 
SELECT * FROM exercise_survey 
WHERE EXISTS (SELECT 1 FROM exercise_survey LIMIT 1);

-- Exercise Management 백업 (중요!)
CREATE TABLE IF NOT EXISTS backup_exercise_management AS 
SELECT * FROM exercise_management 
WHERE EXISTS (SELECT 1 FROM exercise_management LIMIT 1);

-- Exercise Routines 백업
CREATE TABLE IF NOT EXISTS backup_exercise_routines AS 
SELECT * FROM exercise_routines 
WHERE EXISTS (SELECT 1 FROM exercise_routines LIMIT 1);

-- Video Watch History 백업
CREATE TABLE IF NOT EXISTS backup_video_watch_history AS 
SELECT * FROM video_watch_history 
WHERE EXISTS (SELECT 1 FROM video_watch_history LIMIT 1);

-- Pain Tracking 백업
CREATE TABLE IF NOT EXISTS backup_pain_tracking AS 
SELECT * FROM pain_tracking 
WHERE EXISTS (SELECT 1 FROM pain_tracking LIMIT 1);

-- Notification Settings 백업
CREATE TABLE IF NOT EXISTS backup_notification_settings AS 
SELECT * FROM notification_settings 
WHERE EXISTS (SELECT 1 FROM notification_settings LIMIT 1);

-- Consultation History 백업
CREATE TABLE IF NOT EXISTS backup_consultation_history AS 
SELECT * FROM consultation_history 
WHERE EXISTS (SELECT 1 FROM consultation_history LIMIT 1);

-- Exercise Effectiveness 백업
CREATE TABLE IF NOT EXISTS backup_exercise_effectiveness AS 
SELECT * FROM exercise_effectiveness 
WHERE EXISTS (SELECT 1 FROM exercise_effectiveness LIMIT 1);

-- Usage Statistics 백업
CREATE TABLE IF NOT EXISTS backup_usage_statistics AS 
SELECT * FROM usage_statistics 
WHERE EXISTS (SELECT 1 FROM usage_statistics LIMIT 1);

-- ========================================
-- 2. 백업 확인
-- ========================================
SELECT 
    'backup_users' as table_name, 
    COUNT(*) as row_count 
FROM backup_users
UNION ALL
SELECT 
    'backup_user_conditions', 
    COUNT(*) 
FROM backup_user_conditions
UNION ALL
SELECT 
    'backup_exercise_management', 
    COUNT(*) 
FROM backup_exercise_management
UNION ALL
SELECT 
    'backup_pain_tracking', 
    COUNT(*) 
FROM backup_pain_tracking
ORDER BY table_name;

-- ========================================
-- 3. 백업 데이터 JSON 내보내기 (선택적)
-- ========================================
-- Supabase Dashboard에서 각 백업 테이블을 CSV/JSON으로 내보낼 수 있습니다

-- ========================================
-- 4. 백업 테이블 삭제 (데이터 복원 후)
-- ========================================
-- 백업이 더 이상 필요없을 때 실행:
/*
DROP TABLE IF EXISTS backup_users CASCADE;
DROP TABLE IF EXISTS backup_user_conditions CASCADE;
DROP TABLE IF EXISTS backup_work_environment CASCADE;
DROP TABLE IF EXISTS backup_exercise_survey CASCADE;
DROP TABLE IF EXISTS backup_exercise_management CASCADE;
DROP TABLE IF EXISTS backup_exercise_routines CASCADE;
DROP TABLE IF EXISTS backup_video_watch_history CASCADE;
DROP TABLE IF EXISTS backup_pain_tracking CASCADE;
DROP TABLE IF EXISTS backup_notification_settings CASCADE;
DROP TABLE IF EXISTS backup_consultation_history CASCADE;
DROP TABLE IF EXISTS backup_exercise_effectiveness CASCADE;
DROP TABLE IF EXISTS backup_usage_statistics CASCADE;
*/

-- ========================================
-- 5. 데이터 복원 명령어 (필요시)
-- ========================================
/*
-- Users 복원
INSERT INTO users SELECT * FROM backup_users;

-- User Conditions 복원
INSERT INTO user_conditions SELECT * FROM backup_user_conditions;

-- Exercise Management 복원
INSERT INTO exercise_management SELECT * FROM backup_exercise_management;

-- 나머지 테이블도 동일한 방식으로 복원
*/

SELECT '백업이 완료되었습니다. 백업 테이블을 확인하세요.' AS message;