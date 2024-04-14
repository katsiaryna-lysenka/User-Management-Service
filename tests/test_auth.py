# import httpx
# import pytest
# from httpx import AsyncClient
# from main import app
# from src.auth.views import create_user
# from src.users.schemas import CreateUser
# from src.users.views import db, session
# from starlette.testclient import TestClient
#
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
#
#
# @pytest.fixture(scope="module")
# def test_client():
#     with TestClient(app) as client:
#         yield client
#
#
# @pytest.fixture(scope="module")
# async def test_user():
#     # Создаем экземпляр объекта CreateUser из словаря user_data
#     user_data = {
#         "name": "vvv",
#         "surname": "vvv",
#         "username": "vvv",
#         "password": "111",
#         "phone_number": "111",
#         "email": "vvv@example.com",
#         "role": "admin",
#         "group": "Cat",
#         "is_blocked": False,
#     }
#     user = CreateUser(**user_data)
#
#     # Вызываем функцию для создания пользователя, передавая объект CreateUser
#     await create_user(user)
#
#     yield user
#
#
# @pytest.mark.asyncio
# async def test_login_endpoint(test_client, test_user):
#     # Подготовка данных для запроса
#     login_data = {
#         "username": "vvv",
#         "email": "",
#         "phone_number": "111",
#         "password": "111"
#     }
#
#     # Вывод данных перед отправкой запроса
#     print(f"Отправленные данные: {login_data}")
#
#     # Отправка POST запроса на эндпоинт /auth/login
#     response = test_client.post("/auth/login", json=login_data)
#
#     # Вывод ответа на запрос
#     print(f"Полученный ответ: {response.text}")
#     assert response.status_code == 200
#
#     # Получение данных JSON из ответа
#     data = response.json()
#     assert "access_token" in data
#     assert "refresh_token" in data
