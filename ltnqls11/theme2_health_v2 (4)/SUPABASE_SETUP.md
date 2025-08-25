# 🗄️ Supabase 데이터베이스 설정 가이드

## 📋 개요
VDT 증후군 관리 시스템을 위한 포괄적인 Supabase 데이터베이스 스키마입니다.

## 🎯 주요 테이블 구조

### 1. **users** - 사용자 기본 정보
- 이메일, 이름, 나이, 성별, 근무 경력 등 기본 정보 저장

### 2. **user_conditions** - 사용자 증상 관리
- 거북목, 목디스크, 손목터널증후군 등 각 증상별 관리
- 통증 점수 및 상태 추적

### 3. **work_environment** - 작업 환경 평가
- 모니터 거리, 의자 편안함, 조명 등 환경 평가 데이터
- 환경 점수 계산 및 저장

### 4. **exercise_survey** - 개인 운동 설문
- 운동 빈도, 선호 시간, 가능한 요일 등
- 개인 맞춤 운동 계획 수립용 데이터

### 5. **exercise_management** - 운동 관리 기록
- 일일 운동 완료 기록
- 통증 데이터 기록
- 기존 시스템과 호환

### 6. **exercise_routines** - 운동 루틴 추천
- AI가 추천한 운동 루틴
- 완료율 및 피드백 저장

### 7. **video_watch_history** - YouTube 영상 시청 기록
- 시청한 운동 영상 기록
- 효과성 평가 및 완료율

### 8. **pain_tracking** - 상세 통증 추적
- 아침, 오후, 저녁별 통증 레벨
- 통증 유발 요인 및 완화 방법

### 9. **notification_settings** - 알림 설정
- 이메일/Slack 알림 설정
- 휴식 간격 및 근무 시간 설정

### 10. **consultation_history** - AI 상담 기록
- 사용자와 AI 전문의 대화 기록
- 만족도 평가 및 후속 조치

### 11. **exercise_effectiveness** - 운동 효과 분석
- 주간/월간 통증 개선율
- 가장 효과적인 운동 분석

### 12. **usage_statistics** - 시스템 사용 통계
- 기능별 사용 횟수
- 사용 패턴 분석

## 🚀 설치 방법

### 1단계: Supabase 프로젝트 접속
1. [Supabase Dashboard](https://app.supabase.com)에 로그인
2. 프로젝트 선택
3. SQL Editor 열기

### 2단계: 스키마 실행
1. `supabase_schema.sql` 파일의 내용을 복사
2. SQL Editor에 붙여넣기
3. "Run" 버튼 클릭

### 3단계: 권한 설정 (선택사항)
```sql
-- 익명 사용자에게 읽기/쓰기 권한 부여 (개발용)
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon;
```

### 4단계: 환경 변수 설정
`.env` 파일에 다음 정보 추가:
```env
SUPABASE_URL=your-project-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

## 📊 주요 뷰 (View)

### user_comprehensive_view
사용자의 모든 정보를 한 번에 조회할 수 있는 종합 뷰

### weekly_progress_view
주간 운동 및 통증 추세를 확인할 수 있는 뷰

## 🔧 유용한 쿼리

### 사용자 통증 개선율 확인
```sql
SELECT * FROM calculate_pain_improvement('user@email.com');
```

### 최근 7일간 운동 기록 조회
```sql
SELECT * FROM exercise_management 
WHERE user_email = 'user@email.com' 
  AND date >= CURRENT_DATE - INTERVAL '7 days'
  AND data_type = 'exercise_log'
ORDER BY date DESC;
```

### 현재 활성 증상 조회
```sql
SELECT * FROM user_conditions 
WHERE user_email = 'user@email.com' 
  AND status = 'active';
```

## 🔐 보안 설정

### RLS (Row Level Security)
- 모든 테이블에 RLS 활성화
- 사용자는 자신의 데이터만 접근 가능
- 관리자는 모든 데이터 접근 가능

### 인증 연동
Supabase Auth와 연동하여 사용:
```javascript
const { data, error } = await supabase
  .from('users')
  .select('*')
  .eq('email', user.email)
```

## 📈 모니터링

### 대시보드 쿼리
```sql
-- 일일 활성 사용자
SELECT COUNT(DISTINCT user_email) as daily_active_users
FROM exercise_management
WHERE date = CURRENT_DATE;

-- 평균 통증 개선율
SELECT AVG(pain_improvement_percentage) as avg_improvement
FROM exercise_effectiveness
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';

-- 가장 인기 있는 운동 영상
SELECT video_title, COUNT(*) as watch_count
FROM video_watch_history
GROUP BY video_title
ORDER BY watch_count DESC
LIMIT 10;
```

## 🆘 문제 해결

### 테이블이 이미 존재하는 경우
```sql
-- 기존 테이블 삭제 (주의: 데이터 손실)
DROP TABLE IF EXISTS table_name CASCADE;
```

### 권한 오류 발생 시
```sql
-- 권한 재설정
GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;
```

## 📝 마이그레이션

### 기존 데이터 이전
```sql
-- customer_history 데이터를 새 구조로 이전
INSERT INTO users (email, created_at)
SELECT DISTINCT email, MIN(created_at) 
FROM customer_history
GROUP BY email
ON CONFLICT (email) DO NOTHING;

-- 증상 데이터 이전
INSERT INTO user_conditions (user_email, condition_name, pain_score)
SELECT 
  email,
  jsonb_array_elements_text(conditions::jsonb) as condition_name,
  (pain_scores::jsonb->>jsonb_array_elements_text(conditions::jsonb))::integer as pain_score
FROM customer_history;
```

## 📞 지원

문제가 발생하거나 도움이 필요한 경우:
- Supabase 공식 문서: https://supabase.com/docs
- 프로젝트 이슈 트래커: GitHub Issues

---

*최종 업데이트: 2024-08-24*