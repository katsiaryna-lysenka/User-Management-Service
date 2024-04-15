from datetime import datetime
from http import HTTPStatus

from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr
from starlette.responses import JSONResponse

from src.auth.functions import perform_reset_password, get_refreshed_token
from src.auth.utils import encode_jwt, hash_password, validate_password
from src.users.schemas import TokenInfo
from fastapi import APIRouter, status, HTTPException, Depends, Header, Form
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.core.config import engine, get_db
from src.core.models import User
from src.users.crud import CRUD
from src.users.schemas import CreateUser

router = APIRouter(prefix="/auth", tags=["Auth"])
session = async_sessionmaker(bind=engine, expire_on_commit=False)
db = CRUD()
security = HTTPBasic()
crud = CRUD()


@router.post("/signup", status_code=HTTPStatus.CREATED, response_model=dict)
async def create_user(user_data: CreateUser) -> dict:

    # хеширую пароль
    hashed_password = hash_password(user_data.password)

    # преобразую хешированный пароль в строку
    hashed_password_str = hashed_password.decode()

    new_user = User(
        id=user_data.id,
        name=user_data.name,
        surname=user_data.surname,
        username=user_data.username,
        password=hashed_password_str,
        phone_number=user_data.phone_number,
        email=user_data.email,
        role=user_data.role,
        group=user_data.group,
        is_blocked=user_data.is_blocked,
        created_at=datetime.now(),  # Установка значения created_at при создании User
        modified_at=datetime.now(),
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
async def return_tokens(
    username: str = Form(None),
    email: EmailStr = Form(None),
    phone_number: str = Form(None),
    password: str = Form(...),
) -> dict:
    try:
        # проверю наличие информации для входа
        if not any([username, email, phone_number]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login information missing",
            )

        # полученю пользователя из базы данных
        user = None
        if username:
            user = await crud.get_by_login(session, username)
        elif email:
            user = await crud.get_by_login(session, email)
        elif phone_number:
            user = await crud.get_by_login(session, phone_number)

        # проверяю наличие пользователя
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # хеширую пароля
        hashed_password = hash_password(password)

        # провеяю пароль
        if not validate_password(password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
            )

        # созданю токены доступа и обновления
        access_token = encode_jwt({"user_id": str(user.id)})
        refresh_token = encode_jwt(
            {"user_id": str(user.id)},
            expire_minutes=60,
        )

        # возвращеню токены в формате словаря
        return {"access_token": access_token, "refresh_token": refresh_token}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


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


@router.post("/refresh-token", response_model=TokenInfo)
async def refresh_token(
    token: str = Header(...), session: AsyncSession = Depends(get_db)
):
    try:
        response_data = await get_refreshed_token(token, session)
        return JSONResponse(content=response_data, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"detail": e.detail}, status_code=e.status_code)


@router.post("/reset-password", response_model=None)
async def reset_password(
    email: str = Header(...), session: AsyncSession = Depends(get_db)
):

    try:
        validate_email(email)  # Проверка валидности email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email format")

    try:
        return await perform_reset_password(email, session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
