from datetime import datetime
from http import HTTPStatus
from typing import Optional

from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr
from starlette.responses import JSONResponse

from src.auth.functions import (
    perform_reset_password,
    get_refreshed_token,
    generate_tokens,
)
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
        name=user_data.name,
        surname=user_data.surname,
        username=user_data.username,
        password=hashed_password_str,
        phone_number=user_data.phone_number,
        email=user_data.email,
        role=user_data.role,
        group=user_data.group,
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
        "created_at": datetime.now(),  # Установка значения created_at при создании User
        "modified_at": datetime.now(),
    }

    return user_dict


@router.post("/login", status_code=status.HTTP_200_OK, response_model=dict)
async def return_tokens(
    username: str = Form(None),
    email: Optional[EmailStr] = Form(None),
    phone_number: Optional[str] = Form(None),
    password: str = Form(...),
) -> dict:
    try:
        # генерируем токены доступа и обновления
        tokens = await generate_tokens(
            username=username,
            email=email if email != "" else None,
            phone_number=phone_number if phone_number != "" else None,
            password=password,
        )

        # возвращаем токены в формате словаря
        return tokens

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


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
