"""
데이터베이스 모델 정의
온라인 마케팅 연계 플랫폼의 핵심 데이터 구조
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json


class CampaignStatus(str, Enum):
    """캠페인 상태"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OutreachStatus(str, Enum):
    """연락 상태"""
    PENDING = "pending"
    SENT = "sent"
    REPLIED = "replied"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Platform(str, Enum):
    """플랫폼 타입"""
    NAVER_BLOG = "naver_blog"
    INSTAGRAM = "instagram"
    TISTORY = "tistory"
    KAKAO_CHANNEL = "kakao_channel"


# 기본 모델
class TimestampMixin(SQLModel):
    """타임스탬프 믹스인"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# 클라이언트 (광고주)
class ClientBase(SQLModel):
    """클라이언트 기본 모델"""
    name: str = Field(max_length=100)
    industry: str = Field(max_length=50)
    contact_email: str = Field(max_length=100)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    company_url: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)


class Client(ClientBase, TimestampMixin, table=True):
    """클라이언트 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 관계
    campaigns: List["Campaign"] = Relationship(back_populates="client")


class ClientCreate(ClientBase):
    """클라이언트 생성 모델"""
    pass


class ClientRead(ClientBase):
    """클라이언트 조회 모델"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# 캠페인
class CampaignBase(SQLModel):
    """캠페인 기본 모델"""
    title: str = Field(max_length=200)
    objective: str = Field(max_length=500)
    budget: Optional[float] = Field(default=None, ge=0)
    start_at: Optional[datetime] = Field(default=None)
    end_at: Optional[datetime] = Field(default=None)
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    keywords: str = Field(default="[]")  # JSON 문자열로 저장
    reference_urls: str = Field(default="[]")  # JSON 문자열로 저장
    channels: str = Field(default="[]")  # JSON 문자열로 저장


class Campaign(CampaignBase, TimestampMixin, table=True):
    """캠페인 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    
    # 관계
    client: Client = Relationship(back_populates="campaigns")
    copy_variants: List["CopyVariant"] = Relationship(back_populates="campaign")
    outreach: List["Outreach"] = Relationship(back_populates="campaign")
    deliverables: List["Deliverable"] = Relationship(back_populates="campaign")
    
    @property
    def keywords_list(self) -> List[str]:
        """키워드 리스트 반환"""
        return json.loads(self.keywords) if self.keywords else []
    
    @property
    def reference_urls_list(self) -> List[str]:
        """참고 URL 리스트 반환"""
        return json.loads(self.reference_urls) if self.reference_urls else []
    
    @property
    def channels_list(self) -> List[str]:
        """채널 리스트 반환"""
        return json.loads(self.channels) if self.channels else []


class CampaignCreate(CampaignBase):
    """캠페인 생성 모델"""
    client_id: int


class CampaignRead(CampaignBase):
    """캠페인 조회 모델"""
    id: int
    client_id: int
    created_at: datetime
    updated_at: Optional[datetime]


# 문구 생성 결과
class CopyVariantBase(SQLModel):
    """문구 변형 기본 모델"""
    channel: Platform
    tone: str = Field(max_length=50)  # 톤앤매너
    length: int = Field(ge=0)  # 문구 길이
    text: str = Field(max_length=5000)  # 생성된 문구
    score: Optional[float] = Field(default=None, ge=0, le=1)  # 품질 점수
    approved: bool = Field(default=False)  # 승인 여부


class CopyVariant(CopyVariantBase, TimestampMixin, table=True):
    """문구 변형 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    
    # 관계
    campaign: Campaign = Relationship(back_populates="copy_variants")


class CopyVariantCreate(CopyVariantBase):
    """문구 변형 생성 모델"""
    campaign_id: int


class CopyVariantRead(CopyVariantBase):
    """문구 변형 조회 모델"""
    id: int
    campaign_id: int
    created_at: datetime


# 크리에이터 (인플루언서)
class CreatorBase(SQLModel):
    """크리에이터 기본 모델"""
    platform: Platform
    handle: str = Field(max_length=100)  # 계정명
    category: str = Field(max_length=50)  # 카테고리
    followers: Optional[int] = Field(default=None, ge=0)  # 팔로워 수
    engagement_rate: Optional[float] = Field(default=None, ge=0, le=1)  # 참여율
    email: Optional[str] = Field(default=None, max_length=100)
    dm_url: Optional[str] = Field(default=None, max_length=200)  # DM 링크
    active_at: Optional[datetime] = Field(default=None)  # 마지막 활동일
    notes: Optional[str] = Field(default=None, max_length=500)  # 메모


class Creator(CreatorBase, TimestampMixin, table=True):
    """크리에이터 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 관계
    outreach: List["Outreach"] = Relationship(back_populates="creator")
    deliverables: List["Deliverable"] = Relationship(back_populates="creator")


class CreatorCreate(CreatorBase):
    """크리에이터 생성 모델"""
    pass


class CreatorRead(CreatorBase):
    """크리에이터 조회 모델"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


# 연락 이력
class OutreachBase(SQLModel):
    """연락 이력 기본 모델"""
    channel: str = Field(max_length=20)  # email, dm
    method: str = Field(max_length=20)  # 연락 방법
    status: OutreachStatus = Field(default=OutreachStatus.PENDING)
    last_event_at: Optional[datetime] = Field(default=None)
    message_template_id: Optional[int] = Field(default=None)
    response_text: Optional[str] = Field(default=None, max_length=1000)


class Outreach(OutreachBase, TimestampMixin, table=True):
    """연락 이력 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    creator_id: int = Field(foreign_key="creator.id")
    
    # 관계
    campaign: Campaign = Relationship(back_populates="outreach")
    creator: Creator = Relationship(back_populates="outreach")


class OutreachCreate(OutreachBase):
    """연락 이력 생성 모델"""
    campaign_id: int
    creator_id: int


class OutreachRead(OutreachBase):
    """연락 이력 조회 모델"""
    id: int
    campaign_id: int
    creator_id: int
    created_at: datetime


# 게시물 및 성과
class DeliverableBase(SQLModel):
    """게시물 기본 모델"""
    url: str = Field(max_length=500)  # 게시물 URL
    posted_at: Optional[datetime] = Field(default=None)
    metrics_json: Optional[str] = Field(default=None)  # JSON 형태의 메트릭


class Deliverable(DeliverableBase, TimestampMixin, table=True):
    """게시물 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    campaign_id: int = Field(foreign_key="campaign.id")
    creator_id: int = Field(foreign_key="creator.id")
    
    # 관계
    campaign: Campaign = Relationship(back_populates="deliverables")
    creator: Creator = Relationship(back_populates="deliverables")
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """메트릭 딕셔너리 반환"""
        return json.loads(self.metrics_json) if self.metrics_json else {}


class DeliverableCreate(DeliverableBase):
    """게시물 생성 모델"""
    campaign_id: int
    creator_id: int


class DeliverableRead(DeliverableBase):
    """게시물 조회 모델"""
    id: int
    campaign_id: int
    creator_id: int
    created_at: datetime


# 이벤트 로그
class EventBase(SQLModel):
    """이벤트 기본 모델"""
    type: str = Field(max_length=50)  # 이벤트 타입
    payload_json: str = Field(default="{}")  # JSON 페이로드


class Event(EventBase, TimestampMixin, table=True):
    """이벤트 로그 테이블"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    @property
    def payload(self) -> Dict[str, Any]:
        """페이로드 딕셔너리 반환"""
        return json.loads(self.payload_json) if self.payload_json else {}


class EventCreate(EventBase):
    """이벤트 생성 모델"""
    pass


class EventRead(EventBase):
    """이벤트 조회 모델"""
    id: int
    created_at: datetime