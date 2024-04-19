import os
from typing import ClassVar

from sqlalchemy.orm import declarative_base

from pydantic import BaseModel
from pathlib import Path
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv(".env")

BASE_DIR = Path(__file__).parent.parent
private_key_path = BASE_DIR / "certs" / "jwt-private.pem"
public_key_path = BASE_DIR / "certs" / "jwt-public.pem"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


AWS_SECRET_KEY_ID = os.getenv("AWS_SECRET_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BASE_URL = os.getenv("S3_BASE_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
LOCALSTACK_HOST = os.getenv("LOCALSTACK_HOST")


class AuthJWT(BaseModel):
    private_key_path: Path = private_key_path
    public_key_path: Path = public_key_path

    algorithms: ClassVar[str] = os.getenv("ALGORITHMS")
    access_token_expire_minutes: ClassVar[int] = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    refresh_token_expire_days: ClassVar[int] = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
    )
    reset_token_expire_days: ClassVar[int] = int(os.getenv("RESET_TOKEN_EXPIRE_DAYS"))

    class Config:
        from_attributes = True


class Settings(BaseModel):
    db_url: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    db_echo: bool = True
    # db_echo: bool = False

    auth_jwt: AuthJWT = AuthJWT()
    rabbitmq_host: str = "rabbitmq-container"


settings = Settings()

# Creating Metadata for a Database
metadata = MetaData()

# Creating a base class for sessions
Base = declarative_base()
