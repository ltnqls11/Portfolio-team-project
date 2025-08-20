@echo off
echo ========================================
echo 마케팅 플랫폼 시작 스크립트
echo ========================================

echo.
echo 1. 프론트엔드 의존성 설치 중...
cd marketing-integration-platform
call npm install

echo.
echo 2. 환경 변수 파일 확인...
if not exist .env (
    echo .env 파일이 없습니다. .env.example을 복사하여 .env 파일을 생성하세요.
    copy .env.example .env
    echo .env 파일이 생성되었습니다. 필요한 설정을 수정해주세요.
)

echo.
echo 3. 프론트엔드 개발 서버 시작...
echo 브라우저에서 http://localhost:3000 으로 접속하세요.
echo.
echo 주의: Node.js 버전 호환성 문제가 있을 수 있습니다.
echo 오류 발생 시 다음 명령어를 시도해보세요:
echo set NODE_OPTIONS=--openssl-legacy-provider
echo.

set NODE_OPTIONS=--openssl-legacy-provider
npm start

pause