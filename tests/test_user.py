import httpx
import pytest
import asyncio

from src.auth.utils import encode_jwt
from src.auth.views import session
from src.core.models import User
from src.users.schemas import UserInfo
from src.users.crud import CRUD


db = CRUD()


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