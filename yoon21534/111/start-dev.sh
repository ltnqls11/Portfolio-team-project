#!/bin/bash

echo "Starting Marketing Automation RPA Development Environment..."

# Backend 서버 시작
echo "[1/3] Starting Backend Server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

sleep 3

# n8n 서버 시작
echo "[2/3] Starting n8n Server..."
cd n8n
npm start &
N8N_PID=$!
cd ..

sleep 3

# Frontend 서버 시작
echo "[3/3] Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "All servers are running:"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "n8n: http://localhost:5678"
echo ""
echo "Press Ctrl+C to stop all servers"

# 종료 시그널 처리
trap 'kill $BACKEND_PID $N8N_PID $FRONTEND_PID; exit' INT

# 모든 프로세스가 종료될 때까지 대기
wait