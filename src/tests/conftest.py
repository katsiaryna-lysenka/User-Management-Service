from typing import AsyncGenerator

import pytest
from src.infrastructure.models import User
from src.domain.auth.utils import encode_jwt
from src.infrastructure.database.create_db import get_async_session
from main import app
from starlette.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
from src.domain.users.views import session
from src.domain.users.crud import CRUD

# Загрузка переменных окружения из файла .env
config = Config(".env")
DB_HOST_TEST = config("DB_HOST_TEST")
DB_PORT_TEST = config("DB_PORT_TEST")
DB_NAME_TEST = config("DB_NAME_TEST")
DB_USER_TEST = config("DB_USER_TEST")
DB_PASS_TEST = config("DB_PASS_TEST")

# Формирование URL для подключения к тестовой базе данных
DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"

# Создание асинхронного соединения с тестовой базой данных
engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)

# Создание клиента для тестирования
client = AsyncClient()

db = CRUD()


# Переопределение зависимостей для получения асинхронной сессии в тестах
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session")
def access_token():
    def _access_token(user_id):
        return encode_jwt({"user_id": str(user_id)})

    return _access_token


@pytest.fixture(scope="module")
async def test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "30012843-1d0f-4ee0-b17f-a99f70e0aeec",
        "name": "vvv",
        "surname": "vvv",
        "username": "vvv",
        "password": "11144444",
        "phone_number": "111",
        "email": "vvv@example.com",
        "role": "admin",
        "group": "Cat",
        "is_blocked": False,
    }
    user = User(**user_data)
    print("user:", user)
    await db.add(session, user)
    print("user:", user)

    # Выводим список всех пользователей для проверки
    users = await db.get_all(session)
    print("All users:", users)

    return user


@pytest.fixture(scope="module")
async def second_test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "c0b266a1-f393-471a-9e68-83c38fc4270d",
        "name": "helen",
        "surname": "lelen",
        "username": "helen_len_len",
        "password": "33388888",
        "phone_number": "295555555",
        "email": "helen@gmail.com",
        "role": "admin",
        "group": "Cat",
        "is_blocked": False,
    }
    user = User(**user_data)
    print("user:", user)
    await db.add(session, user)
    print("user:", user)

    # Выводим список всех пользователей для проверки
    users = await db.get_all(session)
    print("All users:", users)

    return user


@pytest.fixture(scope="module")
async def third_test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "e39f3f3c-39d3-4914-875f-7301f5e4c791",
        "name": "katsiaryna",
        "surname": "lysenka",
        "username": "katsiaryna.na",
        "password": "44477777",
        "phone_number": "332222222",
        "email": "katsiaryna@gmail.com",
        "role": "user",
        "group": "Cat",
        "is_blocked": False,
    }
    user = User(**user_data)
    print("user:", user)
    await db.add(session, user)
    print("user:", user)

    # Выводим список всех пользователей для проверки
    users = await db.get_all(session)
    print("All users:", users)

    return user


@pytest.fixture(scope="module")
async def fourth_test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "3e1ab104-648c-458f-968f-dbfcc57c92f9",
        "name": "valery",
        "surname": "intol",
        "username": "valery.y.y",
        "password": "55588888",
        "phone_number": "298888888",
        "email": "valery@gmail.com",
        "role": "user",
        "group": "Cat",
        "is_blocked": False,
    }
    user = User(**user_data)
    print("user:", user)
    await db.add(session, user)
    print("user:", user)

    # Выводим список всех пользователей для проверки
    users = await db.get_all(session)
    print("All users:", users)

    return user


@pytest.fixture(scope="module")
async def fifth_test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "c8285014-a740-4d47-b3b1-42a5aeffb5f1",
        "name": "ann",
        "surname": "none",
        "username": "ann.n.n",
        "password": "444555555",
        "phone_number": "298887766",
        "email": "---",
        "role": "moderator",
        "group": "Cat",
        "is_blocked": False,
    }
    user = User(**user_data)
    await db.add(session, user)

    return user


@pytest.fixture(scope="module")
async def six_test_user():
    # Создаем нового пользователя в базе данных
    user_data = {
        "id": "1af54f6d-376e-4c1b-aef4-c3d3b27745c6",
        "name": "katya",
        "surname": "lekatya",
        "username": "katya.a.a",
        "password": "88866666",
        "phone_number": "336666666",
        "email": "katya@example.com",
        "role": "moderator",
        "group": "Dog",
        "is_blocked": False,
    }
    user = User(**user_data)
    await db.add(session, user)

    return user
