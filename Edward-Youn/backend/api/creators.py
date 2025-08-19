"""
크리에이터(인플루언서) 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta

from database.database import get_session
from database.models import (
    Creator, CreatorCreate, CreatorRead,
    Platform
)

router = APIRouter()


@router.post("/", response_model=CreatorRead, status_code=status.HTTP_201_CREATED)
async def create_creator(
    creator: CreatorCreate,
    session: Session = Depends(get_session)
):
    """새 크리에이터 등록"""
    
    # 중복 확인 (플랫폼 + 핸들)
    existing = session.exec(
        select(Creator).where(
            and_(
                Creator.platform == creator.platform,
                Creator.handle == creator.handle
            )
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 크리에이터입니다."
        )
    
    # 크리에이터 생성
    db_creator = Creator.model_validate(creator)
    session.add(db_creator)
    session.commit()
    session.refresh(db_creator)
    
    return db_creator


@router.get("/", response_model=List[CreatorRead])
async def get_creators(
    platform: Optional[Platform] = None,
    category: Optional[str] = None,
    min_followers: Optional[int] = Query(None, ge=0),
    max_followers: Optional[int] = Query(None, ge=0),
    min_engagement: Optional[float] = Query(None, ge=0, le=1),
    active_days: Optional[int] = Query(None, ge=1, description="최근 활동일 기준 (일)"),
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """크리에이터 목록 조회 (필터링 지원)"""
    
    query = select(Creator)
    
    # 필터 적용
    if platform:
        query = query.where(Creator.platform == platform)
    
    if category:
        query = query.where(Creator.category.ilike(f"%{category}%"))
    
    if min_followers is not None:
        query = query.where(Creator.followers >= min_followers)
    
    if max_followers is not None:
        query = query.where(Creator.followers <= max_followers)
    
    if min_engagement is not None:
        query = query.where(Creator.engagement_rate >= min_engagement)
    
    if active_days is not None:
        cutoff_date = datetime.utcnow() - timedelta(days=active_days)
        query = query.where(Creator.active_at >= cutoff_date)
    
    # 정렬 (팔로워 수 내림차순)
    query = query.order_by(Creator.followers.desc())
    
    # 페이지네이션
    query = query.offset(skip).limit(limit)
    
    creators = session.exec(query).all()
    return creators


@router.get("/{creator_id}", response_model=CreatorRead)
async def get_creator(
    creator_id: int,
    session: Session = Depends(get_session)
):
    """특정 크리에이터 조회"""
    
    creator = session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="크리에이터를 찾을 수 없습니다."
        )
    
    return creator


@router.put("/{creator_id}", response_model=CreatorRead)
async def update_creator(
    creator_id: int,
    creator_update: CreatorCreate,
    session: Session = Depends(get_session)
):
    """크리에이터 정보 수정"""
    
    db_creator = session.get(Creator, creator_id)
    if not db_creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="크리에이터를 찾을 수 없습니다."
        )
    
    # 업데이트
    creator_data = creator_update.model_dump(exclude_unset=True)
    for field, value in creator_data.items():
        setattr(db_creator, field, value)
    
    db_creator.updated_at = datetime.utcnow()
    session.add(db_creator)
    session.commit()
    session.refresh(db_creator)
    
    return db_creator


@router.delete("/{creator_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creator(
    creator_id: int,
    session: Session = Depends(get_session)
):
    """크리에이터 삭제"""
    
    creator = session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="크리에이터를 찾을 수 없습니다."
        )
    
    session.delete(creator)
    session.commit()


@router.get("/search/", response_model=List[CreatorRead])
async def search_creators(
    q: str = Query(..., min_length=2, description="검색어"),
    session: Session = Depends(get_session)
):
    """크리에이터 검색 (핸들, 카테고리 기준)"""
    
    query = select(Creator).where(
        or_(
            Creator.handle.ilike(f"%{q}%"),
            Creator.category.ilike(f"%{q}%")
        )
    ).limit(50)
    
    creators = session.exec(query).all()
    return creators


@router.get("/categories/", response_model=List[str])
async def get_creator_categories(
    session: Session = Depends(get_session)
):
    """크리에이터 카테고리 목록"""
    
    query = select(Creator.category).distinct()
    categories = session.exec(query).all()
    return [cat for cat in categories if cat]


@router.get("/stats/platform")
async def get_platform_stats(
    session: Session = Depends(get_session)
):
    """플랫폼별 크리에이터 통계"""
    
    stats = {}
    for platform in Platform:
        count = session.exec(
            select(Creator).where(Creator.platform == platform)
        ).all()
        stats[platform.value] = len(count)
    
    return stats


@router.post("/{creator_id}/update-activity")
async def update_creator_activity(
    creator_id: int,
    session: Session = Depends(get_session)
):
    """크리에이터 활동일 업데이트"""
    
    creator = session.get(Creator, creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="크리에이터를 찾을 수 없습니다."
        )
    
    creator.active_at = datetime.utcnow()
    creator.updated_at = datetime.utcnow()
    session.add(creator)
    session.commit()
    
    return {"message": "활동일이 업데이트되었습니다."}