#!/usr/bin/env python3
"""
백엔드 서버 실행 스크립트
"""

import uvicorn
import os

if __name__ == "__main__":
    print("🚀 백엔드 서버 시작...")
    print("📍 API 문서: http://localhost:8000/docs")
    print("📍 헬스 체크: http://localhost:8000/health")
    print("⏹️  서버 종료: Ctrl+C")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )