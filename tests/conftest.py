from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

from scr.core.config import (
    metadata,
    DB_USER_TEST,
    DB_PASS_TEST,
    DB_HOST_TEST,
    DB_PORT_TEST,
    DB_NAME_TEST,
)
from scr.database.create_db import get_async_session
from main import app

# Проверка, что все переменные окружения установлены
if None in (DB_HOST_TEST, DB_PORT_TEST, DB_NAME_TEST, DB_USER_TEST, DB_PASS_TEST):
    raise ValueError("One or more database environment variables are not set")


# DATABASE
DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)
metadata.bind = engine_test

client = TestClient(app)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session
