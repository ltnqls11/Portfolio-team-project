"""
인스타그램 크롤러
"""

import requests
from typing import List, Dict, Any, Optional
import time
import random
from datetime import datetime
import re
import json

from database.models import Platform


class InstagramCrawler:
    """인스타그램 크롤링 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_range = (2, 5)  # 요청 간 지연 시간 (초)
    
    def search_hashtag(
        self, 
        hashtag: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """해시태그로 인스타그램 계정 검색"""
        
        # 주의: 인스타그램은 공식 API 사용을 권장
        # 실제 운영 시에는 Instagram Basic Display API 또는 Instagram Graph API 사용
        
        accounts = []
        
        try:
            # 해시태그 페이지 URL
            hashtag_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            
            response = self.session.get(hashtag_url)
            response.raise_for_status()
            
            # Instagram의 JSON 데이터 추출
            json_data = self._extract_json_data(response.text)
            
            if json_data:
                posts = self._extract_posts_from_json(json_data)
                accounts = self._extract_accounts_from_posts(posts)
            
        except Exception as e:
            print(f"해시태그 검색 실패: {str(e)}")
        
        return accounts[:limit]
    
    def _extract_json_data(self, html_content: str) -> Optional[Dict]:
        """HTML에서 JSON 데이터 추출"""
        try:
            # Instagram 페이지의 JSON 데이터 패턴 찾기
            pattern = r'window\._sharedData = ({.*?});'
            match = re.search(pattern, html_content)
            
            if match:
                return json.loads(match.group(1))
        except Exception as e:
            print(f"JSON 데이터 추출 실패: {str(e)}")
        
        return None
    
    def _extract_posts_from_json(self, json_data: Dict) -> List[Dict]:
        """JSON 데이터에서 포스트 정보 추출"""
        posts = []
        
        try:
            # Instagram JSON 구조에 따라 포스트 데이터 추출
            # 실제 구조는 Instagram의 변경에 따라 달라질 수 있음
            
            hashtag_data = json_data.get('entry_data', {}).get('TagPage', [])
            if hashtag_data:
                media_data = hashtag_data[0].get('graphql', {}).get('hashtag', {}).get('edge_hashtag_to_media', {})
                edges = media_data.get('edges', [])
                
                for edge in edges:
                    node = edge.get('node', {})
                    posts.append(node)
        
        except Exception as e:
            print(f"포스트 추출 실패: {str(e)}")
        
        return posts
    
    def _extract_accounts_from_posts(self, posts: List[Dict]) -> List[Dict[str, Any]]:
        """포스트에서 계정 정보 추출"""
        accounts = []
        seen_usernames = set()
        
        for post in posts:
            try:
                owner = post.get('owner', {})
                username = owner.get('username')
                
                if username and username not in seen_usernames:
                    account_info = {
                        'platform': Platform.INSTAGRAM.value,
                        'handle': username,
                        'user_id': owner.get('id'),
                        'is_verified': owner.get('is_verified', False),
                        'profile_pic_url': owner.get('profile_pic_url'),
                        'post_count': post.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'followers': None,  # 별도 API 호출 필요
                        'following': None,  # 별도 API 호출 필요
                        'engagement_rate': self._calculate_engagement_rate(post),
                        'last_post_date': self._extract_post_date(post),
                        'category': self._guess_category_from_post(post),
                        'extracted_at': datetime.utcnow()
                    }
                    
                    accounts.append(account_info)
                    seen_usernames.add(username)
            
            except Exception as e:
                print(f"계정 정보 추출 실패: {str(e)}")
                continue
        
        return accounts
    
    def _calculate_engagement_rate(self, post: Dict) -> Optional[float]:
        """포스트 참여율 계산"""
        try:
            likes = post.get('edge_liked_by', {}).get('count', 0)
            comments = post.get('edge_media_to_comment', {}).get('count', 0)
            
            # 간단한 참여율 계산 (실제로는 팔로워 수가 필요)
            total_engagement = likes + comments
            
            # 임시로 좋아요 수 기준으로 참여율 추정
            if total_engagement > 1000:
                return 0.05  # 5%
            elif total_engagement > 500:
                return 0.03  # 3%
            elif total_engagement > 100:
                return 0.02  # 2%
            else:
                return 0.01  # 1%
        
        except Exception:
            return None
    
    def _extract_post_date(self, post: Dict) -> Optional[datetime]:
        """포스트 날짜 추출"""
        try:
            timestamp = post.get('taken_at_timestamp')
            if timestamp:
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass
        
        return None
    
    def _guess_category_from_post(self, post: Dict) -> str:
        """포스트 내용으로 카테고리 추측"""
        try:
            caption = post.get('edge_media_to_caption', {}).get('edges', [])
            if caption:
                text = caption[0].get('node', {}).get('text', '').lower()
                
                category_keywords = {
                    '뷰티': ['beauty', 'makeup', 'skincare', '뷰티', '화장품'],
                    '패션': ['fashion', 'style', 'outfit', 'ootd', '패션'],
                    '음식': ['food', 'recipe', 'cooking', '음식', '요리'],
                    '여행': ['travel', 'trip', 'vacation', '여행', '관광'],
                    '피트니스': ['fitness', 'workout', 'gym', '운동', '헬스'],
                    '라이프스타일': ['lifestyle', 'daily', 'life', '일상', '라이프']
                }
                
                for category, keywords in category_keywords.items():
                    if any(keyword in text for keyword in keywords):
                        return category
        
        except Exception:
            pass
        
        return '기타'
    
    def get_account_details(self, username: str) -> Optional[Dict[str, Any]]:
        """계정 상세 정보 조회"""
        
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            response = self.session.get(profile_url)
            response.raise_for_status()
            
            json_data = self._extract_json_data(response.text)
            
            if json_data:
                user_data = json_data.get('entry_data', {}).get('ProfilePage', [])
                if user_data:
                    user_info = user_data[0].get('graphql', {}).get('user', {})
                    
                    return {
                        'username': user_info.get('username'),
                        'full_name': user_info.get('full_name'),
                        'biography': user_info.get('biography'),
                        'followers': user_info.get('edge_followed_by', {}).get('count'),
                        'following': user_info.get('edge_follow', {}).get('count'),
                        'posts_count': user_info.get('edge_owner_to_timeline_media', {}).get('count'),
                        'is_verified': user_info.get('is_verified'),
                        'is_business': user_info.get('is_business_account'),
                        'external_url': user_info.get('external_url'),
                        'profile_pic_url': user_info.get('profile_pic_url_hd'),
                        'updated_at': datetime.utcnow()
                    }
        
        except Exception as e:
            print(f"계정 상세 정보 조회 실패: {str(e)}")
        
        return None
    
    def get_trending_hashtags(self, category: str = None) -> List[str]:
        """트렌딩 해시태그 조회"""
        
        # 실제로는 Instagram API나 서드파티 서비스 사용 권장
        trending_hashtags = [
            'instagood', 'photooftheday', 'beautiful', 'happy', 'love',
            'fashion', 'style', 'beauty', 'food', 'travel'
        ]
        
        if category:
            category_hashtags = {
                '뷰티': ['beauty', 'makeup', 'skincare', 'cosmetics'],
                '패션': ['fashion', 'style', 'ootd', 'outfit'],
                '음식': ['food', 'foodie', 'delicious', 'yummy'],
                '여행': ['travel', 'vacation', 'wanderlust', 'explore'],
                '피트니스': ['fitness', 'workout', 'gym', 'health']
            }
            
            if category in category_hashtags:
                trending_hashtags.extend(category_hashtags[category])
        
        return trending_hashtags[:15]
    
    def search_by_location(self, location: str, limit: int = 30) -> List[Dict[str, Any]]:
        """위치 기반 계정 검색"""
        
        # 위치 기반 검색 구현
        # 실제로는 Instagram Location API 사용 권장
        
        accounts = []
        
        try:
            # 위치 검색 로직 구현
            # 현재는 더미 데이터 반환
            
            for i in range(min(limit, 10)):
                accounts.append({
                    'platform': Platform.INSTAGRAM.value,
                    'handle': f'local_user_{i}',
                    'location': location,
                    'followers': random.randint(1000, 50000),
                    'category': '로컬',
                    'extracted_at': datetime.utcnow()
                })
        
        except Exception as e:
            print(f"위치 기반 검색 실패: {str(e)}")
        
        return accounts
    
    def validate_account(self, username: str) -> bool:
        """계정 유효성 검증"""
        
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            response = self.session.get(profile_url)
            
            # 404가 아니면 유효한 계정으로 간주
            return response.status_code == 200
        
        except Exception:
            return False