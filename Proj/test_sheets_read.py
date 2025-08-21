#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Sheets 읽기 기능 테스트 스크립트
n8n 워크플로우에서 사용할 데이터 형태를 확인할 수 있습니다.
"""

import json
import argparse
from google_sheets_client import GoogleSheetsClient


def test_read_functionality():
    """Google Sheets 읽기 기능 테스트"""
    parser = argparse.ArgumentParser(description='Google Sheets 읽기 테스트')
    parser.add_argument('--sheet-id', required=True, help='Google Sheets 문서 ID')
    parser.add_argument('--sheet-name', required=True, help='시트 이름')
    
    args = parser.parse_args()
    
    try:
        print("Google Sheets 읽기 기능 테스트")
        print("=" * 50)
        
        # Google Sheets 클라이언트 초기화
        sheets_client = GoogleSheetsClient()
        
        # 1. 모든 데이터 읽기
        print("1. 모든 데이터 읽기:")
        all_data = sheets_client.read_all_data(args.sheet_id, args.sheet_name)
        print(f"총 {len(all_data)}행 읽음")
        
        if all_data:
            print("첫 3행 미리보기:")
            for i, row in enumerate(all_data[:3]):
                print(f"  행 {i+1}: {row}")
        
        print()
        
        # 2. 블로거 데이터 구조화 (n8n용)
        print("2. n8n 워크플로우용 블로거 데이터:")
        blogger_data = sheets_client.get_blogger_data(args.sheet_id, args.sheet_name)
        
        print(f"이메일이 있는 블로거: {len(blogger_data)}명")
        
        if blogger_data:
            print("\n첫 번째 블로거 정보:")
            print(json.dumps(blogger_data[0], ensure_ascii=False, indent=2))
            
            print(f"\n전체 블로거 목록 (JSON 형태):")
            print(json.dumps(blogger_data, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 50)
        print("테스트 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    test_read_functionality()