#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네이버 블로그 인플루언서 정보 수집 RPA 사용 예시
"""

import subprocess
import sys


def run_example():
    """예시 실행"""
    
    # 예시 매개변수
    keyword = "내돈내산 영양제"
    sheet_id = "YOUR_GOOGLE_SHEETS_ID_HERE"  # 실제 Google Sheets ID로 변경 필요
    sheet_name = "Sheet1"
    
    print("네이버 블로그 인플루언서 정보 수집 RPA 예시 실행")
    print("=" * 60)
    print(f"검색 키워드: {keyword}")
    print(f"Google Sheets ID: {sheet_id}")
    print(f"시트 이름: {sheet_name}")
    print("=" * 60)
    
    if sheet_id == "YOUR_GOOGLE_SHEETS_ID_HERE":
        print("⚠️  경고: Google Sheets ID를 실제 값으로 변경해주세요!")
        print("Google Sheets URL에서 ID를 복사하여 sheet_id 변수에 입력하세요.")
        print("예시: https://docs.google.com/spreadsheets/d/[여기가_SHEET_ID]/edit")
        return
    
    # 메인 스크립트 실행
    cmd = [
        sys.executable, 
        "main.py",
        "--keyword", keyword,
        "--sheet-id", sheet_id,
        "--sheet-name", sheet_name
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"실행 중 오류 발생: {e}")
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")


if __name__ == "__main__":
    run_example()