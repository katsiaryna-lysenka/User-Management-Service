import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel
from pathlib import Path
from sqlalchemy import MetaData
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv(".env")

# Определение путей к приватному и публичному ключам JWT
BASE_DIR = Path(__file__).parent.parent
private_key_path = BASE_DIR / "certs" / "jwt-private.pem"
public_key_path = BASE_DIR / "certs" / "jwt-public.pem"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


# Определение настроек для JWT
class AuthJWT(BaseModel):
    private_key_path: Path = private_key_path
    public_key_path: Path = public_key_path
    algorithms: str = "RS256"
    access_token_expire_minutes: int = 180
    refresh_token_expire_days: int = 2
    reset_token_expire_days: int = 1

    class Config:
        from_attributes = True


# Определение настроек приложения
class Settings(BaseModel):
    # db_url: str = f"postgresql+asyncpg://postgres:12345@postgresql:5432/postgres"
    db_url: str = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    db_echo: bool = True
    # db_echo: bool = False

    auth_jwt: AuthJWT = AuthJWT()
    rabbitmq_host: str = "rabbitmq-container"


settings = Settings()

# Создание асинхронного соединения с базой данных
engine = create_async_engine(settings.db_url, echo=settings.db_echo, future=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Создание метаданных для базы данных
metadata = MetaData()

# Создание базового класса для сессий
Base = declarative_base()


# Определение функции для получения асинхронной сессии с базой данных
async def get_db():
    db = None
    try:
        async with SessionLocal() as db:
            yield db
    finally:
        if db is not None:
            await db.close()
