#!/usr/bin/env python3
"""
백엔드 서버 간단 실행 스크립트
"""

import os
import sys
import subprocess

def main():
    # 현재 디렉토리를 Python 경로에 추가
    current_dir = os.getcwd()
    backend_dir = os.path.join(current_dir, 'backend')
    
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    # 백엔드 디렉토리로 이동
    os.chdir(backend_dir)
    
    print("🚀 백엔드 서버 시작...")
    print("📍 API 문서: http://localhost:8000/docs")
    print("📍 헬스 체크: http://localhost:8000/health")
    print("⏹️  서버 종료: Ctrl+C")
    print("-" * 50)
    
    try:
        # uvicorn으로 서버 실행
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()