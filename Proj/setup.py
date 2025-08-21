#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys


def install_requirements():
    """필요한 패키지 설치"""
    print("필요한 Python 패키지를 설치합니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 패키지 설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"✗ 패키지 설치 실패: {e}")
        return False
    return True


def check_env_file():
    """환경변수 파일 확인"""
    if not os.path.exists('.env'):
        print("\n" + "="*60)
        print("환경변수 설정이 필요합니다!")
        print("="*60)
        print("1. .env.example 파일을 복사하여 .env 파일 생성:")
        print("   cp .env.example .env")
        print("2. .env 파일을 편집하여 실제 API 키 입력")
        print("3. 자세한 설정 방법은 ENVIRONMENT_SETUP.md 참조")
        print("="*60)
        return False
    else:
        print("✓ 환경변수 파일(.env) 확인됨")
        return True

def check_credentials():
    """Google API 인증 파일 확인"""
    from config import CREDENTIALS_FILE
    
    if not os.path.exists(CREDENTIALS_FILE):
        print("\n" + "="*60)
        print("Google Sheets API 설정이 필요합니다!")
        print("="*60)
        print("1. Google Cloud Console (https://console.cloud.google.com/)에 접속")
        print("2. 새 프로젝트 생성 또는 기존 프로젝트 선택")
        print("3. Google Sheets API 활성화")
        print("4. OAuth 2.0 클라이언트 ID 생성")
        print(f"5. 인증 정보를 '{CREDENTIALS_FILE}' 파일로 다운로드")
        print("6. 이 파일을 현재 디렉토리에 저장")
        print("="*60)
        return False
    else:
        print(f"✓ Google API 인증 파일({CREDENTIALS_FILE}) 확인됨")
        return True


def main():
    print("네이버 블로그 인플루언서 정보 수집 RPA 설정")
    print("="*50)
    
    # 패키지 설치
    if not install_requirements():
        return 1
    
    # 환경변수 파일 확인
    if not check_env_file():
        return 1
    
    # 인증 파일 확인
    if not check_credentials():
        return 1
    
    print("\n" + "="*50)
    print("설정 완료!")
    print("="*50)
    print("사용법:")
    print("python main.py --keyword '검색키워드' --sheet-id 'SHEET_ID' --sheet-name '시트이름'")
    print("\n예시:")
    print("python main.py --keyword '내돈내산 영양제' --sheet-id '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms' --sheet-name 'Sheet1'")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())