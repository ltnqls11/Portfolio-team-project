from app import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON
import uuid

class Client(db.Model):
    """클라이언트/사용자 정보 모델"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    company = db.Column(db.String(255))
    role = db.Column(db.String(50), default='user')  # admin, user
    oauth_provider = db.Column(db.String(50))  # google, kakao 등
    oauth_id = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    campaigns = db.relationship('Campaign', backref='client', lazy=True)
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Campaign(db.Model):
    """캠페인 정보 모델"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    product_info = db.Column(db.Text)
    keywords = db.Column(db.Text)
    reference_links = db.Column(db.Text)
    target_audience = db.Column(db.Text)  # 타겟 오디언스 정보
    budget = db.Column(db.Float)  # 예산
    status = db.Column(db.String(50), default='draft')  # draft, active, completed, paused
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    scheduled_at = db.Column(db.DateTime)  # 예약 발송 시간
    completed_at = db.Column(db.DateTime)  # 완료 시간
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    copy_variants = db.relationship('CopyVariant', backref='campaign', lazy=True, cascade='all, delete-orphan')
    outreach_records = db.relationship('OutreachRecord', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'product_info': self.product_info,
            'keywords': self.keywords,
            'reference_links': self.reference_links,
            'target_audience': self.target_audience,
            'budget': self.budget,
            'status': self.status,
            'client_id': self.client_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'copy_variants_count': len(self.copy_variants) if self.copy_variants else 0,
            'outreach_count': len(self.outreach_records) if self.outreach_records else 0
        }

class CopyVariant(db.Model):
    """문구 변형 모델"""
    __tablename__ = 'copy_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(50), nullable=False)  # naver_blog, instagram_feed, youtube, tiktok
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(500))  # 제목 (블로그, 유튜브용)
    hashtags = db.Column(db.Text)  # 해시태그
    is_selected = db.Column(db.Boolean, default=False)
    ai_generated = db.Column(db.Boolean, default=True)  # AI 생성 여부
    generation_prompt = db.Column(db.Text)  # 생성에 사용된 프롬프트
    character_count = db.Column(db.Integer)  # 글자 수
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'channel': self.channel,
            'content': self.content,
            'title': self.title,
            'hashtags': self.hashtags,
            'is_selected': self.is_selected,
            'ai_generated': self.ai_generated,
            'character_count': self.character_count,
            'campaign_id': self.campaign_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Creator(db.Model):
    """인플루언서/크리에이터 정보 모델"""
    __tablename__ = 'creators'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    platform = db.Column(db.String(50), nullable=False)  # instagram, youtube, blog, tiktok
    username = db.Column(db.String(255))
    display_name = db.Column(db.String(255))  # 표시명
    followers_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    category = db.Column(db.String(100))
    bio = db.Column(db.Text)  # 프로필 설명
    profile_image_url = db.Column(db.String(500))  # 프로필 이미지 URL
    external_id = db.Column(db.String(255))  # 플랫폼별 고유 ID
    contact_info = db.Column(JSON)  # 연락처 정보
    profile_data = db.Column(JSON)  # 추가 프로필 데이터
    location = db.Column(db.String(255))  # 지역
    language = db.Column(db.String(50), default='ko')  # 주 사용 언어
    is_verified = db.Column(db.Boolean, default=False)  # 인증 계정 여부
    last_post_date = db.Column(db.DateTime)  # 마지막 게시물 날짜
    avg_likes = db.Column(db.Integer)  # 평균 좋아요 수
    avg_comments = db.Column(db.Integer)  # 평균 댓글 수
    collaboration_rate = db.Column(db.Float)  # 협업 단가
    is_active = db.Column(db.Boolean, default=True)  # 활성 상태
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    outreach_records = db.relationship('OutreachRecord', backref='creator', lazy=True)
    
    # 인덱스 설정
    __table_args__ = (
        db.Index('idx_creator_platform', 'platform'),
        db.Index('idx_creator_followers', 'followers_count'),
        db.Index('idx_creator_category', 'category'),
        db.Index('idx_creator_platform_external', 'platform', 'external_id'),
    )
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'platform': self.platform,
            'username': self.username,
            'display_name': self.display_name,
            'followers_count': self.followers_count,
            'engagement_rate': self.engagement_rate,
            'category': self.category,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'external_id': self.external_id,
            'location': self.location,
            'language': self.language,
            'is_verified': self.is_verified,
            'last_post_date': self.last_post_date.isoformat() if self.last_post_date else None,
            'avg_likes': self.avg_likes,
            'avg_comments': self.avg_comments,
            'collaboration_rate': self.collaboration_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EmailTemplate(db.Model):
    """이메일 템플릿 모델"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    variables = db.Column(JSON)  # 템플릿 변수 정의
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(100))  # 템플릿 카테고리
    language = db.Column(db.String(10), default='ko')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    client = db.relationship('Client', backref='email_templates')
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'content': self.content,
            'variables': self.variables,
            'client_id': self.client_id,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'category': self.category,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OutreachRecord(db.Model):
    """연락 기록 모델"""
    __tablename__ = 'outreach'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'))  # 사용된 템플릿
    email_address = db.Column(db.String(255), nullable=False)  # 실제 발송된 이메일 주소
    email_subject = db.Column(db.String(500))
    email_content = db.Column(db.Text)
    personalization_data = db.Column(JSON)  # 개인화 데이터
    status = db.Column(db.String(50), default='pending')  # pending, sent, failed, replied, bounced, opened
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)  # 이메일 열람 시간
    replied_at = db.Column(db.DateTime)  # 답장 시간
    error_message = db.Column(db.Text)
    response_data = db.Column(JSON)  # 답장 내용 등
    retry_count = db.Column(db.Integer, default=0)  # 재시도 횟수
    external_message_id = db.Column(db.String(255))  # 외부 서비스 메시지 ID
    delivery_status = db.Column(db.String(50))  # delivered, bounced, spam
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    template = db.relationship('EmailTemplate', backref='outreach_records')
    
    # 인덱스 설정
    __table_args__ = (
        db.Index('idx_outreach_campaign', 'campaign_id'),
        db.Index('idx_outreach_status', 'status'),
        db.Index('idx_outreach_sent_at', 'sent_at'),
    )
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'creator_id': self.creator_id,
            'template_id': self.template_id,
            'email_address': self.email_address,
            'email_subject': self.email_subject,
            'email_content': self.email_content,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'external_message_id': self.external_message_id,
            'delivery_status': self.delivery_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }