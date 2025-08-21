from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
from enum import Enum
import os
from dotenv import load_dotenv
import json

load_dotenv()

# 앱 설정
app = FastAPI(title="Marketing Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 설정 (SQLite로 간단하게)
DATABASE_URL = "sqlite:///./marketing_platform.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# 모델 정의
class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"

class CreatorCategory(str, Enum):
    BEAUTY = "beauty"
    FASHION = "fashion"
    TECH = "tech"
    FITNESS = "fitness"

# 데이터베이스 모델
class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    product_info: str
    target_audience: str
    campaign_goal: str
    budget: Optional[float] = None
    keywords: Optional[str] = None  # JSON 문자열
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Creator(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    platform: str
    followers_count: int = Field(default=0)
    engagement_rate: float = Field(default=0.0)
    category: CreatorCategory
    trust_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CopyVariant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    content: str
    channel: str
    tone: str
    length: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 요청/응답 모델
class CampaignCreate(SQLModel):
    title: str
    product_info: str
    target_audience: str
    campaign_goal: str
    budget: Optional[float] = None
    keywords: Optional[str] = None

class CopyGenerateRequest(SQLModel):
    channel: str
    count: Optional[int] = 3

# 시작시 테이블 생성
@app.on_event("startup")
def create_tables():
    SQLModel.metadata.create_all(engine)
    
    # 샘플 데이터 추가
    with Session(engine) as session:
        # 크리에이터 샘플 데이터
        creators = [
            Creator(username="@beauty_jenny", platform="instagram", 
                   followers_count=85000, engagement_rate=4.2, 
                   category=CreatorCategory.BEAUTY, trust_score=92),
            Creator(username="@fitness_mike", platform="youtube", 
                   followers_count=150000, engagement_rate=6.8, 
                   category=CreatorCategory.FITNESS, trust_score=88),
            Creator(username="@tech_reviewer", platform="youtube", 
                   followers_count=320000, engagement_rate=5.5, 
                   category=CreatorCategory.TECH, trust_score=95),
        ]
        
        for creator in creators:
            existing = session.exec(select(Creator).where(Creator.username == creator.username)).first()
            if not existing:
                session.add(creator)
        
        session.commit()

# API 엔드포인트들
@app.get("/")
async def root():
    return {"message": "Marketing Platform API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# 대시보드 통계
@app.get("/api/dashboard/stats")
async def dashboard_stats():
    with Session(engine) as session:
        total_campaigns = len(session.exec(select(Campaign)).all())
        active_campaigns = len(session.exec(select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)).all())
        total_creators = len(session.exec(select(Creator)).all())
        
    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_creators": total_creators,
        "total_outreach": 0  # 추후 구현
    }

# 캠페인 관련 API
@app.post("/api/campaigns", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate):
    with Session(engine) as session:
        db_campaign = Campaign(**campaign.dict())
        session.add(db_campaign)
        session.commit()
        session.refresh(db_campaign)
        return db_campaign

@app.get("/api/campaigns", response_model=List[Campaign])
async def get_campaigns():
    with Session(engine) as session:
        campaigns = session.exec(select(Campaign)).all()
        return campaigns

@app.get("/api/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: int):
    with Session(engine) as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign

# AI 문구 생성 (Mock 구현)
@app.post("/api/campaigns/{campaign_id}/generate-copy")
async def generate_copy(campaign_id: int, request: CopyGenerateRequest):
    with Session(engine) as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Mock 문구 생성 (실제로는 OpenAI API 사용)
        mock_variants = [
            {
                "content": f"✨ {campaign.product_info}로 새로운 경험을 시작하세요! {campaign.target_audience}를 위한 완벽한 솔루션 #신제품 #혁신",
                "tone": "enthusiastic",
                "length": 85
            },
            {
                "content": f"{campaign.product_info} - {campaign.target_audience}가 찾던 바로 그것! 지금 바로 확인해보세요.",
                "tone": "professional", 
                "length": 65
            },
            {
                "content": f"와우! 이런 {campaign.product_info} 처음이야 🔥 {campaign.target_audience} 여러분 놓치면 후회할걸?",
                "tone": "casual",
                "length": 72
            }
        ]
        
        # DB에 저장
        db_variants = []
        for variant in mock_variants[:request.count]:
            db_copy = CopyVariant(
                campaign_id=campaign_id,
                content=variant["content"],
                channel=request.channel,
                tone=variant["tone"],
                length=variant["length"]
            )
            session.add(db_copy)
            db_variants.append(variant)
        
        session.commit()
        return {"variants": db_variants, "count": len(db_variants)}

@app.get("/api/campaigns/{campaign_id}/copy-variants")
async def get_copy_variants(campaign_id: int):
    with Session(engine) as session:
        variants = session.exec(select(CopyVariant).where(CopyVariant.campaign_id == campaign_id)).all()
        return variants

# 크리에이터 관련 API
@app.get("/api/creators", response_model=List[Creator])
async def get_creators(
    category: Optional[CreatorCategory] = None,
    platform: Optional[str] = None,
    min_followers: Optional[int] = None
):
    with Session(engine) as session:
        query = select(Creator)
        
        if category:
            query = query.where(Creator.category == category)
        if platform:
            query = query.where(Creator.platform == platform)
        if min_followers:
            query = query.where(Creator.followers_count >= min_followers)
            
        creators = session.exec(query.order_by(Creator.trust_score.desc())).all()
        return creators

@app.get("/api/campaigns/{campaign_id}/recommended-creators")
async def get_recommended_creators(campaign_id: int, limit: int = 10):
    with Session(engine) as session:
        campaign = session.get(Campaign, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
            
        creators = session.exec(select(Creator).order_by(Creator.trust_score.desc()).limit(limit)).all()
        
        recommendations = []
        for creator in creators:
            # 간단한 매칭 점수 계산
            base_score = creator.trust_score
            follower_bonus = min(creator.followers_count / 10000, 10)
            engagement_bonus = creator.engagement_rate * 5
            
            match_score = min(base_score + follower_bonus + engagement_bonus, 100)
            
            recommendations.append({
                "creator": creator,
                "match_score": round(match_score, 1)
            })
        
        return {"recommendations": recommendations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)