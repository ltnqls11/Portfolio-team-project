"""
네이버 블로그 크롤링 API 엔드포인트
Supabase와 연동된 크롤링 기능을 제공합니다.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, status
from typing import Optional, Dict, List
from datetime import datetime
import logging

# 크롤러 임포트
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawlers.naver_supabase_crawler import NaverBlogSupabaseCrawler

router = APIRouter()
logger = logging.getLogger(__name__)

# 크롤러 인스턴스 (싱글톤)
crawler = NaverBlogSupabaseCrawler(delay_seconds=2)


@router.post("/search")
async def search_naver_blogs(
    keyword: str = Query(..., description="검색 키워드"),
    category: Optional[str] = Query(None, description="카테고리 (맛집, 뷰티, 여행 등)"),
    max_results: int = Query(30, ge=1, le=100, description="최대 검색 결과 수"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    네이버 블로그 검색 및 Supabase 저장
    
    - 키워드로 네이버 블로그를 검색합니다
    - 검색된 블로그 정보를 Supabase에 저장합니다
    - 백그라운드로 실행되어 즉시 응답을 반환합니다
    """
    
    # 백그라운드 태스크로 크롤링 실행
    background_tasks.add_task(
        _crawl_blogs_task,
        keyword=keyword,
        category=category,
        max_results=max_results
    )
    
    return {
        "status": "started",
        "message": f"'{keyword}' 키워드로 네이버 블로그 검색을 시작했습니다.",
        "keyword": keyword,
        "category": category,
        "max_results": max_results,
        "estimated_time": f"{max_results * 0.5}초"
    }


async def _crawl_blogs_task(keyword: str, category: Optional[str], max_results: int):
    """백그라운드 크롤링 작업"""
    try:
        logger.info(f"크롤링 작업 시작: {keyword}")
        stats = crawler.search_and_save_blogs(
            keyword=keyword,
            category=category,
            max_results=max_results
        )
        logger.info(f"크롤링 완료: {stats}")
        
    except Exception as e:
        logger.error(f"크롤링 오류: {e}")


@router.get("/blogs")
async def get_blogs(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=500, description="조회 개수"),
    offset: int = Query(0, ge=0, description="시작 위치")
):
    """
    저장된 블로그 목록 조회
    
    Supabase에 저장된 블로그 목록을 조회합니다.
    """
    try:
        blogs = crawler.supabase.get_blogs(
            category=category,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "total": len(blogs),
            "category": category,
            "blogs": blogs
        }
        
    except Exception as e:
        logger.error(f"블로그 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/blogs/{blog_id}")
async def get_blog_detail(blog_id: int):
    """
    특정 블로그 상세 정보 조회
    """
    try:
        blog = crawler.supabase.get_blog(blog_id=blog_id)
        
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"블로그 ID {blog_id}를 찾을 수 없습니다."
            )
        
        return {
            "status": "success",
            "blog": blog
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"블로그 상세 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/blogs/{blog_id}")
async def update_blog(
    blog_id: int,
    update_data: Dict
):
    """
    블로그 정보 업데이트
    
    단가(price) 등의 정보를 업데이트할 수 있습니다.
    """
    try:
        # 허용된 필드만 업데이트
        allowed_fields = ['price', 'category', 'notes', 'active']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
        
        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="업데이트할 필드가 없습니다."
            )
        
        result = crawler.supabase.update_blog(
            blog_id=blog_id,
            update_data=filtered_data
        )
        
        return {
            "status": "success",
            "message": "블로그 정보가 업데이트되었습니다.",
            "blog": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"블로그 업데이트 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: int):
    """
    블로그 삭제 (비활성화)
    """
    try:
        success = crawler.supabase.delete_blog(blog_id=blog_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"블로그 ID {blog_id}를 찾을 수 없습니다."
            )
        
        return {
            "status": "success",
            "message": f"블로그 ID {blog_id}가 비활성화되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"블로그 삭제 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/statistics")
async def get_statistics():
    """
    전체 통계 조회
    """
    try:
        stats = crawler.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/search-history")
async def get_search_history():
    """
    최근 검색 기록 조회
    """
    # TODO: 검색 기록을 별도 테이블에 저장하여 관리
    return {
        "status": "success",
        "message": "검색 기록 기능은 준비 중입니다.",
        "history": []
    }


@router.get("/categories")
async def get_categories():
    """
    사용 가능한 카테고리 목록
    """
    categories = [
        {"id": "일상", "name": "일상", "keywords": ["일상", "데일리", "일기"]},
        {"id": "맛집", "name": "맛집", "keywords": ["맛집", "음식", "카페"]},
        {"id": "여행", "name": "여행", "keywords": ["여행", "국내여행", "해외여행"]},
        {"id": "패션", "name": "패션", "keywords": ["패션", "코디", "스타일"]},
        {"id": "뷰티", "name": "뷰티", "keywords": ["뷰티", "화장품", "스킨케어"]},
        {"id": "IT", "name": "IT/테크", "keywords": ["IT", "테크", "가전"]},
        {"id": "육아", "name": "육아", "keywords": ["육아", "임신", "출산"]},
        {"id": "인테리어", "name": "인테리어", "keywords": ["인테리어", "집꾸미기"]},
        {"id": "건강", "name": "건강", "keywords": ["건강", "운동", "다이어트"]},
        {"id": "반려동물", "name": "반려동물", "keywords": ["반려동물", "강아지", "고양이"]},
    ]
    
    return {
        "status": "success",
        "categories": categories
    }


@router.post("/blogs/search")
async def search_saved_blogs(
    search_term: str = Query(..., description="검색어"),
    limit: int = Query(50, ge=1, le=200, description="최대 결과 수")
):
    """
    저장된 블로그 내에서 검색
    
    블로그명, 카테고리, 메모에서 검색합니다.
    """
    try:
        results = crawler.supabase.search_blogs(
            search_term=search_term,
            limit=limit
        )
        
        return {
            "status": "success",
            "search_term": search_term,
            "total": len(results),
            "blogs": results
        }
        
    except Exception as e:
        logger.error(f"블로그 검색 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/blogs/bulk-update-price")
async def bulk_update_price(
    category: str = Query(..., description="카테고리"),
    price: float = Query(..., ge=0, description="단가")
):
    """
    카테고리별 일괄 단가 업데이트
    """
    try:
        # 해당 카테고리의 모든 블로그 조회
        blogs = crawler.supabase.get_blogs(category=category, limit=1000)
        
        updated_count = 0
        for blog in blogs:
            if blog.get('price') != price:
                crawler.supabase.update_blog(
                    blog_id=blog['id'],
                    update_data={'price': price}
                )
                updated_count += 1
        
        return {
            "status": "success",
            "message": f"{category} 카테고리의 {updated_count}개 블로그 단가가 업데이트되었습니다.",
            "category": category,
            "price": price,
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"일괄 단가 업데이트 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
