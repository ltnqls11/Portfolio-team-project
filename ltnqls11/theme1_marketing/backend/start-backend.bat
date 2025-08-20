@echo off
echo ========================================
echo 마케팅 플랫폼 백엔드 API 서버 시작
echo ========================================

echo.
echo Python 버전 확인...
python --version

echo.
echo 필요한 패키지 설치 확인...
pip install -r requirements.txt

echo.
echo 기존 프로세스 종료 중...
taskkill /f /im python.exe 2>nul

echo.
echo FastAPI 서버 시작 중...
echo 서버가 자동으로 사용 가능한 포트를 찾습니다 (8000-8009)
echo.

python main.py

pause