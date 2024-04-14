from typing import AsyncGenerator
from src.database.create_db import get_async_session
from main import app
from starlette.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

# Загрузка переменных окружения из файла .env
config = Config('.env')
DB_HOST_TEST = config('DB_HOST_TEST')
DB_PORT_TEST = config('DB_PORT_TEST')
DB_NAME_TEST = config('DB_NAME_TEST')
DB_USER_TEST = config('DB_USER_TEST')
DB_PASS_TEST = config('DB_PASS_TEST')

# Формирование URL для подключения к тестовой базе данных
DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

# Создание асинхронного соединения с тестовой базой данных
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)

# Создание клиента для тестирования
client = AsyncClient()


# Переопределение зависимостей для получения асинхронной сессии в тестах
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


# Переопределение зависимостей для получения асинхронной сессии в тестах
async def override_get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


