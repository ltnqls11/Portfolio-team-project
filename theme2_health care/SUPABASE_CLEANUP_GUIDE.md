# 🗑️ Supabase 스키마 정리 가이드

## ⚠️ 중요 경고
**데이터 삭제는 되돌릴 수 없습니다. 반드시 백업을 먼저 수행하세요!**

## 📋 삭제 순서

### 1단계: 데이터 백업 (필수!)
```sql
-- backup_supabase_data.sql 파일 실행
-- Supabase Dashboard > SQL Editor에서 실행
```

### 2단계: 백업 확인
```sql
-- 백업 테이블에 데이터가 있는지 확인
SELECT table_name, COUNT(*) as count 
FROM information_schema.tables 
WHERE table_name LIKE 'backup_%'
GROUP BY table_name;
```

### 3단계: 스키마 삭제
```sql
-- drop_supabase_schema.sql 파일 실행
-- Supabase Dashboard > SQL Editor에서 실행
```

## 🎯 선택적 삭제

### 특정 테이블만 삭제
```sql
-- 운동 관리 데이터만 삭제
DROP TABLE IF EXISTS exercise_management CASCADE;
DROP TABLE IF EXISTS exercise_routines CASCADE;
DROP TABLE IF EXISTS exercise_effectiveness CASCADE;

-- 통증 추적 데이터만 삭제
DROP TABLE IF EXISTS pain_tracking CASCADE;

-- 사용자 데이터만 삭제 (주의: 다른 테이블에 영향)
DROP TABLE IF EXISTS users CASCADE;
```

### 데이터만 삭제 (테이블 구조 유지)
```sql
-- 모든 데이터 삭제하지만 테이블 구조는 유지
TRUNCATE TABLE exercise_management RESTART IDENTITY CASCADE;
TRUNCATE TABLE pain_tracking RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;
```

### 특정 사용자 데이터만 삭제
```sql
-- 특정 이메일의 모든 데이터 삭제
DELETE FROM exercise_management WHERE user_email = 'user@example.com';
DELETE FROM pain_tracking WHERE user_email = 'user@example.com';
DELETE FROM user_conditions WHERE user_email = 'user@example.com';
DELETE FROM users WHERE email = 'user@example.com';
```

## 🔄 데이터 복원

### 백업에서 복원
```sql
-- 전체 복원
INSERT INTO users SELECT * FROM backup_users;
INSERT INTO exercise_management SELECT * FROM backup_exercise_management;
-- ... 나머지 테이블도 동일하게

-- 특정 사용자만 복원
INSERT INTO users 
SELECT * FROM backup_users 
WHERE email = 'user@example.com';
```

## 🛠️ 유용한 명령어

### 테이블 크기 확인
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 테이블 존재 확인
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE '%exercise%' 
     OR table_name LIKE '%user%' 
     OR table_name LIKE '%pain%';
```

### 외래 키 관계 확인
```sql
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

## 📊 삭제 영향 범위

### 완전 삭제 시 영향받는 기능
- ✅ 사용자 관리
- ✅ 증상 추적
- ✅ 운동 기록
- ✅ 통증 모니터링
- ✅ AI 상담 기록
- ✅ 알림 설정
- ✅ 통계 및 분석

### 유지되는 데이터
- ❌ customer_history (기본 유지)
- ❌ video_analysis (기본 유지)

## 🚨 문제 해결

### 삭제 실패 시
```sql
-- CASCADE 옵션 사용
DROP TABLE IF EXISTS table_name CASCADE;

-- 권한 문제 시
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
```

### 백업 복원 실패 시
```sql
-- 제약 조건 임시 비활성화
SET session_replication_role = 'replica';
-- 데이터 복원
INSERT INTO ...
-- 제약 조건 재활성화
SET session_replication_role = 'origin';
```

## 📝 체크리스트

삭제 전:
- [ ] 데이터 백업 완료
- [ ] 백업 데이터 확인
- [ ] 팀원 공지
- [ ] 서비스 중단 공지

삭제 후:
- [ ] 테이블 삭제 확인
- [ ] 애플리케이션 테스트
- [ ] 오류 로그 확인
- [ ] 필요시 복원

---

*최종 업데이트: 2024-08-24*