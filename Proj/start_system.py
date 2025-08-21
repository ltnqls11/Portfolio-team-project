#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
전체 RPA 시스템 통합 실행 스크립트
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def start_api_server():
    """Flask API 서버 시작"""
    print("🚀 API 서버 시작 중...")
    try:
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n📡 API 서버 종료됨")
    except Exception as e:
        print(f"❌ API 서버 오류: {e}")

def start_react_app():
    """React 앱 시작"""
    print("⚛️  React 앱 시작 중...")
    react_dir = Path("react-control-panel")
    
    if not react_dir.exists():
        print("❌ React 앱 디렉토리가 없습니다.")
        return
    
    try:
        # npm install 먼저 실행
        print("📦 npm 패키지 설치 중...")
        subprocess.run(["npm", "install"], cwd=react_dir, check=True)
        
        # React 앱 시작
        subprocess.run(["npm", "start"], cwd=react_dir, check=True)
    except KeyboardInterrupt:
        print("\n⚛️  React 앱 종료됨")
    except Exception as e:
        print(f"❌ React 앱 오류: {e}")

def check_requirements():
    """필요한 요구사항 확인"""
    print("🔍 시스템 요구사항 확인 중...")
    
    # Python 패키지 확인
    try:
        import flask
        import selenium
        import google.auth
        print("✅ Python 패키지 확인 완료")
    except ImportError as e:
        print(f"❌ 필요한 Python 패키지가 없습니다: {e}")
        print("💡 'python setup.py' 또는 'pip install -r requirements.txt'를 실행하세요.")
        return False
    
    # Google API 인증 파일 확인
    if not os.path.exists('credentials.json'):
        print("❌ Google API 인증 파일(credentials.json)이 없습니다.")
        print("💡 Google Cloud Console에서 인증 파일을 다운로드하여 추가하세요.")
        return False
    
    print("✅ Google API 인증 파일 확인 완료")
    
    # Node.js 확인
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("✅ Node.js 및 npm 확인 완료")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 또는 npm이 설치되지 않았습니다.")
        print("💡 https://nodejs.org 에서 Node.js를 설치하세요.")
        return False
    
    return True

def show_instructions():
    """사용 안내 출력"""
    print("\n" + "="*60)
    print("🎯 블로거 마케팅 RPA 시스템 사용 안내")
    print("="*60)
    print("1. API 서버: http://localhost:5000")
    print("2. React 제어판: http://localhost:3000")
    print("3. n8n (별도 설치 필요): http://localhost:5678")
    print()
    print("📋 사용 순서:")
    print("1️⃣  React 제어판에서 기본 설정 입력")
    print("2️⃣  '블로거 정보 수집 시작' 버튼 클릭")
    print("3️⃣  n8n에서 워크플로우 설정 완료 후")
    print("4️⃣  '이메일 발송 시작' 버튼 클릭")
    print("5️⃣  '카페 포스팅 시작' 버튼 클릭")
    print()
    print("🔧 n8n 설정:")
    print("- email-workflow.json 파일을 n8n에 import")
    print("- cafe-post-workflow.json 파일을 n8n에 import")
    print("- Google Sheets, Gmail, Naver API 인증 설정")
    print("="*60)

def main():
    """메인 실행 함수"""
    print("🤖 블로거 마케팅 RPA 시스템 시작")
    print("="*50)
    
    # 요구사항 확인
    if not check_requirements():
        print("\n❌ 시스템 요구사항을 만족하지 않습니다.")
        print("💡 setup.py를 먼저 실행하여 환경을 설정하세요.")
        return 1
    
    print("\n✅ 모든 요구사항 확인 완료!")
    
    # 사용 안내 출력
    show_instructions()
    
    print("\n🚀 시스템 구성 요소 시작 중...")
    
    try:
        # API 서버와 React 앱을 별도 스레드에서 실행
        api_thread = threading.Thread(target=start_api_server, daemon=True)
        react_thread = threading.Thread(target=start_react_app, daemon=True)
        
        api_thread.start()
        time.sleep(2)  # API 서버가 먼저 시작되도록 대기
        react_thread.start()
        
        print("\n✅ 시스템이 성공적으로 시작되었습니다!")
        print("🌐 React 제어판: http://localhost:3000")
        print("📡 API 서버: http://localhost:5000")
        print("\n⏹️  종료하려면 Ctrl+C를 누르세요.")
        
        # 메인 스레드에서 대기
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 시스템 종료 중...")
        print("👋 블로거 마케팅 RPA 시스템이 종료되었습니다.")
        return 0
    except Exception as e:
        print(f"\n❌ 시스템 실행 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())