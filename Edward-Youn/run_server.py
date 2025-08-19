#!/usr/bin/env python3
"""
온라인 마케팅 연계 플랫폼 서버 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """필수 패키지 설치 확인"""
    try:
        import fastapi
        import sqlmodel
        import uvicorn
        print("✅ 필수 패키지가 설치되어 있습니다.")
        return True
    except ImportError as e:
        print(f"❌ 필수 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 설치하세요:")
        print("pip install -r backend/requirements.txt")
        return False

def check_env_file():
    """환경 변수 파일 확인"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env 파일이 없습니다.")
            create_env = input(".env.example을 복사하여 .env 파일을 생성하시겠습니까? (y/n): ")
            if create_env.lower() == 'y':
                import shutil
                shutil.copy(env_example, env_file)
                print("✅ .env 파일이 생성되었습니다.")
                print("⚠️  .env 파일의 설정값들을 확인하고 수정하세요.")
                return True
            else:
                print("❌ .env 파일이 필요합니다.")
                return False
        else:
            print("❌ .env.example 파일을 찾을 수 없습니다.")
            return False
    else:
        print("✅ .env 파일이 존재합니다.")
        return True

def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        "logs",
        "data/raw",
        "data/processed",
        "data/exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 필요한 디렉토리가 생성되었습니다.")

def run_server():
    """서버 실행"""
    print("🚀 서버를 시작합니다...")
    print("📍 API 문서: http://localhost:8000/docs")
    print("📍 ReDoc: http://localhost:8000/redoc")
    print("⏹️  서버 종료: Ctrl+C")
    print("-" * 50)
    
    try:
        # 현재 디렉토리를 Python 경로에 추가
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 서버 실행
        os.chdir("backend")
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

def main():
    """메인 함수"""
    print("=" * 60)
    print("🌟 온라인 마케팅 연계 플랫폼")
    print("=" * 60)
    
    # 1. 필수 패키지 확인
    if not check_requirements():
        return
    
    # 2. 환경 변수 파일 확인
    if not check_env_file():
        return
    
    # 3. 필요한 디렉토리 생성
    create_directories()
    
    # 4. 서버 실행
    run_server()

if __name__ == "__main__":
    main()