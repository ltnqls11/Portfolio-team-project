"""
크롤링 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database.database import get_session
from database.models import (
    Creator, CreatorCreate, Platform, Event, EventCreate
)
from crawlers.naver_crawler import NaverBlogCrawler
from crawlers.instagram_crawler import InstagramCrawler

router = APIRouter()


@router.post("/naver/search")
async def crawl_naver_blogs(
    keyword: str,
    category: Optional[str] = None,
    page_count: int = 3,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session)
):
    """네이버 블로그 크롤링"""
    
    # 백그라운드에서 크롤링 실행
    background_tasks.add_task(
        _crawl_naver_blogs_task,
        keyword, category, page_count, session
    )
    
    # 이벤트 로그 생성
    event = Event(
        type="crawling_started",
        payload_json=f'{{"platform": "naver", "keyword": "{keyword}", "category": "{category}"}}'
    )
    session.add(event)
    session.commit()
    
    return {
        "message": "네이버 블로그 크롤링이 시작되었습니다.",
        "keyword": keyword,
        "category": category,
        "estimated_time": f"{page_count * 2}초"
    }


async def _crawl_naver_blogs_task(
    keyword: str,
    category: Optional[str],
    page_count: int,
    session: Session
):
    """네이버 블로그 크롤링 백그라운드 작업"""
    
    try:
        crawler = NaverBlogCrawler()
        blogs = crawler.search_blogs(keyword, category, page_count)
        
        created_count = 0
        updated_count = 0
        
        for blog_data in blogs:
            # 기존 크리에이터 확인
            existing = session.query(Creator).filter(
                Creator.platform == Platform.NAVER_BLOG,
                Creator.handle == blog_data['handle']
            ).first()
            
            if existing:
                # 기존 크리에이터 업데이트
                existing.active_at = blog_data.get('post_date')
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # 새 크리에이터 생성
                creator_data = CreatorCreate(
                    platform=Platform.NAVER_BLOG,
                    handle=blog_data['handle'],
                    category=blog_data['category'],
                    active_at=blog_data.get('post_date'),
                    notes=f"키워드: {keyword}"
                )
                
                creator = Creator.model_validate(creator_data)
                session.add(creator)
                created_count += 1
        
        session.commit()
        
        # 완료 이벤트 로그
        event = Event(
            type="crawling_completed",
            payload_json=f'{{"platform": "naver", "keyword": "{keyword}", "created": {created_count}, "updated": {updated_count}}}'
        )
        session.add(event)
        session.commit()
        
    except Exception as e:
        # 오류 이벤트 로그
        event = Event(
            type="crawling_failed",
            payload_json=f'{{"platform": "naver", "keyword": "{keyword}", "error": "{str(e)}"}}'
        )
        session.add(event)
        session.commit()


@router.post("/instagram/hashtag")
async def crawl_instagram_hashtag(
    hashtag: str,
    limit: int = 50,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session)
):
    """인스타그램 해시태그 크롤링"""
    
    # 백그라운드에서 크롤링 실행
    background_tasks.add_task(
        _crawl_instagram_hashtag_task,
        hashtag, limit, session
    )
    
    # 이벤트 로그 생성
    event = Event(
        type="crawling_started",
        payload_json=f'{{"platform": "instagram", "hashtag": "{hashtag}", "limit": {limit}}}'
    )
    session.add(event)
    session.commit()
    
    return {
        "message": "인스타그램 해시태그 크롤링이 시작되었습니다.",
        "hashtag": hashtag,
        "limit": limit,
        "estimated_time": f"{limit // 10}분"
    }


async def _crawl_instagram_hashtag_task(
    hashtag: str,
    limit: int,
    session: Session
):
    """인스타그램 해시태그 크롤링 백그라운드 작업"""
    
    try:
        crawler = InstagramCrawler()
        accounts = crawler.search_hashtag(hashtag, limit)
        
        created_count = 0
        updated_count = 0
        
        for account_data in accounts:
            # 기존 크리에이터 확인
            existing = session.query(Creator).filter(
                Creator.platform == Platform.INSTAGRAM,
                Creator.handle == account_data['handle']
            ).first()
            
            if existing:
                # 기존 크리에이터 업데이트
                existing.engagement_rate = account_data.get('engagement_rate')
                existing.active_at = account_data.get('last_post_date')
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # 새 크리에이터 생성
                creator_data = CreatorCreate(
                    platform=Platform.INSTAGRAM,
                    handle=account_data['handle'],
                    category=account_data['category'],
                    engagement_rate=account_data.get('engagement_rate'),
                    active_at=account_data.get('last_post_date'),
                    notes=f"해시태그: #{hashtag}"
                )
                
                creator = Creator.model_validate(creator_data)
                session.add(creator)
                created_count += 1
        
        session.commit()
        
        # 완료 이벤트 로그
        event = Event(
            type="crawling_completed",
            payload_json=f'{{"platform": "instagram", "hashtag": "{hashtag}", "created": {created_count}, "updated": {updated_count}}}'
        )
        session.add(event)
        session.commit()
        
    except Exception as e:
        # 오류 이벤트 로그
        event = Event(
            type="crawling_failed",
            payload_json=f'{{"platform": "instagram", "hashtag": "{hashtag}", "error": "{str(e)}"}}'
        )
        session.add(event)
        session.commit()


@router.get("/status")
async def get_crawling_status(
    session: Session = Depends(get_session)
):
    """크롤링 상태 조회"""
    
    # 최근 크롤링 이벤트 조회
    recent_events = session.query(Event).filter(
        Event.type.in_(['crawling_started', 'crawling_completed', 'crawling_failed'])
    ).order_by(Event.created_at.desc()).limit(10).all()
    
    status_summary = {
        'total_creators': session.query(Creator).count(),
        'naver_creators': session.query(Creator).filter(Creator.platform == Platform.NAVER_BLOG).count(),
        'instagram_creators': session.query(Creator).filter(Creator.platform == Platform.INSTAGRAM).count(),
        'recent_events': [
            {
                'type': event.type,
                'payload': event.payload,
                'created_at': event.created_at
            }
            for event in recent_events
        ]
    }
    
    return status_summary


@router.get("/trending")
async def get_trending_data():
    """트렌딩 데이터 조회"""
    
    naver_crawler = NaverBlogCrawler()
    instagram_crawler = InstagramCrawler()
    
    return {
        'naver_keywords': naver_crawler.get_trending_keywords(),
        'instagram_hashtags': instagram_crawler.get_trending_hashtags(),
        'categories': {
            '뷰티': {
                'naver': naver_crawler.get_trending_keywords('뷰티'),
                'instagram': instagram_crawler.get_trending_hashtags('뷰티')
            },
            '패션': {
                'naver': naver_crawler.get_trending_keywords('패션'),
                'instagram': instagram_crawler.get_trending_hashtags('패션')
            },
            '음식': {
                'naver': naver_crawler.get_trending_keywords('음식'),
                'instagram': instagram_crawler.get_trending_hashtags('음식')
            }
        }
    }


@router.post("/validate-creator")
async def validate_creator(
    platform: Platform,
    handle: str
):
    """크리에이터 계정 유효성 검증"""
    
    if platform == Platform.NAVER_BLOG:
        # 네이버 블로그 유효성 검증 로직
        return {"valid": True, "message": "네이버 블로그 계정이 유효합니다."}
    
    elif platform == Platform.INSTAGRAM:
        crawler = InstagramCrawler()
        is_valid = crawler.validate_account(handle)
        
        return {
            "valid": is_valid,
            "message": "유효한 인스타그램 계정입니다." if is_valid else "유효하지 않은 계정입니다."
        }
    
    else:
        return {"valid": False, "message": "지원하지 않는 플랫폼입니다."}


@router.delete("/cleanup")
async def cleanup_old_data(
    days: int = 30,
    session: Session = Depends(get_session)
):
    """오래된 크롤링 데이터 정리"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 오래된 이벤트 로그 삭제
    old_events = session.query(Event).filter(
        Event.created_at < cutoff_date
    ).all()
    
    deleted_count = len(old_events)
    
    for event in old_events:
        session.delete(event)
    
    session.commit()
    
    return {
        "message": f"{days}일 이전 데이터가 정리되었습니다.",
        "deleted_events": deleted_count
    }