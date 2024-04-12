import pytest
from httpx import AsyncClient

from main import app
from scr.auth.utils import encode_jwt
from scr.core.models.role import State
from scr.users.schemas import UserInfo

from tests.conftest import async_session_maker
from scr.users.crud import CRUD
from sqlalchemy import insert, select

db = CRUD()


@pytest.fixture(scope="session")
def access_token():
    payload = {"id": "f9e17b10-670d-4060-81f9-39815d519430"}
    access_token = encode_jwt(payload)
    return access_token


def test_example(access_token):
    # В этом примере мы просто печатаем токен
    print(access_token)


@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.asyncio
async def test_user_info(client, access_token):
    async with client:
        response = await client.request(
            "GET", "/auth/me/", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200

        # Проверяем, что в ответе содержится корректная информация о пользователе
        user_info = response.json()
        assert "id" in user_info
        assert "username" in user_info
        assert "email" in user_info

        # Проверяем, что полученная информация соответствует модели UserInfo
        user_info_instance = UserInfo(**user_info)
        assert isinstance(user_info_instance, UserInfo)
