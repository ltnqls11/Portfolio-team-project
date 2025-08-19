@echo off
echo Starting Marketing Automation RPA Development Environment...

echo.
echo [1/3] Starting Backend Server...
start "Backend" cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak > nul

echo [2/3] Starting n8n Server...
start "n8n" cmd /k "cd n8n && npm start"

timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo n8n: http://localhost:5678
echo.
pause