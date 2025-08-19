"""
네이버 블로그 크롤러
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import random
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse

from database.models import Platform


class NaverBlogCrawler:
    """네이버 블로그 크롤링 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://search.naver.com/search.naver"
        self.delay_range = (1, 3)  # 요청 간 지연 시간 (초)
    
    def search_blogs(
        self, 
        keyword: str, 
        category: str = None,
        page_count: int = 5
    ) -> List[Dict[str, Any]]:
        """키워드로 블로그 검색"""
        
        blogs = []
        
        for page in range(1, page_count + 1):
            try:
                page_blogs = self._search_single_page(keyword, page, category)
                blogs.extend(page_blogs)
                
                # 요청 간 지연
                time.sleep(random.uniform(*self.delay_range))
                
            except Exception as e:
                print(f"페이지 {page} 크롤링 실패: {str(e)}")
                continue
        
        return blogs
    
    def _search_single_page(
        self, 
        keyword: str, 
        page: int,
        category: str = None
    ) -> List[Dict[str, Any]]:
        """단일 페이지 검색"""
        
        params = {
            'where': 'post',
            'query': keyword,
            'start': (page - 1) * 10 + 1,
            'display': 10
        }
        
        if category:
            params['nso'] = f'so:r,p:all,a:all,c:{category}'
        
        response = self.session.get(self.base_url, params=params)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        blog_items = soup.find_all('div', class_='detail_box')
        
        blogs = []
        for item in blog_items:
            try:
                blog_data = self._extract_blog_info(item)
                if blog_data:
                    blogs.append(blog_data)
            except Exception as e:
                print(f"블로그 정보 추출 실패: {str(e)}")
                continue
        
        return blogs
    
    def _extract_blog_info(self, item) -> Optional[Dict[str, Any]]:
        """블로그 정보 추출"""
        
        try:
            # 제목과 링크
            title_elem = item.find('a', class_='title')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            blog_url = title_elem.get('href')
            
            # 블로거 정보
            blogger_elem = item.find('a', class_='name')
            blogger_name = blogger_elem.get_text(strip=True) if blogger_elem else "Unknown"
            blogger_url = blogger_elem.get('href') if blogger_elem else ""
            
            # 요약 내용
            summary_elem = item.find('div', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ""
            
            # 날짜
            date_elem = item.find('span', class_='date')
            post_date = self._parse_date(date_elem.get_text(strip=True)) if date_elem else None
            
            # 블로그 ID 추출
            blog_id = self._extract_blog_id(blogger_url)
            
            return {
                'platform': Platform.NAVER_BLOG.value,
                'handle': blog_id,
                'blogger_name': blogger_name,
                'blog_url': blogger_url,
                'post_title': title,
                'post_url': blog_url,
                'summary': summary,
                'post_date': post_date,
                'category': self._guess_category(title, summary),
                'extracted_at': datetime.utcnow()
            }
            
        except Exception as e:
            print(f"블로그 정보 추출 중 오류: {str(e)}")
            return None
    
    def _extract_blog_id(self, blogger_url: str) -> str:
        """블로거 URL에서 블로그 ID 추출"""
        if not blogger_url:
            return "unknown"
        
        # 네이버 블로그 URL 패턴 매칭
        patterns = [
            r'blog\.naver\.com/([^/]+)',
            r'blog\.naver\.com/PostList\.naver\?blogId=([^&]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, blogger_url)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """날짜 문자열 파싱"""
        try:
            # "2024.01.15" 형태
            if '.' in date_str:
                return datetime.strptime(date_str, "%Y.%m.%d")
            
            # "1일 전", "2주 전" 등의 상대적 날짜
            if '일 전' in date_str:
                days = int(re.search(r'(\d+)일 전', date_str).group(1))
                return datetime.utcnow() - timedelta(days=days)
            
            if '주 전' in date_str:
                weeks = int(re.search(r'(\d+)주 전', date_str).group(1))
                return datetime.utcnow() - timedelta(weeks=weeks)
            
            if '개월 전' in date_str:
                months = int(re.search(r'(\d+)개월 전', date_str).group(1))
                return datetime.utcnow() - timedelta(days=months*30)
            
        except Exception:
            pass
        
        return None
    
    def _guess_category(self, title: str, summary: str) -> str:
        """제목과 요약으로 카테고리 추측"""
        
        text = (title + " " + summary).lower()
        
        category_keywords = {
            '뷰티': ['화장품', '스킨케어', '메이크업', '뷰티', '코스메틱'],
            '패션': ['옷', '패션', '스타일', '코디', '의류'],
            '음식': ['맛집', '요리', '레시피', '음식', '카페'],
            '여행': ['여행', '관광', '호텔', '펜션', '맛집'],
            '육아': ['육아', '아이', '아기', '유아', '임신'],
            '건강': ['건강', '운동', '다이어트', '헬스', '의료'],
            'IT': ['컴퓨터', '스마트폰', '앱', '프로그램', '기술'],
            '생활': ['생활', '일상', '팁', '정보', '리뷰']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return '기타'
    
    def get_blog_details(self, blog_url: str) -> Optional[Dict[str, Any]]:
        """블로그 상세 정보 조회"""
        
        try:
            response = self.session.get(blog_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 팔로워 수, 방문자 수 등 추가 정보 추출
            # (네이버 블로그 구조에 따라 셀렉터 조정 필요)
            
            return {
                'detailed_info': 'extracted',
                'followers': self._extract_followers(soup),
                'total_posts': self._extract_post_count(soup),
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            print(f"블로그 상세 정보 추출 실패: {str(e)}")
            return None
    
    def _extract_followers(self, soup: BeautifulSoup) -> Optional[int]:
        """팔로워 수 추출"""
        # 네이버 블로그의 팔로워 정보 추출 로직
        # 실제 구현 시 네이버 블로그 HTML 구조 분석 필요
        return None
    
    def _extract_post_count(self, soup: BeautifulSoup) -> Optional[int]:
        """총 포스트 수 추출"""
        # 네이버 블로그의 포스트 수 정보 추출 로직
        # 실제 구현 시 네이버 블로그 HTML 구조 분석 필요
        return None
    
    def get_trending_keywords(self, category: str = None) -> List[str]:
        """트렌딩 키워드 조회"""
        
        # 네이버 트렌드 API 또는 인기 검색어 크롤링
        # 실제 구현 시 네이버 트렌드 데이터 활용
        
        trending_keywords = [
            '신상품', '후기', '추천', '리뷰', '체험',
            '할인', '이벤트', '특가', '한정판', '인기'
        ]
        
        if category:
            category_keywords = {
                '뷰티': ['스킨케어', '메이크업', '화장품', '뷰티템'],
                '패션': ['OOTD', '코디', '스타일링', '트렌드'],
                '음식': ['맛집', '레시피', '요리', '디저트'],
                '여행': ['여행지', '호텔', '맛집', '관광']
            }
            
            if category in category_keywords:
                trending_keywords.extend(category_keywords[category])
        
        return trending_keywords[:10]