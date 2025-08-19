#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

import sys
import os

# 백엔드 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db
from models import Client, Campaign, CopyVariant, Creator, OutreachRecord, EmailTemplate

def init_database():
    """데이터베이스 테이블 생성 및 초기 데이터 삽입"""
    with app.app_context():
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블이 생성되었습니다.")
        
        # 샘플 데이터 생성 (개발용)
        create_sample_data()

def create_sample_data():
    """개발용 샘플 데이터 생성"""
    try:
        # 샘플 클라이언트 생성
        if not Client.query.first():
            sample_client = Client(
                name="테스트 클라이언트",
                email="test@example.com",
                company="테스트 회사",
                role="admin"
            )
            db.session.add(sample_client)
            db.session.commit()
            print("✅ 샘플 클라이언트가 생성되었습니다.")
            
            # 기본 이메일 템플릿 생성
            default_template = EmailTemplate(
                name="기본 협업 제안 템플릿",
                subject="[{{company_name}}] {{creator_name}}님과의 협업 제안",
                content="""안녕하세요 {{creator_name}}님,

{{company_name}}의 마케팅 담당자입니다.

{{creator_name}}님의 {{platform}} 계정을 보고 연락드립니다. 
저희 {{product_name}} 제품과 관련하여 협업을 제안드리고 싶습니다.

제품 정보:
{{product_info}}

협업 내용:
- 제품 체험 후 솔직한 리뷰
- {{channel}} 채널에 콘텐츠 게시
- 상호 협의 하에 협업비 지급

관심이 있으시다면 회신 부탁드립니다.

감사합니다.

{{company_name}} 마케팅팀
{{contact_email}}""",
                variables={
                    "creator_name": "크리에이터 이름",
                    "company_name": "회사명",
                    "product_name": "제품명",
                    "product_info": "제품 정보",
                    "platform": "플랫폼",
                    "channel": "채널",
                    "contact_email": "연락처 이메일"
                },
                client_id=sample_client.id,
                is_default=True,
                category="협업제안"
            )
            db.session.add(default_template)
            db.session.commit()
            print("✅ 기본 이메일 템플릿이 생성되었습니다.")
        
        # 샘플 크리에이터 생성
        if not Creator.query.first():
            sample_creators = [
                Creator(
                    name="김뷰티",
                    email="beauty.kim@example.com",
                    platform="instagram",
                    username="beauty_kim_official",
                    display_name="뷰티킴",
                    followers_count=15000,
                    engagement_rate=4.2,
                    category="뷰티",
                    bio="뷰티 인플루언서 | 화장품 리뷰 | 협업 문의 DM",
                    location="서울",
                    language="ko",
                    is_verified=False,
                    avg_likes=800,
                    avg_comments=45,
                    collaboration_rate=300000.0
                ),
                Creator(
                    name="테크리뷰어",
                    email="tech.reviewer@example.com",
                    platform="youtube",
                    username="tech_reviewer_kr",
                    display_name="테크리뷰어",
                    followers_count=85000,
                    engagement_rate=3.8,
                    category="테크",
                    bio="IT 제품 리뷰 전문 | 주 2회 업로드",
                    location="경기도",
                    language="ko",
                    is_verified=True,
                    avg_likes=2500,
                    avg_comments=180,
                    collaboration_rate=800000.0
                ),
                Creator(
                    name="푸드블로거",
                    email="food.blogger@example.com",
                    platform="blog",
                    username="food_lover_blog",
                    display_name="맛집탐험가",
                    followers_count=25000,
                    engagement_rate=5.1,
                    category="푸드",
                    bio="전국 맛집 탐방 | 솔직한 맛집 리뷰",
                    location="부산",
                    language="ko",
                    is_verified=False,
                    avg_likes=450,
                    avg_comments=25,
                    collaboration_rate=200000.0
                )
            ]
            
            for creator in sample_creators:
                db.session.add(creator)
            
            db.session.commit()
            print("✅ 샘플 크리에이터가 생성되었습니다.")
            
    except Exception as e:
        print(f"❌ 샘플 데이터 생성 중 오류 발생: {e}")
        db.session.rollback()

def reset_database():
    """데이터베이스 초기화 (모든 데이터 삭제)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ 데이터베이스가 초기화되었습니다.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='데이터베이스 관리 스크립트')
    parser.add_argument('--reset', action='store_true', help='데이터베이스 초기화')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()