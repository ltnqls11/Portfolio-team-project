"""
네이버 블로그 크롤러 테스트 스크립트
Supabase 연동 및 API 엔드포인트 테스트
"""

import asyncio
import requests
import json
from datetime import datetime
import time

# API 서버 URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """API 헬스 체크"""
    print("\n1. API 헬스 체크")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"상태 코드: {response.status_code}")
    print(f"응답: {response.json()}")
    
    assert response.status_code == 200
    print("✅ 헬스 체크 성공")


def test_get_categories():
    """카테고리 목록 조회"""
    print("\n2. 카테고리 목록 조회")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/api/naver-blogs/categories")
    print(f"상태 코드: {response.status_code}")
    
    data = response.json()
    categories = data.get('categories', [])
    
    print(f"카테고리 수: {len(categories)}")
    for cat in categories[:3]:
        print(f"  - {cat['name']}: {', '.join(cat['keywords'][:3])}")
    
    assert response.status_code == 200
    assert len(categories) > 0
    print("✅ 카테고리 조회 성공")


def test_search_blogs(keyword="맛집", category="맛집", max_results=5):
    """블로그 검색 및 저장"""
    print(f"\n3. 블로그 검색: '{keyword}'")
    print("-" * 50)
    
    params = {
        "keyword": keyword,
        "category": category,
        "max_results": max_results
    }
    
    response = requests.post(
        f"{BASE_URL}/api/naver-blogs/search",
        params=params
    )
    
    print(f"상태 코드: {response.status_code}")
    data = response.json()
    print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    assert data['status'] == 'started'
    print("✅ 검색 시작 성공")
    
    # 크롤링 완료 대기
    print(f"크롤링 중... (약 {max_results * 0.5}초 대기)")
    time.sleep(max_results * 0.5 + 2)
    
    return True


def test_get_blogs(category=None, limit=10):
    """저장된 블로그 목록 조회"""
    print(f"\n4. 저장된 블로그 목록 조회")
    print("-" * 50)
    
    params = {
        "limit": limit
    }
    if category:
        params["category"] = category
    
    response = requests.get(
        f"{BASE_URL}/api/naver-blogs/blogs",
        params=params
    )
    
    print(f"상태 코드: {response.status_code}")
    data = response.json()
    
    if data['status'] == 'success':
        blogs = data.get('blogs', [])
        print(f"조회된 블로그 수: {len(blogs)}")
        
        for blog in blogs[:3]:
            print(f"\n📝 블로그 정보:")
            print(f"  - 이름: {blog.get('blog_name')}")
            print(f"  - 카테고리: {blog.get('category')}")
            print(f"  - 포스트 수: {blog.get('post_count')}")
            print(f"  - URL: {blog.get('blog_url')}")
            print(f"  - 단가: {blog.get('price') or '미설정'}")
    
    assert response.status_code == 200
    print("✅ 블로그 목록 조회 성공")
    
    return data.get('blogs', [])


def test_update_blog_price(blog_id, price=50000):
    """블로그 단가 업데이트"""
    print(f"\n5. 블로그 단가 업데이트 (ID: {blog_id})")
    print("-" * 50)
    
    update_data = {
        "price": price
    }
    
    response = requests.patch(
        f"{BASE_URL}/api/naver-blogs/blogs/{blog_id}",
        json=update_data
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"✅ 단가 업데이트 성공: {price}원")
    else:
        print(f"❌ 업데이트 실패: {response.text}")
    
    return response.status_code == 200


def test_get_statistics():
    """통계 조회"""
    print(f"\n6. 전체 통계 조회")
    print("-" * 50)
    
    response = requests.get(f"{BASE_URL}/api/naver-blogs/statistics")
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('statistics', {})
        
        print(f"📊 통계:")
        print(f"  - 전체 블로그: {stats.get('total_blogs')}개")
        print(f"  - 활성 블로그: {stats.get('active_blogs')}개")
        print(f"  - 비활성 블로그: {stats.get('inactive_blogs')}개")
        
        categories = stats.get('categories', {})
        if categories:
            print(f"  - 카테고리별:")
            for cat, count in categories.items():
                print(f"    • {cat}: {count}개")
    
    assert response.status_code == 200
    print("✅ 통계 조회 성공")


def test_search_saved_blogs(search_term="스킨케어"):
    """저장된 블로그 내 검색"""
    print(f"\n7. 저장된 블로그 검색: '{search_term}'")
    print("-" * 50)
    
    params = {
        "search_term": search_term,
        "limit": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/api/naver-blogs/blogs/search",
        params=params
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('blogs', [])
        
        print(f"검색 결과: {len(results)}개")
        for blog in results[:3]:
            print(f"  - {blog.get('blog_name')} ({blog.get('category')})")
    
    assert response.status_code == 200
    print("✅ 블로그 검색 성공")


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("네이버 블로그 크롤러 API 테스트")
    print("=" * 60)
    
    try:
        # 1. API 헬스 체크
        test_api_health()
        
        # 2. 카테고리 조회
        test_get_categories()
        
        # 3. 블로그 검색 및 저장
        test_search_blogs("맛집 추천", "맛집", 5)
        
        # 4. 저장된 블로그 조회
        blogs = test_get_blogs(limit=5)
        
        # 5. 블로그 단가 업데이트 (블로그가 있을 경우)
        if blogs and len(blogs) > 0:
            first_blog_id = blogs[0].get('id')
            if first_blog_id:
                test_update_blog_price(first_blog_id, 30000)
        
        # 6. 통계 조회
        test_get_statistics()
        
        # 7. 블로그 검색
        test_search_saved_blogs("맛집")
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 성공!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ API 서버에 연결할 수 없습니다.")
        print("   서버가 실행 중인지 확인하세요: python backend/main.py")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")


if __name__ == "__main__":
    # 테스트 실행
    run_all_tests()
    
    # 추가 테스트 (선택적)
    print("\n" + "=" * 60)
    print("추가 테스트 실행 (선택적)")
    print("=" * 60)
    
    # 다른 카테고리 테스트
    print("\n다른 카테고리 검색 테스트:")
    test_search_blogs("스킨케어 루틴", "뷰티", 3)
    test_search_blogs("여행 코스", "여행", 3)
