import urllib.parse
from http import HTTPStatus
from typing import Any
from .conftest import access_token
import httpx
import pytest

from src.domain.users.schemas import UserInfo
from src.domain.users.crud import CRUD


db = CRUD()


@pytest.mark.asyncio
async def test_user_info(access_token, test_user):
    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = access_token(user_id)
    print("Access token:", token)
    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    headers = {"accept": "application/json"}
    params = {"access_token": token}
    url = base_url + endpoint
    print("Request URL:", url)

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers, params=params)
        print("Response:", response.text)

        assert response.status_code == 200
        assert "id" in response.json()
        assert "name" in response.json()
        assert "surname" in response.json()
        assert "username" in response.json()
        assert "email" in response.json()
        assert "phone_number" in response.json()
        assert "role" in response.json()
        assert "group" in response.json()

        user_info_instance = UserInfo(**response.json())
        assert isinstance(user_info_instance, UserInfo)


@pytest.mark.asyncio
async def test_second_user_info(access_token, test_user):
    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aee"
    token = access_token(user_id)
    print("Access token:", token)
    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    headers = {"accept": "application/json"}
    params = {"access_token": token}
    url = base_url + endpoint
    print("Request URL:", url)

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers, params=params)
        print("Response:", response.text)

        assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user(test_user: Any, access_token):

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

    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = access_token(user_id)

    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    url = base_url + endpoint + "?access_token=" + token
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.patch(url, json=updated_user_data, headers=headers)
    print("Response:", response.text)

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["name"] == updated_user_data["name"]
    assert response_data["surname"] == updated_user_data["surname"]
    assert response_data["username"] == updated_user_data["username"]
    assert response_data["phone_number"] == updated_user_data["phone_number"]
    assert response_data["email"] == updated_user_data["email"]
    assert response_data["role"] == updated_user_data["role"]
    assert response_data["group"] == updated_user_data["group"]
    assert response_data["is_blocked"] == updated_user_data["is_blocked"]


@pytest.mark.asyncio
async def test_update_second_user(test_user: Any, access_token):
    updated_user_data = {
        "name": "kkk",
        "surname": "kkk",
        "username": "kkk",
        "password": "222",
        "phone_number": "222",
        "email": "kkk@example.com",
        "role": "queen",
        "group": "Dog",
        "is_blocked": False,
    }

    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = access_token(user_id)

    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    url = base_url + endpoint + "?access_token=" + token
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.patch(url, json=updated_user_data, headers=headers)
    print("Response:", response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_user(access_token, test_user):

    user_id = "30012843-1d0f-4ee0-b17f-a99f70e0aeec"
    token = access_token(user_id)

    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/me/"
    url = base_url + endpoint + "?access_token=" + token
    headers = {"accept": "*/*"}

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.delete(url, headers=headers)
    print("Response:", response.text)

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_get_user_by_id(access_token, second_test_user, third_test_user: Any):

    user_id = "c0b266a1-f393-471a-9e68-83c38fc4270d"
    token = access_token(user_id)

    base_url = "http://0.0.0.0:5000"
    endpoint = f"/user/{third_test_user.id}/"
    url = f"{base_url}{endpoint}?access_token={token}"
    headers = {"accept": "application/json"}
    print(f"other_test_user.id = {third_test_user.id}")

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers)
    print("Response:", response.text)

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert response_data["id"] == str(third_test_user.id)
    assert response_data["name"] == third_test_user.name
    assert response_data["surname"] == third_test_user.surname
    assert response_data["username"] == third_test_user.username
    assert response_data["phone_number"] == third_test_user.phone_number
    assert response_data["email"] == third_test_user.email
    assert response_data["role"] == third_test_user.role
    assert response_data["group"] == third_test_user.group


@pytest.mark.asyncio
async def test_get_second_user_by_id(
    access_token, third_test_user, second_test_user: Any
):

    user_id = "e39f3f3c-39d3-4914-875f-7301f5e4c791"
    token = access_token(user_id)

    base_url = "http://0.0.0.0:5000"
    endpoint = f"/user/{second_test_user.id}/"
    url = f"{base_url}{endpoint}?access_token={token}"
    headers = {"accept": "application/json"}
    print(f"other_test_user.id = {second_test_user.id}")

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(url, headers=headers)
    print("Response:", response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_for_admin(
    access_token, second_test_user, third_test_user: Any
):
    user_id = "c0b266a1-f393-471a-9e68-83c38fc4270d"
    token = access_token(user_id)

    updated_data = {
        "name": "katya",
        "surname": "lekatya",
        "username": "katya.a.a",
        "password": "888",
        "phone_number": "336666666",
        "email": "katya@example.com",
        "role": "moderator",
        "group": "Dog",
        "is_blocked": False,
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = f"/user/{third_test_user.id}/"
    url = f"{base_url}{endpoint}?access_token={token}"
    headers = {"accept": "application/json"}
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.patch(url, json=updated_data, headers=headers)

    assert response.status_code == HTTPStatus.OK
    print("Response data:", response.text)

    response_data = response.json()
    assert response_data["name"] == updated_data["name"]
    assert response_data["surname"] == updated_data["surname"]
    assert response_data["username"] == updated_data["username"]
    assert response_data["password"] == updated_data["password"]
    assert response_data["phone_number"] == updated_data["phone_number"]
    assert response_data["email"] == updated_data["email"]
    assert response_data["role"] == updated_data["role"]
    assert response_data["group"] == updated_data["group"]


@pytest.mark.asyncio
async def test_update_second_user_for_admin(
    access_token, third_test_user, second_test_user: Any
):
    user_id = "e39f3f3c-39d3-4914-875f-7301f5e4c791"
    token = access_token(user_id)

    updated_data = {
        "name": "katya",
        "surname": "lekatya",
        "username": "katya.a.a",
        "password": "888",
        "phone_number": "336666666",
        "email": "katya@example.com",
        "role": "moderator",
        "group": "Dog",
        "is_blocked": False,
    }

    base_url = "http://0.0.0.0:5000"
    endpoint = f"/user/{second_test_user.id}/"
    url = f"{base_url}{endpoint}?access_token={token}"
    headers = {"accept": "application/json"}
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.patch(url, json=updated_data, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users_for_parameters(
    access_token, second_test_user, six_test_user: Any
):
    user_id = "c0b266a1-f393-471a-9e68-83c38fc4270d"
    token = access_token(user_id)

    user_id_main = str(six_test_user.id)
    print("user_id_main:", user_id_main)

    query_params = {
        "page": 1,
        "limit": 30,
        "filter_by_name": str(six_test_user.name),
        "sort_by": "id",
        "order_by": "asc",
    }
    print("six_test_user.name:", six_test_user.name)

    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/users"
    headers = {"accept": "application/json"}
    url = f"{base_url}{endpoint}"
    query_string = urllib.parse.urlencode(query_params)
    full_url = f"{url}?access_token={token}&{query_string}"

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(full_url, headers=headers)
    print("Response data:", response.text)

    assert response.status_code == 200

    assert response.json()


@pytest.mark.asyncio
async def test_get_second_users_for_parameters(
    access_token, second_test_user, six_test_user: Any
):
    user_id = "c0b266a1-f393-471a-9e68-83c38fc4270d"
    token = access_token(user_id)

    user_id_main = str(six_test_user.id)
    print("user_id_main:", user_id_main)

    query_params = {
        "page": 1,
        "limit": 30,
        "filter_by_name": str(six_test_user.name),
        "sort_by": "id",
        "order_by": "ddd",
    }
    print("six_test_user.name:", six_test_user.name)

    base_url = "http://0.0.0.0:5000"
    endpoint = "/user/users"
    headers = {"accept": "application/json"}
    url = f"{base_url}{endpoint}"
    query_string = urllib.parse.urlencode(query_params)
    full_url = f"{url}?access_token={token}&{query_string}"

    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(full_url, headers=headers)
    print("Response data:", response.text)

    assert response.status_code == 422

    assert response.json()
