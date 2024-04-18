from typing import Any
from urllib.parse import quote_plus

import pytest
import httpx


@pytest.mark.asyncio
async def test_create_user():
    user_data = {
        "id": "fb4e9d85-26cf-40ec-9660-c8fd7cfed8b9",
        "name": "nikol",
        "surname": "syt",
        "username": "nikol_l_l",
        "password": "99987777",
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

    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_create_second_user():
    user_data = {
        "id": "d213231c-da77-4587-a4dd-1fc0f069655c",
        "name": "nikol",
        "surname": "syt",
        "username": "nikol_l_l",
        "password": "99987777",
        "phone_number": "294444444",
        "email": "nikol@gmail.com",
        "role": "frog",
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

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_endpoint():

    data = {
        "username": "nikol_l_l",
        "email": "nikol@gmail.com",
        "phone_number": "",
        "password": "99987777",
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/login"
    url = f"{base_url}{endpoint}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Sending a request
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data=data)
    print("Response data:", response.text)

    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@pytest.mark.asyncio
async def test_second_login_endpoint():
    data = {
        "username": "nikol_l_l",
        "email": "nikol@gmail.com",
        "phone_number": "",
        "password": "",
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/login"
    url = f"{base_url}{endpoint}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data=data)
    print("Response data:", response.text)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_token_endpoint(access_token, six_test_user):
    token = access_token("1af54f6d-376e-4c1b-aef4-c3d3b27745c6")

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/refresh-token"
    url = f"{base_url}{endpoint}"
    headers = {"accept": "application/json", "token": token}

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers)
    print("Response data:", response.text)

    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data


@pytest.mark.asyncio
async def test_refresh_second_token_endpoint(access_token):
    token = access_token("fb4e9d85-26cf-40ec-9660-c8fd7cfed8b9")

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/refresh-token"
    url = f"{base_url}{endpoint}"
    headers = {
        "accept": "application/json",
        "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjk0MzFmNTItZDFhOC00MzRkLWI5NjEtNzA5ZWUyNGUxNTRmIiwiZXhwIjoxNzEzMjcwMTc2LCJpYXQiOjE3MTMyNTkzNzZ9.qyzV5EbPBa4Nb7aISEvc4S3nKORYfEbVQibprFpdP0Gtm4b9gkDoY1hfWZ4fUFQ2JZBucI6mN-TPH9rIuLQn4_PJTBDnBSkjRWUGxbzBnSHvoB_stq89BXOxySToUk7MRFHM5wtDK8B6j3GDeZn--d_Jz9b7Mc1U5ks4vT407IytaQvSJ2TQwstXpUu0gE1MqDP19805d3Tpo9Iro5D6flAAW5h3IGY47fz8LDJqkFn8bY_w23NJVkGk31pzSbjT7yVmNzpDUDdz87c5VDKqP_99h3fHYEEUK2YyXHb88k_n89Fsu1EWgq_GuNiJ6GmwjJZrv43whwg7aWH3e5Rka",
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers)
    print("Response data:", response.text)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_success(fourth_test_user: Any):

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/reset-password"
    url = f"{base_url}{endpoint}?email={quote_plus(fourth_test_user.email)}"

    headers = {
        "accept": "application/json",
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data="")
        print("Response data:", response.text)

        assert response.status_code == 200
        print("ok")


@pytest.mark.asyncio
async def test_reset_password_invalid_email(fifth_test_user: Any):

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/reset-password"
    url = f"{base_url}{endpoint}?email={quote_plus(fifth_test_user.email)}"

    headers = {
        "accept": "application/json",
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data="")
        print("Response data:", response.text)

        assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_missing_email(fifth_test_user: Any):

    base_url = "http://0.0.0.0:5000"
    endpoint = "/auth/reset-password"
    url = f"{base_url}{endpoint}?email="
    headers = {
        "accept": "application/json",
    }

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.post(url, headers=headers, data="")
        print("Response data:", response.text)

        assert response.status_code == 400
