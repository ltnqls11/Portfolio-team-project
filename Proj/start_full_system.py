#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
완전한 백엔드/프론트엔드 분리 시스템 실행 스크립트
Flask 백엔드 + React 프론트엔드 + 모든 RPA 기능
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import webbrowser

def start_backend():
    """Flask 백엔드 서버 시작"""
    print("🚀 백엔드 서버 시작 중...")
    try:
        backend_dir = Path("backend")
        if backend_dir.exists():
            subprocess.run([sys.executable, "app.py"], cwd=backend_dir, check=True)
        else:
            print("❌ backend 디렉토리를 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n📡 백엔드 서버 종료됨")
    except Exception as e:
        print(f"❌ 백엔드 서버 오류: {e}")

def start_frontend():
    """React 프론트엔드 시작"""
    print("⚛️  프론트엔드 시작 중...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ frontend 디렉토리가 없습니다.")
        return
    
    try:
        # npm install 먼저 실행
        print("📦 npm 패키지 설치 중...")
        install_result = subprocess.run(["npm", "install"], cwd=frontend_dir, capture_output=True, text=True)
        
        if install_result.returncode != 0:
            print(f"❌ npm install 실패: {install_result.stderr}")
            return
        
        print("✅ npm 패키지 설치 완료")
        
        # React 앱 시작
        print("🚀 React 개발 서버 시작 중...")
        subprocess.run(["npm", "start"], cwd=frontend_dir, check=True)
    except KeyboardInterrupt:
        print("\n⚛️  프론트엔드 종료됨")
    except Exception as e:
        print(f"❌ 프론트엔드 오류: {e}")

def check_requirements():
    """시스템 요구사항 확인"""
    print("🔍 시스템 요구사항 확인 중...")
    
    # Python 패키지 확인
    try:
        import flask
        import flask_sqlalchemy
        import flask_cors
        print("✅ Python 백엔드 패키지 확인 완료")
    except ImportError as e:
        print(f"❌ 필요한 Python 패키지가 없습니다: {e}")
        print("💡 'pip install -r requirements.txt'를 실행하세요.")
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

def show_system_info():
    """시스템 정보 출력"""
    print("\n" + "="*80)
    print("🤖 BloggerRPA - 완전한 백엔드/프론트엔드 분리 시스템")
    print("="*80)
    print("📊 백엔드 (Flask + SQLAlchemy):")
    print("   - RESTful API 서버")
    print("   - SQLite 데이터베이스")
    print("   - 프로젝트 관리")
    print("   - 블로거 데이터 관리")
    print("   - 자동화 로그 관리")
    print()
    print("⚛️  프론트엔드 (React):")
    print("   - 현대적인 웹 인터페이스")
    print("   - 반응형 디자인")
    print("   - 실시간 데이터 업데이트")
    print("   - 프로젝트 관리 대시보드")
    print()
    print("🔗 통합 기능:")
    print("   - ①블로거 정보 수집 (Kiro 독립 실행)")
    print("   - ②이메일 자동 발송 (Gmail API)")
    print("   - ③네이버 카페 자동 포스팅 (Naver API)")
    print("   - 🚀 완전한 자동화 (모든 단계 원클릭)")
    print("   - 📊 n8n 워크플로우 연동 지원")
    print()
    print("🌐 접속 주소:")
    print("   - 프론트엔드: http://localhost:3000")
    print("   - 백엔드 API: http://localhost:5000")
    print("="*80)

def main():
    """메인 실행 함수"""
    show_system_info()
    
    # 요구사항 확인
    if not check_requirements():
        print("\n❌ 시스템 요구사항을 만족하지 않습니다.")
        print("💡 setup.py를 먼저 실행하여 환경을 설정하세요.")
        return 1
    
    print("\n✅ 모든 요구사항 확인 완료!")
    print("\n🚀 시스템 구성 요소 시작 중...")
    
    try:
        # 백엔드와 프론트엔드를 별도 스레드에서 실행
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        
        backend_thread.start()
        print("📡 백엔드 서버 시작됨 (http://localhost:5000)")
        
        time.sleep(3)  # 백엔드가 먼저 시작되도록 대기
        
        frontend_thread.start()
        print("⚛️  프론트엔드 시작됨 (http://localhost:3000)")
        
        # 잠시 후 브라우저 자동 열기
        time.sleep(5)
        try:
            webbrowser.open('http://localhost:3000')
            print("🌐 브라우저에서 애플리케이션이 열렸습니다!")
        except:
            pass
        
        print("\n✅ 시스템이 성공적으로 시작되었습니다!")
        print("🌐 프론트엔드: http://localhost:3000")
        print("📡 백엔드 API: http://localhost:5000")
        print("\n⏹️  종료하려면 Ctrl+C를 누르세요.")
        
        # 메인 스레드에서 대기
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 시스템 종료 중...")
        print("👋 BloggerRPA 시스템이 종료되었습니다.")
        return 0
    except Exception as e:
        print(f"\n❌ 시스템 실행 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())