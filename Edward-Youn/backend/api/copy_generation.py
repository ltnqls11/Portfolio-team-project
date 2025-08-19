"""
홍보 문구 생성 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any
from datetime import datetime
import json

from database.database import get_session
from database.models import (
    CopyVariant, CopyVariantCreate, CopyVariantRead,
    Campaign, Platform
)
from services.copy_generator import CopyGeneratorService

router = APIRouter()


@router.post("/generate/{campaign_id}", response_model=List[CopyVariantRead])
async def generate_copy_variants(
    campaign_id: int,
    channels: List[Platform],
    session: Session = Depends(get_session)
):
    """캠페인용 홍보 문구 생성"""
    
    # 캠페인 확인
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    # 문구 생성 서비스 초기화
    copy_service = CopyGeneratorService()
    
    generated_variants = []
    
    for channel in channels:
        try:
            # 채널별 문구 생성 (3개씩)
            variants = await copy_service.generate_variants(
                campaign=campaign,
                channel=channel,
                count=3
            )
            
            for variant_data in variants:
                # DB에 저장
                copy_variant = CopyVariant(
                    campaign_id=campaign_id,
                    channel=channel,
                    tone=variant_data.get("tone", "professional"),
                    length=len(variant_data["text"]),
                    text=variant_data["text"],
                    score=variant_data.get("score", 0.8)
                )
                
                session.add(copy_variant)
                generated_variants.append(copy_variant)
        
        except Exception as e:
            # 개별 채널 실패 시 로그만 남기고 계속 진행
            print(f"문구 생성 실패 - 채널: {channel}, 오류: {str(e)}")
            continue
    
    if not generated_variants:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="문구 생성에 실패했습니다."
        )
    
    session.commit()
    
    # 생성된 문구들 새로고침
    for variant in generated_variants:
        session.refresh(variant)
    
    return generated_variants


@router.get("/campaign/{campaign_id}", response_model=List[CopyVariantRead])
async def get_campaign_copy_variants(
    campaign_id: int,
    channel: Platform = None,
    approved_only: bool = False,
    session: Session = Depends(get_session)
):
    """캠페인의 생성된 문구 목록 조회"""
    
    query = select(CopyVariant).where(CopyVariant.campaign_id == campaign_id)
    
    if channel:
        query = query.where(CopyVariant.channel == channel)
    
    if approved_only:
        query = query.where(CopyVariant.approved == True)
    
    # 점수 내림차순 정렬
    query = query.order_by(CopyVariant.score.desc())
    
    variants = session.exec(query).all()
    return variants


@router.get("/{variant_id}", response_model=CopyVariantRead)
async def get_copy_variant(
    variant_id: int,
    session: Session = Depends(get_session)
):
    """특정 문구 조회"""
    
    variant = session.get(CopyVariant, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문구를 찾을 수 없습니다."
        )
    
    return variant


@router.patch("/{variant_id}/approve")
async def approve_copy_variant(
    variant_id: int,
    session: Session = Depends(get_session)
):
    """문구 승인"""
    
    variant = session.get(CopyVariant, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문구를 찾을 수 없습니다."
        )
    
    variant.approved = True
    session.add(variant)
    session.commit()
    
    return {"message": "문구가 승인되었습니다."}


@router.patch("/{variant_id}/reject")
async def reject_copy_variant(
    variant_id: int,
    session: Session = Depends(get_session)
):
    """문구 거부"""
    
    variant = session.get(CopyVariant, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문구를 찾을 수 없습니다."
        )
    
    variant.approved = False
    session.add(variant)
    session.commit()
    
    return {"message": "문구가 거부되었습니다."}


@router.put("/{variant_id}/text")
async def update_copy_text(
    variant_id: int,
    new_text: str,
    session: Session = Depends(get_session)
):
    """문구 텍스트 수정"""
    
    variant = session.get(CopyVariant, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문구를 찾을 수 없습니다."
        )
    
    variant.text = new_text
    variant.length = len(new_text)
    variant.approved = False  # 수정 시 재승인 필요
    session.add(variant)
    session.commit()
    
    return {"message": "문구가 수정되었습니다."}


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_copy_variant(
    variant_id: int,
    session: Session = Depends(get_session)
):
    """문구 삭제"""
    
    variant = session.get(CopyVariant, variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문구를 찾을 수 없습니다."
        )
    
    session.delete(variant)
    session.commit()


@router.get("/templates/{channel}")
async def get_copy_templates(
    channel: Platform
):
    """채널별 문구 템플릿 조회"""
    
    copy_service = CopyGeneratorService()
    templates = copy_service.get_channel_templates(channel)
    
    return {
        "channel": channel.value,
        "templates": templates
    }


@router.post("/analyze")
async def analyze_copy_performance(
    variant_ids: List[int],
    session: Session = Depends(get_session)
):
    """문구 성과 분석"""
    
    variants = []
    for variant_id in variant_ids:
        variant = session.get(CopyVariant, variant_id)
        if variant:
            variants.append(variant)
    
    if not variants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="분석할 문구가 없습니다."
        )
    
    # 간단한 분석 결과 반환
    analysis = {
        "total_variants": len(variants),
        "approved_count": sum(1 for v in variants if v.approved),
        "avg_length": sum(v.length for v in variants) / len(variants),
        "avg_score": sum(v.score or 0 for v in variants) / len(variants),
        "channel_distribution": {}
    }
    
    # 채널별 분포
    for variant in variants:
        channel = variant.channel.value
        if channel not in analysis["channel_distribution"]:
            analysis["channel_distribution"][channel] = 0
        analysis["channel_distribution"][channel] += 1
    
    return analysis