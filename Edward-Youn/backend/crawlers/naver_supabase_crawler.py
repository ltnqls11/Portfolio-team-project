"""
네이버 블로그 크롤러 with Supabase 연동
네이버 블로그 정보를 수집하여 Supabase에 저장합니다.
"""

import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, parse_qs

# Supabase 클라이언트 임포트
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.supabase_client import get_supabase_client

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NaverBlogSupabaseCrawler:
    """네이버 블로그 크롤러 (Supabase 연동)"""
    
    def __init__(self, delay_seconds: float = 2.0):
        """
        초기화
        
        Args:
            delay_seconds: 요청 간 지연 시간 (초)
        """
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Supabase 클라이언트
        self.supabase = get_supabase_client()
        
        # 카테고리 매핑
        self.category_mapping = {
            '일상': ['일상', '데일리', '일기', '브이로그'],
            '맛집': ['맛집', '음식', '요리', '레시피', '카페', '베이커리'],
            '여행': ['여행', '국내여행', '해외여행', '호텔', '펜션'],
            '패션': ['패션', '코디', '옷', '스타일', '쇼핑', 'ootd'],
            '뷰티': ['뷰티', '화장품', '메이크업', '스킨케어', '코스메틱'],
            'IT': ['IT', '테크', '가전', '전자제품', '리뷰'],
            '육아': ['육아', '임신', '출산', '아기', '키즈'],
            '인테리어': ['인테리어', '집꾸미기', '홈데코', '가구'],
            '건강': ['건강', '운동', '다이어트', '헬스', '요가'],
            '반려동물': ['반려동물', '강아지', '고양이', '펫'],
        }
    
    def search_and_save_blogs(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        max_results: int = 30
    ) -> Dict:
        """
        키워드로 블로그를 검색하고 Supabase에 저장
        
        Args:
            keyword: 검색 키워드
            category: 카테고리 (선택사항)
            max_results: 최대 결과 수
            
        Returns:
            처리 결과 통계
        """
        logger.info(f"🔍 '{keyword}' 키워드로 네이버 블로그 검색 시작...")
        
        stats = {
            'searched': 0,
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # 네이버 검색 API 대신 웹 크롤링 사용
            search_url = "https://search.naver.com/search.naver"
            
            page = 1
            while stats['searched'] < max_results and page <= 10:  # 최대 10페이지
                params = {
                    'where': 'blog',
                    'query': keyword,
                    'start': (page - 1) * 10 + 1
                }
                
                response = self.session.get(search_url, params=params)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 블로그 검색 결과 파싱
                blog_items = soup.select('li.bx')  # 검색 결과 아이템
                
                if not blog_items:
                    logger.warning(f"페이지 {page}에서 검색 결과를 찾을 수 없습니다.")
                    break
                
                for item in blog_items:
                    if stats['searched'] >= max_results:
                        break
                    
                    try:
                        blog_data = self._parse_blog_from_search(item, keyword, category)
                        if blog_data:
                            # Supabase에 저장
                            result = self._save_to_supabase(blog_data)
                            if result == 'created':
                                stats['created'] += 1
                            elif result == 'updated':
                                stats['updated'] += 1
                            else:
                                stats['failed'] += 1
                            
                            stats['searched'] += 1
                            
                    except Exception as e:
                        logger.error(f"블로그 항목 처리 오류: {e}")
                        stats['failed'] += 1
                        stats['errors'].append(str(e))
                        continue
                
                page += 1
                time.sleep(self.delay_seconds)  # 요청 간 지연
                
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            stats['errors'].append(str(e))
        
        logger.info(f"✅ 검색 완료: 검색 {stats['searched']}, 생성 {stats['created']}, 업데이트 {stats['updated']}, 실패 {stats['failed']}")
        return stats
    
    def _parse_blog_from_search(self, item, keyword: str, category: Optional[str]) -> Optional[Dict]:
        """
        검색 결과에서 블로그 정보 파싱
        
        Args:
            item: BeautifulSoup 요소
            keyword: 검색 키워드
            category: 카테고리
            
        Returns:
            블로그 정보 딕셔너리
        """
        try:
            # 블로그 링크 추출
            link_elem = item.select_one('a.title_link')
            if not link_elem:
                link_elem = item.select_one('a.api_txt_lines')
            
            if not link_elem:
                return None
            
            blog_url = link_elem.get('href', '')
            
            # 네이버 블로그 URL이 아니면 스킵
            if 'blog.naver.com' not in blog_url:
                return None
            
            # 블로그 이름 추출
            blog_name_elem = item.select_one('.name')
            if not blog_name_elem:
                blog_name_elem = item.select_one('.sub_txt.sub_name')
            
            blog_name = blog_name_elem.get_text(strip=True) if blog_name_elem else '알 수 없음'
            
            # 포스트 제목
            title_elem = item.select_one('.title_link') or item.select_one('.api_txt_lines')
            post_title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 날짜 추출
            date_elem = item.select_one('.sub_time')
            post_date = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                post_date = self._parse_date(date_text)
            
            # 카테고리 자동 판별 (제공되지 않은 경우)
            if not category:
                category = self._detect_category(post_title + ' ' + blog_name)
            
            # 블로그 ID 추출
            blog_id = self._extract_blog_id(blog_url)
            
            # 블로그 상세 정보 수집 (추가 요청)
            detail_info = self._get_blog_detail(blog_id) if blog_id else {}
            
            return {
                'blog_name': blog_name,
                'category': category or '기타',
                'post_count': detail_info.get('post_count', 0),
                'price': None,  # 초기에는 단가 정보 없음
                'blog_url': blog_url,
                'platform': 'naver',
                'last_post_date': post_date,
                'metadata': {
                    'blog_id': blog_id,
                    'search_keyword': keyword,
                    'last_post_title': post_title,
                    **detail_info
                },
                'notes': f"키워드: {keyword}"
            }
            
        except Exception as e:
            logger.error(f"블로그 파싱 오류: {e}")
            return None
    
    def _extract_blog_id(self, blog_url: str) -> Optional[str]:
        """블로그 URL에서 ID 추출"""
        try:
            # 패턴 1: https://blog.naver.com/blog_id
            if 'blog.naver.com/' in blog_url and '?' not in blog_url:
                parts = blog_url.split('/')
                for i, part in enumerate(parts):
                    if part == 'blog.naver.com' and i + 1 < len(parts):
                        return parts[i + 1]
            
            # 패턴 2: blogId 파라미터
            if 'blogId=' in blog_url:
                parsed = urlparse(blog_url)
                params = parse_qs(parsed.query)
                return params.get('blogId', [None])[0]
            
            # 패턴 3: PostView 형식
            if 'PostView' in blog_url:
                parsed = urlparse(blog_url)
                params = parse_qs(parsed.query)
                return params.get('blogId', [None])[0]
            
            return None
            
        except Exception as e:
            logger.error(f"블로그 ID 추출 오류: {e}")
            return None
    
    def _get_blog_detail(self, blog_id: str) -> Dict:
        """
        블로그 상세 정보 수집
        
        Args:
            blog_id: 블로그 ID
            
        Returns:
            상세 정보 딕셔너리
        """
        detail_info = {}
        
        try:
            # 블로그 메인 페이지 접속
            blog_main_url = f"https://blog.naver.com/{blog_id}"
            response = self.session.get(blog_main_url)
            
            if response.status_code == 200:
                # iframe 내용 추출을 위한 추가 요청
                frame_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}"
                frame_response = self.session.get(frame_url)
                
                if frame_response.status_code == 200:
                    soup = BeautifulSoup(frame_response.text, 'html.parser')
                    
                    # 전체 게시글 수 추출
                    count_elem = soup.select_one('.blog-info span.num')
                    if count_elem:
                        count_text = count_elem.get_text(strip=True)
                        # 숫자만 추출
                        count_match = re.search(r'\d+', count_text.replace(',', ''))
                        if count_match:
                            detail_info['post_count'] = int(count_match.group())
                    
                    # 블로그 설명 추출
                    desc_elem = soup.select_one('.blog-info .blog-desc')
                    if desc_elem:
                        detail_info['description'] = desc_elem.get_text(strip=True)
                    
            time.sleep(self.delay_seconds)  # 요청 간 지연
            
        except Exception as e:
            logger.warning(f"블로그 상세 정보 수집 실패: {e}")
        
        return detail_info
    
    def _detect_category(self, text: str) -> Optional[str]:
        """
        텍스트에서 카테고리 자동 감지
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감지된 카테고리
        """
        text_lower = text.lower()
        
        for category, keywords in self.category_mapping.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return category
        
        return None
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """
        날짜 텍스트를 ISO 형식으로 변환
        
        Args:
            date_text: 날짜 텍스트
            
        Returns:
            ISO 형식 날짜 문자열
        """
        try:
            # "2024.01.20." 형식
            if '.' in date_text:
                date_text = date_text.replace('.', '-').rstrip('-')
                if len(date_text.split('-')) == 3:
                    return datetime.strptime(date_text, '%Y-%m-%d').isoformat()
            
            # "1일 전", "2시간 전" 등의 상대 시간
            if '일 전' in date_text:
                days = int(re.search(r'\d+', date_text).group())
                return (datetime.now() - timedelta(days=days)).isoformat()
            elif '시간 전' in date_text:
                hours = int(re.search(r'\d+', date_text).group())
                return (datetime.now() - timedelta(hours=hours)).isoformat()
            elif '분 전' in date_text:
                minutes = int(re.search(r'\d+', date_text).group())
                return (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            return None
            
        except Exception as e:
            logger.warning(f"날짜 파싱 실패: {date_text} - {e}")
            return None
    
    def _save_to_supabase(self, blog_data: Dict) -> str:
        """
        블로그 데이터를 Supabase에 저장
        
        Args:
            blog_data: 블로그 정보
            
        Returns:
            'created', 'updated', 또는 'failed'
        """
        try:
            # Upsert (있으면 업데이트, 없으면 생성)
            result = self.supabase.upsert_blog(blog_data)
            
            if result:
                # ID가 있는지 확인하여 생성/업데이트 판단
                if 'id' in result:
                    # 기존 데이터가 있었는지 확인
                    existing = self.supabase.get_blog(blog_url=blog_data['blog_url'])
                    if existing and existing.get('created_at'):
                        # created_at이 이미 있으면 업데이트
                        return 'updated'
                    else:
                        return 'created'
                return 'created'
            
            return 'failed'
            
        except Exception as e:
            logger.error(f"Supabase 저장 오류: {e}")
            return 'failed'
    
    def get_saved_blogs(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        저장된 블로그 목록 조회
        
        Args:
            category: 카테고리 필터
            limit: 조회 개수
            
        Returns:
            블로그 목록
        """
        return self.supabase.get_blogs(category=category, limit=limit)
    
    def get_statistics(self) -> Dict:
        """
        전체 통계 조회
        
        Returns:
            통계 정보
        """
        return self.supabase.get_statistics()


# 사용 예시 및 테스트
if __name__ == "__main__":
    # 크롤러 인스턴스 생성
    crawler = NaverBlogSupabaseCrawler(delay_seconds=2)
    
    # 테스트 1: 키워드로 블로그 검색 및 저장
    print("=" * 50)
    print("네이버 블로그 크롤링 및 Supabase 저장 테스트")
    print("=" * 50)
    
    # 검색할 키워드와 카테고리
    test_keywords = [
        {'keyword': '맛집 추천', 'category': '맛집'},
        {'keyword': '스킨케어 루틴', 'category': '뷰티'},
        {'keyword': '여행 코스', 'category': '여행'}
    ]
    
    for test in test_keywords[:1]:  # 테스트용으로 1개만 실행
        print(f"\n📌 '{test['keyword']}' 검색 중...")
        stats = crawler.search_and_save_blogs(
            keyword=test['keyword'],
            category=test['category'],
            max_results=10  # 테스트용으로 10개만
        )
        
        print(f"   - 검색: {stats['searched']}개")
        print(f"   - 생성: {stats['created']}개")
        print(f"   - 업데이트: {stats['updated']}개")
        print(f"   - 실패: {stats['failed']}개")
        
        if stats['errors']:
            print(f"   - 오류: {stats['errors'][:3]}")  # 처음 3개만 표시
    
    # 테스트 2: 저장된 블로그 조회
    print("\n📋 저장된 블로그 목록:")
    saved_blogs = crawler.get_saved_blogs(limit=5)
    for blog in saved_blogs:
        print(f"   - {blog.get('blog_name')} ({blog.get('category')}): {blog.get('post_count')}개 포스트")
    
    # 테스트 3: 통계 조회
    print("\n📊 전체 통계:")
    stats = crawler.get_statistics()
    print(f"   - 전체 블로그: {stats.get('total_blogs')}개")
    print(f"   - 활성 블로그: {stats.get('active_blogs')}개")
    print(f"   - 카테고리별: {stats.get('categories')}")
