"""
Supabase 연동 설정
블로그 데이터를 Supabase에 저장하고 관리합니다.
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# 환경 변수 로드
load_dotenv('.env.supabase')

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase 클라이언트"""
    
    def __init__(self):
        """초기화"""
        self.url = os.getenv('SUPABASE_URL', 'https://ohemvgnzikgdzjkzipvy.supabase.co')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.url or not self.service_key:
            raise ValueError("Supabase URL과 Service Key가 필요합니다.")
        
        # Service Key 사용 (더 많은 권한)
        self.client: Client = create_client(self.url, self.service_key)
        
        # 테이블 초기화
        self._init_tables()
    
    def _init_tables(self):
        """테이블 초기화 및 확인"""
        try:
            # blogs 테이블이 있는지 확인
            result = self.client.table('blogs').select('*').limit(1).execute()
            logger.info("✅ Supabase 연결 성공: blogs 테이블 확인됨")
        except Exception as e:
            logger.warning(f"blogs 테이블이 없습니다. 생성이 필요할 수 있습니다: {e}")
            # 테이블 생성 SQL (Supabase 대시보드에서 실행)
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS blogs (
                id SERIAL PRIMARY KEY,
                blog_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                post_count INTEGER DEFAULT 0,
                price DECIMAL(10, 2),
                blog_url VARCHAR(500) NOT NULL UNIQUE,
                platform VARCHAR(50) DEFAULT 'naver',
                followers INTEGER DEFAULT 0,
                engagement_rate DECIMAL(5, 2),
                last_post_date TIMESTAMP,
                crawled_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                active BOOLEAN DEFAULT TRUE,
                metadata JSONB,
                notes TEXT
            );
            
            -- 인덱스 생성
            CREATE INDEX idx_blogs_category ON blogs(category);
            CREATE INDEX idx_blogs_platform ON blogs(platform);
            CREATE INDEX idx_blogs_active ON blogs(active);
            """
            logger.info("테이블 생성 SQL:\n" + create_table_sql)
    
    # 블로그 CRUD 작업
    
    def create_blog(self, blog_data: Dict[str, Any]) -> Dict:
        """
        블로그 정보 생성
        
        Args:
            blog_data: 블로그 정보 딕셔너리
                - blog_name: 블로그명 (필수)
                - category: 카테고리
                - post_count: 포스팅 개수
                - price: 단가 (초기값 None)
                - blog_url: 블로그 링크 (필수)
                
        Returns:
            생성된 블로그 정보
        """
        try:
            # 필수 필드 검증
            if not blog_data.get('blog_name') or not blog_data.get('blog_url'):
                raise ValueError("blog_name과 blog_url은 필수입니다.")
            
            # 기본값 설정
            blog_data.setdefault('platform', 'naver')
            blog_data.setdefault('crawled_at', datetime.now().isoformat())
            blog_data.setdefault('updated_at', datetime.now().isoformat())
            blog_data.setdefault('active', True)
            
            # Supabase에 삽입
            result = self.client.table('blogs').insert(blog_data).execute()
            
            if result.data:
                logger.info(f"✅ 블로그 생성 성공: {blog_data['blog_name']}")
                return result.data[0]
            else:
                raise Exception("블로그 생성 실패")
                
        except Exception as e:
            logger.error(f"❌ 블로그 생성 오류: {e}")
            raise
    
    def get_blog(self, blog_id: int = None, blog_url: str = None) -> Optional[Dict]:
        """
        블로그 정보 조회
        
        Args:
            blog_id: 블로그 ID
            blog_url: 블로그 URL
            
        Returns:
            블로그 정보
        """
        try:
            query = self.client.table('blogs').select('*')
            
            if blog_id:
                query = query.eq('id', blog_id)
            elif blog_url:
                query = query.eq('blog_url', blog_url)
            else:
                raise ValueError("blog_id 또는 blog_url이 필요합니다.")
            
            result = query.single().execute()
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"블로그 조회 오류: {e}")
            return None
    
    def get_blogs(
        self,
        category: Optional[str] = None,
        platform: str = 'naver',
        active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        블로그 목록 조회
        
        Args:
            category: 카테고리 필터
            platform: 플랫폼 필터
            active: 활성 상태 필터
            limit: 조회 개수
            offset: 시작 위치
            
        Returns:
            블로그 목록
        """
        try:
            query = self.client.table('blogs').select('*')
            
            # 필터 적용
            if category:
                query = query.eq('category', category)
            if platform:
                query = query.eq('platform', platform)
            if active is not None:
                query = query.eq('active', active)
            
            # 정렬 및 페이징
            query = query.order('post_count', desc=True)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"블로그 목록 조회 오류: {e}")
            return []
    
    def update_blog(self, blog_id: int = None, blog_url: str = None, update_data: Dict = None) -> Dict:
        """
        블로그 정보 업데이트
        
        Args:
            blog_id: 블로그 ID
            blog_url: 블로그 URL
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 블로그 정보
        """
        try:
            if not update_data:
                raise ValueError("업데이트할 데이터가 없습니다.")
            
            # 업데이트 시간 추가
            update_data['updated_at'] = datetime.now().isoformat()
            
            query = self.client.table('blogs')
            
            if blog_id:
                query = query.update(update_data).eq('id', blog_id)
            elif blog_url:
                query = query.update(update_data).eq('blog_url', blog_url)
            else:
                raise ValueError("blog_id 또는 blog_url이 필요합니다.")
            
            result = query.execute()
            
            if result.data:
                logger.info(f"✅ 블로그 업데이트 성공")
                return result.data[0]
            else:
                raise Exception("블로그 업데이트 실패")
                
        except Exception as e:
            logger.error(f"블로그 업데이트 오류: {e}")
            raise
    
    def upsert_blog(self, blog_data: Dict[str, Any]) -> Dict:
        """
        블로그 정보 생성 또는 업데이트 (Upsert)
        blog_url을 기준으로 중복 체크
        
        Args:
            blog_data: 블로그 정보
            
        Returns:
            생성/업데이트된 블로그 정보
        """
        try:
            blog_url = blog_data.get('blog_url')
            if not blog_url:
                raise ValueError("blog_url은 필수입니다.")
            
            # 기존 블로그 확인
            existing = self.get_blog(blog_url=blog_url)
            
            if existing:
                # 업데이트
                blog_id = existing['id']
                # ID는 업데이트하지 않음
                update_data = {k: v for k, v in blog_data.items() if k != 'id'}
                return self.update_blog(blog_id=blog_id, update_data=update_data)
            else:
                # 새로 생성
                return self.create_blog(blog_data)
                
        except Exception as e:
            logger.error(f"Upsert 오류: {e}")
            raise
    
    def delete_blog(self, blog_id: int) -> bool:
        """
        블로그 삭제 (소프트 삭제)
        
        Args:
            blog_id: 블로그 ID
            
        Returns:
            성공 여부
        """
        try:
            # 소프트 삭제 (active를 false로 설정)
            result = self.client.table('blogs').update({
                'active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('id', blog_id).execute()
            
            if result.data:
                logger.info(f"✅ 블로그 삭제(비활성화) 성공: ID {blog_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"블로그 삭제 오류: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        전체 통계 조회
        
        Returns:
            통계 정보
        """
        try:
            # 전체 블로그 수
            total_result = self.client.table('blogs').select('count', count='exact').execute()
            total_count = total_result.count if total_result else 0
            
            # 활성 블로그 수
            active_result = self.client.table('blogs').select('count', count='exact').eq('active', True).execute()
            active_count = active_result.count if active_result else 0
            
            # 카테고리별 통계
            all_blogs = self.get_blogs(limit=1000)
            category_stats = {}
            
            for blog in all_blogs:
                category = blog.get('category', '미분류')
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1
            
            return {
                'total_blogs': total_count,
                'active_blogs': active_count,
                'inactive_blogs': total_count - active_count,
                'categories': category_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            return {}
    
    def search_blogs(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        블로그 검색
        
        Args:
            search_term: 검색어
            limit: 최대 결과 수
            
        Returns:
            검색 결과
        """
        try:
            # blog_name 또는 notes에서 검색
            result = self.client.table('blogs').select('*').or_(
                f"blog_name.ilike.%{search_term}%,"
                f"category.ilike.%{search_term}%,"
                f"notes.ilike.%{search_term}%"
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"블로그 검색 오류: {e}")
            return []


# 싱글톤 인스턴스
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Supabase 클라이언트 싱글톤 인스턴스 반환"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


# 테스트 코드
if __name__ == "__main__":
    # Supabase 연결 테스트
    client = get_supabase_client()
    
    # 테스트 블로그 데이터
    test_blog = {
        'blog_name': '테스트 블로그',
        'category': '일상',
        'post_count': 150,
        'price': None,  # 초기에는 단가 모름
        'blog_url': 'https://blog.naver.com/testblog123',
        'platform': 'naver'
    }
    
    # 블로그 생성 테스트
    print("📝 블로그 생성 테스트...")
    # created = client.upsert_blog(test_blog)
    # print(f"생성된 블로그: {created}")
    
    # 블로그 목록 조회 테스트
    print("\n📋 블로그 목록 조회...")
    blogs = client.get_blogs(limit=5)
    print(f"조회된 블로그 수: {len(blogs)}")
    for blog in blogs:
        print(f"  - {blog.get('blog_name')}: {blog.get('category')}")
    
    # 통계 조회
    print("\n📊 통계 조회...")
    stats = client.get_statistics()
    print(f"전체 블로그: {stats.get('total_blogs')}")
    print(f"활성 블로그: {stats.get('active_blogs')}")
    print(f"카테고리별: {stats.get('categories')}")
