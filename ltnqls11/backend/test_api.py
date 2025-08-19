#!/usr/bin/env python3
"""
백엔드 API 테스트 스크립트
"""

import requests
import json
from datetime import datetime, timedelta

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 마케팅 플랫폼 API 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ 서버 상태: {response.status_code}")
        print(f"   응답: {response.json()}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 캠페인 목록 조회
    try:
        response = requests.get(f"{base_url}/api/campaigns")
        print(f"✅ 캠페인 목록: {response.status_code}")
        campaigns = response.json()
        print(f"   캠페인 수: {len(campaigns)}")
    except Exception as e:
        print(f"❌ 캠페인 목록 조회 실패: {e}")
    
    # 3. 크리에이터 목록 조회
    try:
        response = requests.get(f"{base_url}/api/creators")
        print(f"✅ 크리에이터 목록: {response.status_code}")
        creators = response.json()
        print(f"   크리에이터 수: {len(creators)}")
        for creator in creators:
            print(f"   - {creator['handle']} ({creator['category']})")
    except Exception as e:
        print(f"❌ 크리에이터 목록 조회 실패: {e}")
    
    # 4. 문구 생성 테스트
    try:
        test_request = {
            "productDescription": "혁신적인 스마트 워치",
            "channel": "naver_blog",
            "benefits": ["건강 관리", "편리함", "스타일"],
            "keywords": ["스마트워치", "건강", "피트니스"]
        }
        response = requests.post(f"{base_url}/api/copy/generate", json=test_request)
        print(f"✅ 문구 생성: {response.status_code}")
        result = response.json()
        print(f"   생성된 문구 수: {len(result['variants'])}")
        if result['variants']:
            print(f"   첫 번째 문구 제목: {result['variants'][0].get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ 문구 생성 실패: {e}")
    
    # 5. 대시보드 통계 조회
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats")
        print(f"✅ 대시보드 통계: {response.status_code}")
        stats = response.json()
        print(f"   활성 캠페인: {stats['activeCampaigns']}")
        print(f"   승인 대기: {stats['pendingApprovals']}")
    except Exception as e:
        print(f"❌ 대시보드 통계 조회 실패: {e}")
    
    print("=" * 50)
    print("🎉 API 테스트 완료!")

if __name__ == "__main__":
    test_api()