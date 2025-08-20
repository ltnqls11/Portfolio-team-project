"""
블로거 관리 API
네이버 블로그 중심의 블로거 관리 시스템
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta

from database.database import get_session
from database.models import (
    Blogger, BloggerCreate, BloggerRead,
    Platform
)

router = APIRouter()


@router.post("/", response_model=BloggerRead, status_code=status.HTTP_201_CREATED)
async def create_blogger(
    blogger: BloggerCreate,
    session: Session = Depends(get_session)
):
    """새 블로거 등록"""
    
    # 중복 확인 (블로그 URL)
    existing = session.exec(
        select(Blogger).where(Blogger.blog_url == blogger.blog_url)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 블로그입니다."
        )
    
    # 블로거 생성
    db_blogger = Blogger.model_validate(blogger)
    session.add(db_blogger)
    session.commit()
    session.refresh(db_blogger)
    
    return db_blogger


@router.get("/", response_model=List[BloggerRead])
async def get_bloggers(
    category: Optional[str] = None,
    min_posts: Optional[int] = Query(None, ge=0, description="최소 포스팅 수"),
    max_posts: Optional[int] = Query(None, ge=0, description="최대 포스팅 수"),
    active_days: Optional[int] = Query(None, ge=1, description="최근 활동일 기준 (일)"),
    has_contact: Optional[bool] = Query(None, description="연락처 정보 보유 여부"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """블로거 목록 조회 (필터링 지원)"""
    
    query = select(Blogger).where(Blogger.is_active == True)
    
    # 필터 적용
    if category:
        query = query.where(Blogger.category.ilike(f"%{category}%"))
    
    if min_posts is not None:
        query = query.where(Blogger.post_count >= min_posts)
    
    if max_posts is not None:
        query = query.where(Blogger.post_count <= max_posts)
    
    if active_days is not None:
        cutoff_date = datetime.utcnow() - timedelta(days=active_days)
        query = query.where(Blogger.last_post_date >= cutoff_date)
    
    if has_contact is not None:
        if has_contact:
            query = query.where(
                or_(
                    Blogger.email.isnot(None),
                    Blogger.contact_info.isnot(None)
                )
            )
        else:
            query = query.where(
                and_(
                    Blogger.email.is_(None),
                    Blogger.contact_info.is_(None)
                )
            )
    
    # 정렬 (포스팅 수 내림차순)
    query = query.order_by(Blogger.post_count.desc())
    
    # 페이지네이션
    query = query.offset(skip).limit(limit)
    
    bloggers = session.exec(query).all()
    return bloggers


@router.get("/{blogger_id}", response_model=BloggerRead)
async def get_blogger(
    blogger_id: int,
    session: Session = Depends(get_session)
):
    """특정 블로거 조회"""
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    return blogger


@router.put("/{blogger_id}", response_model=BloggerRead)
async def update_blogger(
    blogger_id: int,
    blogger_update: BloggerCreate,
    session: Session = Depends(get_session)
):
    """블로거 정보 수정"""
    
    db_blogger = session.get(Blogger, blogger_id)
    if not db_blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    # 업데이트
    blogger_data = blogger_update.model_dump(exclude_unset=True)
    for field, value in blogger_data.items():
        setattr(db_blogger, field, value)
    
    db_blogger.updated_at = datetime.utcnow()
    session.add(db_blogger)
    session.commit()
    session.refresh(db_blogger)
    
    return db_blogger


@router.patch("/{blogger_id}/contact")
async def update_blogger_contact(
    blogger_id: int,
    email: Optional[str] = None,
    contact_info: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """블로거 연락처 정보 업데이트"""
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    if email is not None:
        blogger.email = email
    if contact_info is not None:
        blogger.contact_info = contact_info
    
    blogger.updated_at = datetime.utcnow()
    session.add(blogger)
    session.commit()
    
    return {"message": "연락처 정보가 업데이트되었습니다."}


@router.patch("/{blogger_id}/price")
async def update_blogger_price(
    blogger_id: int,
    price_range: str,
    session: Session = Depends(get_session)
):
    """블로거 협찬 단가 업데이트"""
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    blogger.price_range = price_range
    blogger.updated_at = datetime.utcnow()
    session.add(blogger)
    session.commit()
    
    return {"message": "협찬 단가가 업데이트되었습니다."}


@router.delete("/{blogger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blogger(
    blogger_id: int,
    session: Session = Depends(get_session)
):
    """블로거 삭제 (비활성화)"""
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    blogger.is_active = False
    blogger.updated_at = datetime.utcnow()
    session.add(blogger)
    session.commit()


@router.get("/search/", response_model=List[BloggerRead])
async def search_bloggers(
    q: str = Query(..., min_length=2, description="검색어"),
    session: Session = Depends(get_session)
):
    """블로거 검색 (블로그명, 블로거명, 카테고리 기준)"""
    
    query = select(Blogger).where(
        and_(
            Blogger.is_active == True,
            or_(
                Blogger.blog_name.ilike(f"%{q}%"),
                Blogger.blogger_name.ilike(f"%{q}%"),
                Blogger.category.ilike(f"%{q}%")
            )
        )
    ).limit(50)
    
    bloggers = session.exec(query).all()
    return bloggers


@router.get("/categories/", response_model=List[str])
async def get_blogger_categories(
    session: Session = Depends(get_session)
):
    """블로거 카테고리 목록"""
    
    query = select(Blogger.category).distinct().where(Blogger.is_active == True)
    categories = session.exec(query).all()
    return [cat for cat in categories if cat]


@router.get("/stats/overview")
async def get_blogger_stats(
    session: Session = Depends(get_session)
):
    """블로거 통계 개요"""
    
    total_bloggers = session.exec(
        select(Blogger).where(Blogger.is_active == True)
    ).all()
    
    # 카테고리별 통계
    category_stats = {}
    for blogger in total_bloggers:
        category = blogger.category
        if category not in category_stats:
            category_stats[category] = {
                "count": 0,
                "avg_posts": 0,
                "with_contact": 0
            }
        
        category_stats[category]["count"] += 1
        if blogger.post_count:
            category_stats[category]["avg_posts"] += blogger.post_count
        if blogger.email or blogger.contact_info:
            category_stats[category]["with_contact"] += 1
    
    # 평균 계산
    for category in category_stats:
        if category_stats[category]["count"] > 0:
            category_stats[category]["avg_posts"] = round(
                category_stats[category]["avg_posts"] / category_stats[category]["count"]
            )
    
    return {
        "total_bloggers": len(total_bloggers),
        "categories": len(category_stats),
        "with_contact_info": len([b for b in total_bloggers if b.email or b.contact_info]),
        "category_breakdown": category_stats
    }


@router.post("/{blogger_id}/select-for-campaign")
async def select_blogger_for_campaign(
    blogger_id: int,
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """캠페인용 블로거 선택 (포스팅 제안 준비)"""
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    # 연락처 정보 확인
    if not blogger.email and not blogger.contact_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="해당 블로거의 연락처 정보가 없습니다."
        )
    
    return {
        "message": "블로거가 선택되었습니다.",
        "blogger_id": blogger_id,
        "campaign_id": campaign_id,
        "blogger_name": blogger.blogger_name,
        "blog_name": blogger.blog_name,
        "contact_available": bool(blogger.email or blogger.contact_info)
    }