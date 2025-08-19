@echo off
echo ========================================
echo 네이버 블로그 마케팅 자동화 플랫폼 시작
echo ========================================
echo.
echo 🚀 체험단 후기 크롤링 기반 파워블로거 대행 서비스
echo 📊 자동 콘텐츠 생성 및 이메일 마케팅 플랫폼
echo.

echo 기존 프로세스 정리 중...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo 1. 백엔드 API 서버 시작 중...
echo    - 파워블로거 데이터 관리
echo    - 체험단 후기 크롤링 API
echo    - AI 콘텐츠 자동 생성
echo    - 이메일 발송 시스템
start "네이버 블로그 마케팅 - 백엔드 API" cmd /k "cd backend && python main.py"

echo.
echo 백엔드 서버가 시작될 때까지 8초 대기...
timeout /t 8 /nobreak

echo.
echo 2. 프론트엔드 개발 서버 시작 중...
echo    - 파워블로거 탐색 및 선택
echo    - 후기 크롤링 대시보드
echo    - 콘텐츠 생성 및 관리
echo    - 블로거 컨택 자동화
start "네이버 블로그 마케팅 - 프론트엔드" cmd /k "cd marketing-integration-platform && set NODE_OPTIONS=--openssl-legacy-provider && npm start"

echo.
echo ========================================
echo 🎉 네이버 블로그 마케팅 플랫폼이 시작되었습니다!
echo ========================================
echo.
echo 📍 접속 주소:
echo   🔗 프론트엔드: http://localhost:3000
echo   🔗 백엔드 API: http://localhost:8000
echo   📖 API 문서: http://localhost:8000/docs
echo.
echo 🔧 주요 기능:
echo   ✅ 파워블로거 자동 발굴 및 데이터화
echo   ✅ 체험단 후기 크롤링 및 분석
echo   ✅ AI 기반 마케팅 콘텐츠 자동 생성
echo   ✅ 블로거 컨택 이메일 자동 발송
echo   ✅ 캠페인 성과 추적 및 관리
echo.
echo 💡 사용 방법:
echo   1. 브라우저에서 http://localhost:3000 접속
echo   2. 새 캠페인 생성
echo   3. 파워블로거 탐색 및 선택
echo   4. 체험단 후기 크롤링
echo   5. AI 콘텐츠 자동 생성
echo   6. 블로거 컨택 이메일 발송
echo.
echo ⚠️  종료하려면 각 창에서 Ctrl+C를 누르세요.
echo.

pause