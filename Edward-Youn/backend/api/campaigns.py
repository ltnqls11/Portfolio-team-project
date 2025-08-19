"""
캠페인 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json

from database.database import get_session
from database.models import (
    Campaign, CampaignCreate, CampaignRead,
    CampaignStatus, Client
)

router = APIRouter()


@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign: CampaignCreate,
    session: Session = Depends(get_session)
):
    """새 캠페인 생성"""
    
    # 클라이언트 존재 확인
    client = session.get(Client, campaign.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클라이언트를 찾을 수 없습니다."
        )
    
    # 캠페인 생성
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    
    return db_campaign


@router.get("/", response_model=List[CampaignRead])
async def get_campaigns(
    client_id: Optional[int] = None,
    status: Optional[CampaignStatus] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """캠페인 목록 조회"""
    
    query = select(Campaign)
    
    # 필터 적용
    if client_id:
        query = query.where(Campaign.client_id == client_id)
    if status:
        query = query.where(Campaign.status == status)
    
    # 페이지네이션
    query = query.offset(skip).limit(limit)
    
    campaigns = session.exec(query).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """특정 캠페인 조회"""
    
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    return campaign


@router.put("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(
    campaign_id: int,
    campaign_update: CampaignCreate,
    session: Session = Depends(get_session)
):
    """캠페인 수정"""
    
    db_campaign = session.get(Campaign, campaign_id)
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    # 업데이트
    campaign_data = campaign_update.model_dump(exclude_unset=True)
    for field, value in campaign_data.items():
        setattr(db_campaign, field, value)
    
    db_campaign.updated_at = datetime.utcnow()
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    
    return db_campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """캠페인 삭제"""
    
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    session.delete(campaign)
    session.commit()


@router.patch("/{campaign_id}/status")
async def update_campaign_status(
    campaign_id: int,
    new_status: CampaignStatus,
    session: Session = Depends(get_session)
):
    """캠페인 상태 변경"""
    
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    campaign.status = new_status
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    
    return {"message": f"캠페인 상태가 {new_status.value}로 변경되었습니다."}


@router.get("/{campaign_id}/keywords")
async def get_campaign_keywords(
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """캠페인 키워드 조회"""
    
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    return {"keywords": campaign.keywords_list}


@router.put("/{campaign_id}/keywords")
async def update_campaign_keywords(
    campaign_id: int,
    keywords: List[str],
    session: Session = Depends(get_session)
):
    """캠페인 키워드 업데이트"""
    
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    campaign.keywords = json.dumps(keywords, ensure_ascii=False)
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    
    return {"message": "키워드가 업데이트되었습니다.", "keywords": keywords}