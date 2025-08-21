from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class OutreachStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    RESPONDED = "responded"
    DECLINED = "declined"

class CreatorCategory(str, Enum):
    BEAUTY = "beauty"
    FASHION = "fashion"
    TECH = "tech"
    FOOD = "food"
    FITNESS = "fitness"
    LIFESTYLE = "lifestyle"

# Client Model
class ClientBase(SQLModel):
    company_name: str
    email: str = Field(unique=True, index=True)
    contact_person: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool = Field(default=True)

class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    campaigns: List["Campaign"] = Relationship(back_populates="client")

# Campaign Model
class CampaignBase(SQLModel):
    title: str
    description: Optional[str] = None
    product_info: str
    target_audience: str
    campaign_goal: str
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    keywords: str  # JSON string
    channels: str  # JSON string
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)

class Campaign(CampaignBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    client: Client = Relationship(back_populates="campaigns")
    copy_variants: List["CopyVariant"] = Relationship(back_populates="campaign")
    outreach_records: List["Outreach"] = Relationship(back_populates="campaign")

# Copy Variant Model
class CopyVariantBase(SQLModel):
    content: str
    channel: str
    tone: str
    length: int
    seo_keywords: Optional[str] = None
    is_approved: bool = Field(default=False)

class CopyVariant(CopyVariantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    campaign: Campaign = Relationship(back_populates="copy_variants")

# Creator Model
class CreatorBase(SQLModel):
    username: str = Field(unique=True, index=True)
    platform: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    followers_count: int = Field(default=0)
    engagement_rate: float = Field(default=0.0)
    avg_views: Optional[int] = None
    category: CreatorCategory
    location: Optional[str] = None
    bio: Optional[str] = None
    profile_url: str
    last_post_date: Optional[datetime] = None
    is_verified: bool = Field(default=False)
    trust_score: float = Field(default=0.0)

class Creator(CreatorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    outreach_records: List["Outreach"] = Relationship(back_populates="creator")

# Outreach Model
class OutreachBase(SQLModel):
    subject: str
    message: str
    contact_method: str
    status: OutreachStatus = Field(default=OutreachStatus.PENDING)
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    response_message: Optional[str] = None

class Outreach(OutreachBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    creator_id: int = Field(foreign_key="creator.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    campaign: Campaign = Relationship(back_populates="outreach_records")
    creator: Creator = Relationship(back_populates="outreach_records")
    deliverables: List["Deliverable"] = Relationship(back_populates="outreach")

# Deliverable Model
class DeliverableBase(SQLModel):
    content_url: str
    platform: str
    post_date: Optional[datetime] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    shares_count: Optional[int] = None
    views_count: Optional[int] = None
    clicks_count: Optional[int] = None
    conversions_count: Optional[int] = None

class Deliverable(DeliverableBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    outreach_id: int = Field(foreign_key="outreach.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    outreach: Outreach = Relationship(back_populates="deliverables")

# Event Log Model
class EventLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str
    entity_type: str
    entity_id: int
    user_id: Optional[int] = None
    data: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)