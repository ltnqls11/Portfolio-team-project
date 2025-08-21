#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
React 프로젝트 설치 및 실행 스크립트
react-scripts 오류 해결을 위한 전용 스크립트
"""

import subprocess
import sys
import os
from pathlib import Path

def install_frontend_dependencies():
    """프론트엔드 의존성 설치"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ frontend 디렉토리가 없습니다.")
        return False
    
    print("📦 React 프로젝트 의존성 설치 중...")
    
    try:
        # 기존 node_modules 삭제 (있다면)
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            print("🗑️ 기존 node_modules 삭제 중...")
            import shutil
            shutil.rmtree(node_modules)
        
        # package-lock.json 삭제 (있다면)
        package_lock = frontend_dir / "package-lock.json"
        if package_lock.exists():
            package_lock.unlink()
        
        # npm cache 정리
        print("🧹 npm 캐시 정리 중...")
        subprocess.run(["npm", "cache", "clean", "--force"], check=True)
        
        # npm install 실행
        print("📥 npm install 실행 중...")
        result = subprocess.run(
            ["npm", "install"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True,
            timeout=300  # 5분 타임아웃
        )
        
        if result.returncode == 0:
            print("✅ npm install 성공!")
            return True
        else:
            print(f"❌ npm install 실패:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ npm install 시간 초과 (5분)")
        return False
    except Exception as e:
        print(f"❌ 설치 중 오류: {e}")
        return False

def start_react_app():
    """React 앱 시작"""
    frontend_dir = Path("frontend")
    
    print("🚀 React 개발 서버 시작 중...")
    
    try:
        # react-scripts 존재 확인
        node_modules_bin = frontend_dir / "node_modules" / ".bin"
        react_scripts = node_modules_bin / "react-scripts"
        
        if not react_scripts.exists():
            print("❌ react-scripts를 찾을 수 없습니다.")
            print("💡 npm install을 다시 실행해보세요.")
            return False
        
        print("✅ react-scripts 확인됨")
        
        # React 앱 시작
        subprocess.run(["npm", "start"], cwd=frontend_dir, check=True)
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ React 앱이 중단되었습니다.")
        return True
    except Exception as e:
        print(f"❌ React 앱 시작 실패: {e}")
        return False

def check_node_npm():
    """Node.js와 npm 버전 확인"""
    try:
        # Node.js 버전 확인
        node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✅ Node.js: {node_result.stdout.strip()}")
            print(f"✅ npm: {npm_result.stdout.strip()}")
            return True
        else:
            print("❌ Node.js 또는 npm을 찾을 수 없습니다.")
            return False
            
    except FileNotFoundError:
        print("❌ Node.js가 설치되지 않았습니다.")
        print("💡 https://nodejs.org 에서 Node.js를 설치하세요.")
        return False

def main():
    """메인 실행 함수"""
    print("🔧 React 프로젝트 설치 및 실행")
    print("=" * 50)
    
    # Node.js와 npm 확인
    if not check_node_npm():
        return 1
    
    # 프론트엔드 의존성 설치
    if not install_frontend_dependencies():
        print("\n❌ 의존성 설치에 실패했습니다.")
        print("💡 다음을 시도해보세요:")
        print("   1. Node.js 최신 버전 설치")
        print("   2. 관리자 권한으로 실행")
        print("   3. 네트워크 연결 확인")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 설치 완료! React 앱을 시작합니다...")
    print("🌐 브라우저에서 http://localhost:3000 이 열립니다.")
    print("⏹️ 종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    # React 앱 시작
    if not start_react_app():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())