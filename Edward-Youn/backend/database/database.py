"""
데이터베이스 연결 및 설정
"""

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@localhost:5432/marketing_platform"
)

# 개발 환경에서는 SQLite 사용
if os.getenv("ENVIRONMENT") == "development":
    DATABASE_URL = "sqlite:///./marketing_platform.db"

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "true" else False,
    # SQLite 사용 시 필요한 설정
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
)


def create_db_and_tables():
    """데이터베이스와 테이블 생성"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    with Session(engine) as session:
        yield session