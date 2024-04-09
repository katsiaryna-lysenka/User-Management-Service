from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
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

    class Config:
        from_attributes = True


class Settings(BaseSettings):
    db_url: str = f"postgresql+asyncpg://postgres:12345@postgresql:5432/postgres"

    # db_echo: bool = False
    db_echo: bool = True

    auth_jwt: AuthJWT = AuthJWT()


engine = create_async_engine(Settings().db_url, echo=Settings().db_echo, future=True)

Base = declarative_base()
settings = Settings()
auth_jwt = AuthJWT()


# def create_access_token(user_id: str) -> str:
#     """
#     Создаю токен доступа для пользователя
#     """
#     expire = datetime.utcnow() + timedelta(minutes=auth_jwt.access_token_expire_minutes)
#     to_encode = {"user_id": user_id, "exp": expire}
#     encoded_jwt = jwt.encode(to_encode, auth_jwt.private_key_path, algorithm=auth_jwt.algorithms)
#     return encoded_jwt
#
#
# def create_refresh_token(user_id: str) -> str:
#     """
#     Создаю токен обновления для пользователя
#     """
#     expire = datetime.utcnow() + timedelta(days=auth_jwt.refresh_token_expire_days)
#     to_encode = {"user_id": user_id, "exp": expire}
#     encoded_jwt = jwt.encode(to_encode, auth_jwt.private_key_path, algorithm=auth_jwt.algorithms)
#     return encoded_jwt
