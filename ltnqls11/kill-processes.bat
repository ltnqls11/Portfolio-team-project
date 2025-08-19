@echo off
echo ========================================
echo 마케팅 플랫폼 프로세스 종료
echo ========================================

echo.
echo Python 프로세스 종료 중...
taskkill /f /im python.exe 2>nul
if %errorlevel% == 0 (
    echo ✅ Python 프로세스가 종료되었습니다.
) else (
    echo ℹ️  실행 중인 Python 프로세스가 없습니다.
)

echo.
echo Node.js 프로세스 종료 중...
taskkill /f /im node.exe 2>nul
if %errorlevel% == 0 (
    echo ✅ Node.js 프로세스가 종료되었습니다.
) else (
    echo ℹ️  실행 중인 Node.js 프로세스가 없습니다.
)

echo.
echo 포트 8000-8009 사용 중인 프로세스 확인...
netstat -ano | findstr :800

echo.
echo ========================================
echo 프로세스 정리가 완료되었습니다.
echo ========================================

pause