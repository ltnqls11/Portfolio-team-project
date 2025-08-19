"""
FastAPI 메인 애플리케이션
온라인 마케팅 연계 플랫폼의 백엔드 API 서버
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional
import logging

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 라이프사이클 이벤트
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시
    logger.info("🚀 애플리케이션 시작")
    
    # 데이터베이스 테이블 생성
    try:
        create_db_and_tables()
        logger.info("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}")
    
    yield
    
    # 종료 시
    logger.info("🛑 애플리케이션 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="온라인 마케팅 연계 플랫폼 API",
    description="기업과 인플루언서를 연결하고 홍보 문구를 자동 생성하는 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 개발 서버
        "http://localhost:5173",  # Vite 개발 서버
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우트
@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "온라인 마케팅 연계 플랫폼 API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "marketing-platform-api"
    }

# API 라우터 등록
from api.campaigns import router as campaigns_router
from api.creators import router as creators_router
from api.copy_generation import router as copy_router
from api.clients import router as clients_router
from api.crawling import router as crawling_router
from database.database import create_db_and_tables

app.include_router(campaigns_router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(creators_router, prefix="/api/creators", tags=["Creators"])
app.include_router(copy_router, prefix="/api/copy", tags=["Copy Generation"])
app.include_router(clients_router, prefix="/api/clients", tags=["Clients"])
app.include_router(crawling_router, prefix="/api/crawling", tags=["Crawling"])

# 에러 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """일반 예외 처리"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500
            }
        }
    )

if __name__ == "__main__":
    # 개발 서버 실행
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # 개발 환경에서만 사용
        log_level="info"
    )
