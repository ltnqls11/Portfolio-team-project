from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Campaign, CampaignBase, CopyVariant
from ..services.copy_generator import CopyGeneratorService
import json

router = APIRouter()

@router.post("/", response_model=Campaign)
async def create_campaign(campaign: CampaignBase, session: Session = Depends(get_session)):
    db_campaign = Campaign.from_orm(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return db_campaign

@router.get("/", response_model=List[Campaign])
async def get_campaigns(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    campaigns = session.exec(select(Campaign).offset(skip).limit(limit)).all()
    return campaigns

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: int, session: Session = Depends(get_session)):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{campaign_id}/generate-copy")
async def generate_copy_variants(
    campaign_id: int,
    channel: str,
    count: int = 3,
    session: Session = Depends(get_session)
):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    copy_service = CopyGeneratorService()
    variants = await copy_service.generate_copy_variants(campaign, channel, count)
    
    # 생성된 문구들을 DB에 저장
    db_variants = []
    for variant in variants:
        db_copy = CopyVariant(
            campaign_id=campaign_id,
            content=variant["content"],
            channel=channel,
            tone=variant["tone"],
            length=variant["length"]
        )
        session.add(db_copy)
        db_variants.append(db_copy)
    
    session.commit()
    return {"variants": variants}

@router.get("/{campaign_id}/copy-variants", response_model=List[CopyVariant])
async def get_copy_variants(campaign_id: int, session: Session = Depends(get_session)):
    variants = session.exec(
        select(CopyVariant).where(CopyVariant.campaign_id == campaign_id)
    ).all()
    return variants