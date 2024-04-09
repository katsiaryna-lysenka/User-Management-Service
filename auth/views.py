from datetime import datetime
from http import HTTPStatus

from auth.utils import encode_jwt
from rabbitmq_management_field.rebbitmq_management import rabbitmq_management
from redis_manager_field.redis_manager import redis_manager
from users.schemas import TokenInfo
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from sqlalchemy.ext.asyncio import async_sessionmaker

from auth.helpers import create_access_token, create_refresh_token
from core.config import engine
from core.models import User
from users.crud import CRUD
from users.schemas import CreateUser


router = APIRouter(prefix="/auth", tags=["Auth"])
session = async_sessionmaker(bind=engine, expire_on_commit=False)
db = CRUD()
security = HTTPBasic()
crud = CRUD()


@router.post("/signup", status_code=HTTPStatus.CREATED, response_model=dict)
async def create_user(user_data: CreateUser) -> dict:

    # устанавливаю значения по умолчанию для created_at и modified_at
    user_data.created_at = datetime.now()
    user_data.modified_at = datetime.now()

    new_user = User(
        id=user_data.id,
        name=user_data.name,
        surname=user_data.surname,
        username=user_data.username,
        password=user_data.password,
        phone_number=user_data.phone_number,
        email=user_data.email,
        role=user_data.role,
        group=user_data.group,
        is_blocked=user_data.is_blocked,
        created_at=user_data.created_at,
        modified_at=user_data.modified_at,
    )

    user = await db.add(session, new_user)

    # преобразую объект User в словарь, выбирая только нужные атрибуты
    user_dict = {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "username": user.username,
        "phone_number": user.phone_number,
        "email": user.email,
        "role": user.role,
        "group": user.group,
        "is_blocked": user.is_blocked,
        "created_at": user.created_at,
        "modified_at": user.modified_at,
    }

    return user_dict


@router.post("/login", status_code=status.HTTP_200_OK, response_model=dict)
async def return_tokens(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    try:
        # аутентификация пользователя
        user = await crud.authenticate_user(
            session, credentials.username, credentials.password
        )

        # создаю токены доступа и обновления
        access_token = encode_jwt({"user_id": str(user.id)})
        refresh_token = encode_jwt(
            {"user_id": str(user.id)},
            expire_minutes=60,  # Токен обновления сроком на 1 час
        )

        # возвращаю токены в формате словаря
        return {"access_token": access_token, "refresh_token": refresh_token}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_access_token(username: str, password: str) -> bytes:
    try:

        # получаю словарь с токенами доступа от функции return_tokens
        tokens = await return_tokens(
            HTTPBasicCredentials(username=username, password=password)
        )

        # извлекаю токен доступа из словаря
        access_token = tokens.get("access_token")

        # если токен доступа не был получен, возникает ошибка
        if not access_token:
            raise HTTPException(
                status_code=500, detail="Failed to generate access token"
            )

        # преобразую токен доступа в байтовый формат
        access_token_bytes = access_token.encode()

        return access_token_bytes
    except HTTPException as e:

        # если возникла ошибка при получении токена доступа, пробрасываю ее дальше
        raise e


async def get_refresh_token(username: str, password: str) -> bytes:
    try:

        # получаю словарь с токенами доступа от функции return_tokens
        tokens = await return_tokens(
            HTTPBasicCredentials(username=username, password=password)
        )

        # извлекаю токен доступа из словаря
        refresh_token = tokens.get("refresh_token")

        print(f"refresh_token = {refresh_token}")
        # если токен доступа не был получен, возникает ошибка
        if not refresh_token:
            raise HTTPException(
                status_code=500, detail="Failed to generate access token"
            )

        # преобразую токен доступа в байтовый формат
        refresh_token_bytes = refresh_token.encode()

        print(f"refresh_token_bytes = {refresh_token_bytes}")
        return refresh_token_bytes
    except HTTPException as e:

        # если возникла ошибка при получении токена доступа, пробрасываю ее дальше
        raise e


@router.post("/refresh/", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        # Аутентификация пользователя
        user = await crud.authenticate_user(
            session, credentials.username, credentials.password
        )

        # Получаем старый refresh токен
        old_refresh_token = await get_refresh_token(
            credentials.username, credentials.password
        )

        print(f"old_refresh_token = {old_refresh_token}")

        # Генерируем новые токены доступа и обновления
        access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        # Добавляем старый refresh токен в черный список Redis
        redis_manager.redisClient.set(old_refresh_token, "blacklisted")

        return TokenInfo(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/reset-password/")
async def auth_reset_password(email: str):
    try:
        # Публикуем сообщение в очередь RabbitMQ
        if rabbitmq_management.publish_reset_password_message(email):
            return {"message": "Password reset request has been submitted."}
        else:
            raise HTTPException(status_code=500, detail="Failed to submit password reset request.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Выводим подробности об ошибке
        raise HTTPException(status_code=500, detail="Internal Server Error")
