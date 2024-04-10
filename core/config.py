from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, ClassVar

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_session
from sqlalchemy.ext.declarative import declarative_base
import jwt
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithms: str = "RS256"
    # access_token_expire_minutes: int = 15
    access_token_expire_minutes: int = 180
    refresh_token_expire_days: int = 2
    reset_token_expire_days: int = 1

    class Config:
        from_attributes = True


class Settings(BaseSettings):
    db_url: str = f"postgresql+asyncpg://postgres:12345@postgresql:5432/postgres"

    # db_echo: bool = False
    db_echo: bool = True

    auth_jwt: AuthJWT = AuthJWT()
    # RABBITMQ_HOST: ClassVar[int] = 15672
    RABBITMQ_HOST: ClassVar[str] = "rabbitmq-container"


async def get_db():
    db = None
    try:
        async with SessionLocal() as db:
            yield db
    finally:
        if db is not None:
            await db.close()


engine = create_async_engine(Settings().db_url, echo=Settings().db_echo, future=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


Base = declarative_base()
settings = Settings()
auth_jwt = AuthJWT()
