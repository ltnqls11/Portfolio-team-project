"""
캠페인 관리 API 엔드포인트
캠페인 생성, 조회, 수정, 삭제 기능
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

# 라우터 생성
router = APIRouter()

# Pydantic 모델 (요청/응답 스키마)
class CampaignStatus(str, Enum):
    """캠페인 상태"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Platform(str, Enum):
    """지원 플랫폼"""
    NAVER_BLOG = "naver_blog"
    INSTAGRAM = "instagram"
    TISTORY = "tistory"
    BLOGSPOT = "blogspot"
    KAKAO_CHANNEL = "kakao_channel"

class CampaignCreate(BaseModel):
    """캠페인 생성 요청 모델"""
    client_id: int = Field(..., description="광고주 ID")
    title: str = Field(..., min_length=1, max_length=200, description="캠페인 제목")
    objective: str = Field(..., description="캠페인 목표")
    budget: float = Field(..., gt=0, description="예산")
    start_at: datetime = Field(..., description="시작일")
    end_at: datetime = Field(..., description="종료일")
    
    # 캠페인 설정
    target_platforms: List[Platform] = Field(..., description="타겟 플랫폼")
    keywords: List[str] = Field(..., description="핵심 키워드")
    reference_urls: Optional[List[str]] = Field(None, description="참고 URL")
    
    # 제품 정보
    product_name: str = Field(..., description="제품/서비스명")
    product_description: str = Field(..., description="제품/서비스 설명")
    product_benefits: List[str] = Field(..., description="주요 효익")
    
    # 타겟 오디언스
    target_age: Optional[str] = Field(None, description="타겟 연령대", example="20-30")
    target_gender: Optional[str] = Field(None, description="타겟 성별", example="all")
    target_interests: Optional[List[str]] = Field(None, description="관심사")
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": 1,
                "title": "2024 신제품 런칭 캠페인",
                "objective": "신제품 인지도 향상 및 초기 판매 증대",
                "budget": 5000000,
                "start_at": "2024-02-01T00:00:00",
                "end_at": "2024-02-28T23:59:59",
                "target_platforms": ["naver_blog", "instagram"],
                "keywords": ["스킨케어", "수분크림", "민감성피부"],
                "reference_urls": ["https://example.com/product"],
                "product_name": "퓨어 모이스처 크림",
                "product_description": "민감성 피부를 위한 저자극 수분크림",
                "product_benefits": ["72시간 보습", "저자극 테스트 완료", "비건 인증"],
                "target_age": "20-35",
                "target_gender": "female",
                "target_interests": ["뷰티", "스킨케어", "클린뷰티"]
            }
        }

class CampaignUpdate(BaseModel):
    """캠페인 수정 요청 모델"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    objective: Optional[str] = None
    budget: Optional[float] = Field(None, gt=0)
    status: Optional[CampaignStatus] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    target_platforms: Optional[List[Platform]] = None
    keywords: Optional[List[str]] = None

class CampaignResponse(BaseModel):
    """캠페인 응답 모델"""
    id: int
    client_id: int
    title: str
    objective: str
    budget: float
    status: CampaignStatus
    start_at: datetime
    end_at: datetime
    target_platforms: List[Platform]
    keywords: List[str]
    product_name: str
    created_at: datetime
    updated_at: datetime
    
    # 통계 정보
    total_outreaches: int = 0
    accepted_outreaches: int = 0
    total_deliverables: int = 0
    total_spent: float = 0

class CampaignListResponse(BaseModel):
    """캠페인 목록 응답 모델"""
    total: int
    page: int
    per_page: int
    campaigns: List[CampaignResponse]

# 임시 데이터 저장소 (실제로는 데이터베이스 사용)
fake_campaigns_db = []

# API 엔드포인트
@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(campaign: CampaignCreate):
    """
    새 캠페인 생성
    
    - **client_id**: 광고주 ID (필수)
    - **title**: 캠페인 제목 (필수)
    - **objective**: 캠페인 목표
    - **budget**: 예산
    - **target_platforms**: 타겟 플랫폼 리스트
    - **keywords**: 핵심 키워드 리스트
    """
    # 실제로는 데이터베이스에 저장
    new_campaign = {
        "id": len(fake_campaigns_db) + 1,
        **campaign.dict(),
        "status": CampaignStatus.DRAFT,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "total_outreaches": 0,
        "accepted_outreaches": 0,
        "total_deliverables": 0,
        "total_spent": 0
    }
    fake_campaigns_db.append(new_campaign)
    
    return CampaignResponse(**new_campaign)

@router.get("/", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    status: Optional[CampaignStatus] = Query(None, description="캠페인 상태 필터"),
    client_id: Optional[int] = Query(None, description="광고주 ID 필터")
):
    """
    캠페인 목록 조회
    
    - 페이지네이션 지원
    - 상태별 필터링
    - 광고주별 필터링
    """
    # 필터링
    filtered_campaigns = fake_campaigns_db
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.get("status") == status]
    if client_id:
        filtered_campaigns = [c for c in filtered_campaigns if c.get("client_id") == client_id]
    
    # 페이지네이션
    total = len(filtered_campaigns)
    start = (page - 1) * per_page
    end = start + per_page
    campaigns = filtered_campaigns[start:end]
    
    return CampaignListResponse(
        total=total,
        page=page,
        per_page=per_page,
        campaigns=[CampaignResponse(**c) for c in campaigns]
    )

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int):
    """
    특정 캠페인 상세 조회
    """
    # 실제로는 데이터베이스에서 조회
    for campaign in fake_campaigns_db:
        if campaign["id"] == campaign_id:
            return CampaignResponse(**campaign)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )

@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, update: CampaignUpdate):
    """
    캠페인 정보 수정
    """
    # 실제로는 데이터베이스에서 업데이트
    for campaign in fake_campaigns_db:
        if campaign["id"] == campaign_id:
            update_data = update.dict(exclude_unset=True)
            for key, value in update_data.items():
                campaign[key] = value
            campaign["updated_at"] = datetime.now()
            return CampaignResponse(**campaign)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )

@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: int):
    """
    캠페인 삭제
    """
    # 실제로는 데이터베이스에서 삭제
    for i, campaign in enumerate(fake_campaigns_db):
        if campaign["id"] == campaign_id:
            del fake_campaigns_db[i]
            return
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )

@router.post("/{campaign_id}/activate", response_model=CampaignResponse)
async def activate_campaign(campaign_id: int):
    """
    캠페인 활성화
    """
    for campaign in fake_campaigns_db:
        if campaign["id"] == campaign_id:
            if campaign["status"] != CampaignStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Draft 상태의 캠페인만 활성화할 수 있습니다."
                )
            campaign["status"] = CampaignStatus.ACTIVE
            campaign["updated_at"] = datetime.now()
            return CampaignResponse(**campaign)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )

@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(campaign_id: int):
    """
    캠페인 일시정지
    """
    for campaign in fake_campaigns_db:
        if campaign["id"] == campaign_id:
            if campaign["status"] != CampaignStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Active 상태의 캠페인만 일시정지할 수 있습니다."
                )
            campaign["status"] = CampaignStatus.PAUSED
            campaign["updated_at"] = datetime.now()
            return CampaignResponse(**campaign)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )

@router.get("/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: int):
    """
    캠페인 통계 조회
    """
    for campaign in fake_campaigns_db:
        if campaign["id"] == campaign_id:
            return {
                "campaign_id": campaign_id,
                "total_outreaches": campaign.get("total_outreaches", 0),
                "accepted_outreaches": campaign.get("accepted_outreaches", 0),
                "rejection_rate": 0,  # 계산 필요
                "total_deliverables": campaign.get("total_deliverables", 0),
                "total_spent": campaign.get("total_spent", 0),
                "remaining_budget": campaign["budget"] - campaign.get("total_spent", 0),
                "avg_engagement_rate": 0,  # 계산 필요
                "total_reach": 0,  # 계산 필요
                "total_impressions": 0,  # 계산 필요
                "roi": 0  # 계산 필요
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"캠페인 ID {campaign_id}를 찾을 수 없습니다."
    )
