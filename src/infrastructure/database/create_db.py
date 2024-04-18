from sqlalchemy import NullPool
from sqlalchemy.orm import sessionmaker

from src.infrastructure.models import Base

from src.config import settings
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.domain.users.crud import db_url

engine = create_async_engine(
    db_url, echo=settings.db_echo, future=True, poolclass=NullPool
)


async def create_db():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


asyncio.run(create_db())
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# Определение функции для получения асинхронной сессии с базой данных
async def get_db():
    db = None
    try:
        async with SessionLocal() as db:
            yield db
    finally:
        if db is not None:
            await db.close()
