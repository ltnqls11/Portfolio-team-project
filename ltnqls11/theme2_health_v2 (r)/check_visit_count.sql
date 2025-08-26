-- younjc7450@gmail.com 사용자의 방문 횟수 확인
SELECT 
    email,
    personal_info->>'visit_count' as visit_count,
    personal_info->>'last_visit' as last_visit,
    created_at,
    updated_at
FROM customers
WHERE email = 'younjc7450@gmail.com';

-- 모든 사용자의 방문 횟수 확인
SELECT 
    email,
    personal_info->>'visit_count' as visit_count,
    personal_info->>'last_visit' as last_visit
FROM customers
ORDER BY personal_info->>'visit_count' DESC;