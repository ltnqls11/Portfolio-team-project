"""
API 테스트 스크립트
개발 중 API 엔드포인트를 테스트하기 위한 스크립트
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


class APITester:
    """API 테스트 클래스"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        print("🔍 헬스 체크 테스트...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"✅ 상태: {response.status_code}")
            print(f"📄 응답: {response.json()}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def test_create_client(self) -> int:
        """클라이언트 생성 테스트"""
        print("🔍 클라이언트 생성 테스트...")
        
        client_data = {
            "name": "테스트 회사",
            "industry": "뷰티",
            "contact_email": "test@example.com",
            "contact_phone": "010-1234-5678",
            "company_url": "https://test-company.com",
            "description": "테스트용 클라이언트입니다."
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/clients/",
                json=client_data
            )
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get("id")
        except Exception as e:
            print(f"❌ 오류: {e}")
            return None
        
        print("-" * 50)
    
    def test_create_campaign(self, client_id: int) -> int:
        """캠페인 생성 테스트"""
        print("🔍 캠페인 생성 테스트...")
        
        campaign_data = {
            "client_id": client_id,
            "title": "신제품 런칭 캠페인",
            "objective": "새로운 스킨케어 제품의 인지도 향상 및 구매 유도",
            "budget": 1000000.0,
            "keywords": '["스킨케어", "보습", "안티에이징", "자연성분"]',
            "reference_urls": '["https://example.com/product1", "https://example.com/product2"]',
            "channels": '["naver_blog", "instagram"]'
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/campaigns/",
                json=campaign_data
            )
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get("id")
        except Exception as e:
            print(f"❌ 오류: {e}")
            return None
        
        print("-" * 50)
    
    def test_create_creator(self) -> int:
        """크리에이터 생성 테스트"""
        print("🔍 크리에이터 생성 테스트...")
        
        creator_data = {
            "platform": "naver_blog",
            "handle": "beauty_blogger_123",
            "category": "뷰티",
            "followers": 15000,
            "engagement_rate": 0.035,
            "email": "blogger@example.com",
            "notes": "뷰티 전문 블로거, 20-30대 여성 타겟"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/creators/",
                json=creator_data
            )
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result.get("id")
        except Exception as e:
            print(f"❌ 오류: {e}")
            return None
        
        print("-" * 50)
    
    def test_generate_copy(self, campaign_id: int):
        """문구 생성 테스트"""
        print("🔍 문구 생성 테스트...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/copy/generate/{campaign_id}",
                json=["naver_blog", "instagram"]
            )
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def test_get_campaigns(self):
        """캠페인 목록 조회 테스트"""
        print("🔍 캠페인 목록 조회 테스트...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/campaigns/")
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {len(result)}개 캠페인 조회됨")
            if result:
                print(f"첫 번째 캠페인: {result[0]['title']}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def test_get_creators(self):
        """크리에이터 목록 조회 테스트"""
        print("🔍 크리에이터 목록 조회 테스트...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/creators/")
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {len(result)}개 크리에이터 조회됨")
            if result:
                print(f"첫 번째 크리에이터: {result[0]['handle']} ({result[0]['platform']})")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def test_crawling_status(self):
        """크롤링 상태 조회 테스트"""
        print("🔍 크롤링 상태 조회 테스트...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/crawling/status")
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def test_trending_data(self):
        """트렌딩 데이터 조회 테스트"""
        print("🔍 트렌딩 데이터 조회 테스트...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/crawling/trending")
            print(f"✅ 상태: {response.status_code}")
            result = response.json()
            print(f"📄 네이버 키워드: {result.get('naver_keywords', [])[:5]}")
            print(f"📄 인스타 해시태그: {result.get('instagram_hashtags', [])[:5]}")
        except Exception as e:
            print(f"❌ 오류: {e}")
        
        print("-" * 50)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 API 테스트 시작")
        print("=" * 50)
        
        # 1. 헬스 체크
        self.test_health_check()
        
        # 2. 클라이언트 생성
        client_id = self.test_create_client()
        
        if client_id:
            # 3. 캠페인 생성
            campaign_id = self.test_create_campaign(client_id)
            
            if campaign_id:
                # 4. 문구 생성
                self.test_generate_copy(campaign_id)
        
        # 5. 크리에이터 생성
        creator_id = self.test_create_creator()
        
        # 6. 목록 조회 테스트
        self.test_get_campaigns()
        self.test_get_creators()
        
        # 7. 크롤링 관련 테스트
        self.test_crawling_status()
        self.test_trending_data()
        
        print("✅ 모든 테스트 완료!")


def main():
    """메인 함수"""
    tester = APITester()
    
    print("온라인 마케팅 연계 플랫폼 API 테스트")
    print("서버가 실행 중인지 확인하세요: python backend/main.py")
    print()
    
    choice = input("전체 테스트를 실행하시겠습니까? (y/n): ").lower()
    
    if choice == 'y':
        tester.run_all_tests()
    else:
        print("개별 테스트 메뉴:")
        print("1. 헬스 체크")
        print("2. 클라이언트 생성")
        print("3. 캠페인 생성")
        print("4. 크리에이터 생성")
        print("5. 크롤링 상태")
        
        test_choice = input("테스트 번호를 선택하세요: ")
        
        if test_choice == "1":
            tester.test_health_check()
        elif test_choice == "2":
            tester.test_create_client()
        elif test_choice == "3":
            client_id = int(input("클라이언트 ID를 입력하세요: "))
            tester.test_create_campaign(client_id)
        elif test_choice == "4":
            tester.test_create_creator()
        elif test_choice == "5":
            tester.test_crawling_status()
        else:
            print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()