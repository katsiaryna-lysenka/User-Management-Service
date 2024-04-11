import pytest
from fastapi.testclient import TestClient

from auth.utils import decode_jwt

from main import app
from users.crud import CRUD

db = CRUD()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_user_info(client):
    # Подготовка данных для теста
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjdmNmM0MTAtNDliNy00NTM3LWJkYTUtOWU2ZTVjMjM4MzNmIiwiZXhwIjoxNzEyODQ0NzA4LCJpYXQiOjE3MTI4MzM5MDh9.G0EoUq6m5qoNMbVtSHnRms1uh2Ttx1LjXHdLRPAjLRXY_kldXibMmIWamKTNnE6Jx2hnhhkdTySsmYDzQzGnq-sdGKmCsvG60eoWkpBxU0KZbZa8SgT10evRS8yz-nwAuqwCdYW_D6AtZCIjVEHDAqPps2enPQkOU05UvxzD7Xob0LgVjYkdyHJ26OGGGKAF7dBpHroEz-il2ugGpf7y7mFe09laY8i1xomBK0n5EftJFYDxymqkk_SX7HrphC3lN8bRAYbnvdpbSDc0hImutMXiucH9zEZTjTfiGamxWs3lCRaIuI41MHnyypSK6mX5n5DtrYdRGaLzi76s50yi_Q"

    # Ожидаемый результат
    expected_user_info = {
        "id": "27f6c410-49b7-4537-bda5-9e6e5c23833f",
        "name": "Helen",
        "surname": "Fry",
        "username": "helen.fry111",
        "email": "helen.fry_y_y@gmail.com",
        "phone_number": "+375298888888",
        "role": "admin",
        "group": "Cat"
    }

    # Мокируем метод decode_jwt
    async def mock_decode_jwt(token: str):
        decoded_token = await decode_jwt(token)  # Декодируем токен
        return decoded_token  # Мокированный результат декодирования токена

    app.dependency_overrides[decode_jwt] = mock_decode_jwt

    # Мокируем метод get_user_info_by_id
    async def mock_get_user_info_by_id(session, user_id):
        return expected_user_info  # Мокированный результат получения информации о пользователе

    app.dependency_overrides[db.get_user_info_by_id] = mock_get_user_info_by_id

    # Вызов тестируемого эндпоинта
    response = client.get(
        "/user/me/",
        params={"access_token": access_token}
    )

    # Проверка корректности ответа
    assert response.status_code == 200
    assert response.json() == expected_user_info
