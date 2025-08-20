"""
포스팅 제안 메일 발송 API
기업이 선택한 블로거에게 포스팅 제안 메일을 발송하는 시스템
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from database.database import get_session
from database.models import (
    Blogger, Campaign, Outreach, OutreachCreate, OutreachRead,
    OutreachStatus
)
from services.email_service import EmailService
from services.proposal_generator import ProposalGeneratorService

router = APIRouter()


class ProposalRequest(BaseModel):
    """포스팅 제안 요청 모델"""
    campaign_id: int
    blogger_ids: List[int]
    custom_message: Optional[str] = None
    collaboration_type: str = "sponsored_post"  # sponsored_post, product_review, etc.
    compensation_type: str = "monetary"  # monetary, product, both
    compensation_amount: Optional[str] = None
    deadline: Optional[datetime] = None
    requirements: Optional[List[str]] = None


class ProposalTemplate(BaseModel):
    """포스팅 제안 템플릿 모델"""
    subject: str
    content: str
    blogger_name: str
    blog_name: str
    company_name: str
    product_name: str


@router.post("/send-proposals")
async def send_posting_proposals(
    proposal_request: ProposalRequest,
    session: Session = Depends(get_session)
):
    """선택된 블로거들에게 포스팅 제안 메일 발송"""
    
    # 캠페인 확인
    campaign = session.get(Campaign, proposal_request.campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    # 블로거들 확인
    bloggers = []
    for blogger_id in proposal_request.blogger_ids:
        blogger = session.get(Blogger, blogger_id)
        if not blogger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"블로거 ID {blogger_id}를 찾을 수 없습니다."
            )
        if not blogger.email and not blogger.contact_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"블로거 '{blogger.blogger_name}'의 연락처 정보가 없습니다."
            )
        bloggers.append(blogger)
    
    # 제안 문구 생성 서비스
    proposal_service = ProposalGeneratorService()
    email_service = EmailService()
    
    sent_proposals = []
    failed_proposals = []
    
    for blogger in bloggers:
        try:
            # 개별 맞춤 제안 문구 생성
            proposal_template = await proposal_service.generate_proposal(
                campaign=campaign,
                blogger=blogger,
                custom_message=proposal_request.custom_message,
                collaboration_type=proposal_request.collaboration_type,
                compensation_type=proposal_request.compensation_type,
                compensation_amount=proposal_request.compensation_amount,
                deadline=proposal_request.deadline,
                requirements=proposal_request.requirements
            )
            
            # 메일 발송
            if blogger.email:
                email_sent = await email_service.send_proposal_email(
                    to_email=blogger.email,
                    subject=proposal_template.subject,
                    content=proposal_template.content,
                    blogger_name=blogger.blogger_name
                )
                
                if email_sent:
                    # 발송 이력 저장
                    outreach = Outreach(
                        campaign_id=proposal_request.campaign_id,
                        blogger_id=blogger.id,
                        channel="email",
                        method="proposal_email",
                        status=OutreachStatus.SENT,
                        last_event_at=datetime.utcnow()
                    )
                    session.add(outreach)
                    
                    sent_proposals.append({
                        "blogger_id": blogger.id,
                        "blogger_name": blogger.blogger_name,
                        "email": blogger.email,
                        "status": "sent"
                    })
                else:
                    failed_proposals.append({
                        "blogger_id": blogger.id,
                        "blogger_name": blogger.blogger_name,
                        "error": "메일 발송 실패"
                    })
            else:
                # 이메일이 없는 경우 연락처 정보만 기록
                outreach = Outreach(
                    campaign_id=proposal_request.campaign_id,
                    blogger_id=blogger.id,
                    channel="manual",
                    method="contact_info",
                    status=OutreachStatus.PENDING,
                    last_event_at=datetime.utcnow()
                )
                session.add(outreach)
                
                sent_proposals.append({
                    "blogger_id": blogger.id,
                    "blogger_name": blogger.blogger_name,
                    "contact_info": blogger.contact_info,
                    "status": "manual_contact_required"
                })
        
        except Exception as e:
            failed_proposals.append({
                "blogger_id": blogger.id,
                "blogger_name": blogger.blogger_name,
                "error": str(e)
            })
    
    session.commit()
    
    return {
        "message": f"{len(sent_proposals)}개의 제안이 발송되었습니다.",
        "campaign_id": proposal_request.campaign_id,
        "sent_count": len(sent_proposals),
        "failed_count": len(failed_proposals),
        "sent_proposals": sent_proposals,
        "failed_proposals": failed_proposals
    }


@router.get("/proposals/{campaign_id}", response_model=List[OutreachRead])
async def get_campaign_proposals(
    campaign_id: int,
    status: Optional[OutreachStatus] = None,
    session: Session = Depends(get_session)
):
    """캠페인의 포스팅 제안 목록 조회"""
    
    query = select(Outreach).where(Outreach.campaign_id == campaign_id)
    
    if status:
        query = query.where(Outreach.status == status)
    
    query = query.order_by(Outreach.created_at.desc())
    
    proposals = session.exec(query).all()
    return proposals


@router.patch("/proposals/{outreach_id}/status")
async def update_proposal_status(
    outreach_id: int,
    new_status: OutreachStatus,
    response_text: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """포스팅 제안 상태 업데이트"""
    
    outreach = session.get(Outreach, outreach_id)
    if not outreach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제안 이력을 찾을 수 없습니다."
        )
    
    outreach.status = new_status
    outreach.last_event_at = datetime.utcnow()
    
    if response_text:
        outreach.response_text = response_text
    
    session.add(outreach)
    session.commit()
    
    return {"message": f"제안 상태가 {new_status.value}로 변경되었습니다."}


@router.get("/templates/preview")
async def preview_proposal_template(
    campaign_id: int,
    blogger_id: int,
    collaboration_type: str = "sponsored_post",
    compensation_type: str = "monetary",
    session: Session = Depends(get_session)
):
    """포스팅 제안 템플릿 미리보기"""
    
    # 캠페인과 블로거 확인
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="캠페인을 찾을 수 없습니다."
        )
    
    blogger = session.get(Blogger, blogger_id)
    if not blogger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="블로거를 찾을 수 없습니다."
        )
    
    # 제안 문구 생성
    proposal_service = ProposalGeneratorService()
    
    try:
        proposal_template = await proposal_service.generate_proposal(
            campaign=campaign,
            blogger=blogger,
            collaboration_type=collaboration_type,
            compensation_type=compensation_type
        )
        
        return {
            "subject": proposal_template.subject,
            "content": proposal_template.content,
            "blogger_info": {
                "name": blogger.blogger_name,
                "blog_name": blogger.blog_name,
                "category": blogger.category,
                "post_count": blogger.post_count
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"템플릿 생성 실패: {str(e)}"
        )


@router.get("/stats/{campaign_id}")
async def get_outreach_stats(
    campaign_id: int,
    session: Session = Depends(get_session)
):
    """캠페인의 아웃리치 통계"""
    
    outreach_list = session.exec(
        select(Outreach).where(Outreach.campaign_id == campaign_id)
    ).all()
    
    stats = {
        "total_sent": len(outreach_list),
        "pending": len([o for o in outreach_list if o.status == OutreachStatus.PENDING]),
        "sent": len([o for o in outreach_list if o.status == OutreachStatus.SENT]),
        "replied": len([o for o in outreach_list if o.status == OutreachStatus.REPLIED]),
        "accepted": len([o for o in outreach_list if o.status == OutreachStatus.ACCEPTED]),
        "rejected": len([o for o in outreach_list if o.status == OutreachStatus.REJECTED]),
    }
    
    # 응답률 계산
    if stats["sent"] > 0:
        stats["response_rate"] = round((stats["replied"] / stats["sent"]) * 100, 2)
        stats["acceptance_rate"] = round((stats["accepted"] / stats["sent"]) * 100, 2)
    else:
        stats["response_rate"] = 0
        stats["acceptance_rate"] = 0
    
    return stats