import pytest
import httpx


@pytest.mark.asyncio
async def test_create_user():
    user_data = {
        "id": "fb4e9d85-26cf-40ec-9660-c8fd7cfed8b9",
        "name": "nikol",
        "surname": "syt",
        "username": "nikol_l_l",
        "password": "999",
        "phone_number": "294444444",
        "email": "nikol@gmail.com",
        "role": "user",
        "group": "Dog",
        "is_blocked": False,
        "created_at": "2024-04-15T13:30:13.488Z",
        "modified_at": "2024-04-15T13:30:13.488Z",
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/signup"
    url = f"{base_url}{endpoint}"
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, json=user_data)

    assert response.status_code == 201  # Проверяем, что запрос выполнен успешно
    assert "id" in response.json()  # Проверяем, что в ответе есть поле "id"


@pytest.mark.asyncio
async def test_login_endpoint():
    # Параметры запроса
    data = {
        "username": "nikol_l_l",
        "email": "nikol@gmail.com",
        "phone_number": "",
        "password": "888",
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/login"
    url = f"{base_url}{endpoint}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Отправка запроса
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data=data)
    print("Response data:", response.text)

    # Проверки ответа
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@pytest.mark.asyncio
async def test_refresh_token_endpoint(access_token):
    # Получение токена из фикстуры
    token = access_token("fb4e9d85-26cf-40ec-9660-c8fd7cfed8b9")

    # Параметры запроса
    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/refresh-token"
    url = f"{base_url}{endpoint}"
    headers = {"accept": "application/json", "token": token}
    # Отправка запроса

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers)
    print("Response data:", response.text)

    # Проверки ответа
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data
