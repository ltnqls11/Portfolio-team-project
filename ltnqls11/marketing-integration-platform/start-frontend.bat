@echo off
echo ========================================
echo 마케팅 플랫폼 프론트엔드 시작
echo ========================================

echo.
echo 환경 변수 설정 중...
set NODE_OPTIONS=--openssl-legacy-provider

echo.
echo 개발 서버 시작 중...
echo 브라우저에서 http://localhost:3000 으로 접속하세요.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

npm start

pause