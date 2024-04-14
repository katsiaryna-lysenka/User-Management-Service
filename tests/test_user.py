import httpx
import pytest
from sqlalchemy.ext.asyncio import async_session, async_sessionmaker, AsyncSession

from src.auth.utils import encode_jwt, decode_jwt
from src.auth.views import session
from src.core.config import metadata
from src.core.models import User
from src.database.create_db import engine
from src.users.schemas import UserInfo
from src.users.crud import CRUD


db = CRUD()


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


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
        "password": "111",
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


@pytest.mark.asyncio
async def test_user_info(access_token, test_user):
    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = access_token(user_id)
    print("Access token:", token)  # Добавляем вывод токена
    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    headers = {"accept": "application/json"}
    params = {"access_token": token}
    url = base_url + endpoint
    print("Request URL:", url)  # Добавляем вывод URL-адреса запроса

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers, params=params)
        print("Response:", response.text)  # Добавляем вывод ответа

        assert response.status_code == 200
        # Проверяем наличие данных в ответе сервера
        assert "id" in response.json()
        assert "name" in response.json()
        assert "surname" in response.json()
        assert "username" in response.json()
        assert "email" in response.json()
        assert "phone_number" in response.json()
        assert "role" in response.json()
        assert "group" in response.json()

        # Проверяем, что полученная информация соответствует модели UserInfo
        user_info_instance = UserInfo(**response.json())
        assert isinstance(user_info_instance, UserInfo)


@pytest.mark.asyncio
async def test_update_user(test_user):
    # Создаем тестовые данные для обновления пользователя
    updated_user_data = {
        "name": "kkk",
        "surname": "kkk",
        "username": "kkk",
        "password": "222",
        "phone_number": "222",
        "email": "kkk@example.com",
        "role": "user",
        "group": "Dog",
        "is_blocked": False,
    }

    # Создаем базу данных
    await create_database()

    # Выполняем ручную аутентификацию пользователя
    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = encode_jwt({"user_id": user_id})

    # Вызываем эндпоинт для обновления пользователя с использованием предварительно созданного пользователя и токена доступа
    response = await db.update(async_sessionmaker[AsyncSession], user_id, updated_user_data)

    # Проверяем, что ответ содержит ожидаемые данные пользователя
    assert response.name == updated_user_data["name"]
    assert response.surname == updated_user_data["surname"]
    assert response.username == updated_user_data["username"]
    assert response.phone_number == updated_user_data["phone_number"]
    assert response.email == updated_user_data["email"]
    assert response.role == updated_user_data["role"]
    assert response.group == updated_user_data["group"]
    assert response.is_blocked == updated_user_data["is_blocked"]