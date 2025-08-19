"""
클라이언트(광고주) 관리 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from database.database import get_session
from database.models import (
    Client, ClientCreate, ClientRead
)

router = APIRouter()


@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    session: Session = Depends(get_session)
):
    """새 클라이언트 등록"""
    
    # 이메일 중복 확인
    existing = session.exec(
        select(Client).where(Client.contact_email == client.contact_email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 클라이언트 생성
    db_client = Client.model_validate(client)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    
    return db_client


@router.get("/", response_model=List[ClientRead])
async def get_clients(
    industry: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """클라이언트 목록 조회"""
    
    query = select(Client)
    
    # 업종 필터
    if industry:
        query = query.where(Client.industry.ilike(f"%{industry}%"))
    
    # 페이지네이션
    query = query.offset(skip).limit(limit)
    
    clients = session.exec(query).all()
    return clients


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: int,
    session: Session = Depends(get_session)
):
    """특정 클라이언트 조회"""
    
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클라이언트를 찾을 수 없습니다."
        )
    
    return client


@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int,
    client_update: ClientCreate,
    session: Session = Depends(get_session)
):
    """클라이언트 정보 수정"""
    
    db_client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클라이언트를 찾을 수 없습니다."
        )
    
    # 업데이트
    client_data = client_update.model_dump(exclude_unset=True)
    for field, value in client_data.items():
        setattr(db_client, field, value)
    
    db_client.updated_at = datetime.utcnow()
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    session: Session = Depends(get_session)
):
    """클라이언트 삭제"""
    
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클라이언트를 찾을 수 없습니다."
        )
    
    session.delete(client)
    session.commit()


@router.get("/{client_id}/campaigns")
async def get_client_campaigns(
    client_id: int,
    session: Session = Depends(get_session)
):
    """클라이언트의 캠페인 목록"""
    
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클라이언트를 찾을 수 없습니다."
        )
    
    return {
        "client_id": client_id,
        "client_name": client.name,
        "campaigns": client.campaigns
    }


@router.get("/industries/", response_model=List[str])
async def get_industries(
    session: Session = Depends(get_session)
):
    """업종 목록 조회"""
    
    query = select(Client.industry).distinct()
    industries = session.exec(query).all()
    return [industry for industry in industries if industry]