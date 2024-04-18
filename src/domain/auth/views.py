from datetime import datetime
from http import HTTPStatus
from typing import Optional, Annotated

import boto3
from botocore.client import Config
from botocore.session import get_session
from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from src.config import Settings, settings
from src.domain.auth.functions import (
    perform_reset_password,
    get_refreshed_token,
    generate_tokens,
)
from src.domain.auth.utils import hash_password
from src.domain.users.schemas import TokenInfo, UserInfo
from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Depends,
    Header,
    Form,
    UploadFile,
    File,
)
from fastapi.security import HTTPBasic

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.infrastructure.database.create_db import engine, get_db, SessionLocal
from src.infrastructure.models import User, Role
from src.domain.users.crud import CRUD
from src.domain.users.schemas import CreateUser

router = APIRouter(prefix="/auth", tags=["Auth"])
session = async_sessionmaker(bind=engine, expire_on_commit=False)
db = CRUD()
security = HTTPBasic()
crud = CRUD()


@router.post("/signup", status_code=HTTPStatus.CREATED, response_model=dict)
async def create_user(user_data: CreateUser) -> dict:

    hashed_password = hash_password(user_data.password)
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
        s3_file_path=user_data.s3_file_path,
    )

    user = await db.add(session, new_user)

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
        "created_at": datetime.now(),
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

        tokens = await generate_tokens(
            username=username,
            email=email if email != "" else None,
            phone_number=phone_number if phone_number != "" else None,
            password=password,
        )

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
    email: str, session: AsyncSession = Depends(get_db)
):

    try:
        validate_email(email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email format")

    try:
        return await perform_reset_password(email, session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)
