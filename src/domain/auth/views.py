import logging
from typing import Optional, Annotated

from datetime import datetime
from src.infrastructure.models.reset_password_message import ResetPasswordMessage
from email_validator import EmailNotValidError, validate_email
from pydantic import EmailStr
from sqlalchemy import select
from starlette.responses import JSONResponse

from src.config import Settings, settings
from src.domain.auth.functions import (
    perform_reset_password,
    get_refreshed_token,
    generate_tokens, check_if_image, upload_to_s3, perform_signup,
    verify_reset_token,
)
from src.domain.auth.utils import hash_password
from src.domain.users.schemas import TokenInfo, UserInfo, NewPasswordRequest
from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Depends,
    Header,
    Form,
    UploadFile,
    File, Query,
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
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=UserInfo)
async def signup(
    user: CreateUser = Depends(),
    image: UploadFile = Depends(check_if_image),
    session: AsyncSession = Depends(get_db),
):

    try:
        # Uploading an image to S3
        s3_file_path = await upload_to_s3(image)
        # User registration
        new_user = await perform_signup(s3_file_path, user, session)

        new_user_dict = {
            "id": str(new_user.id),
            "name": new_user.name,
            "surname": new_user.surname,
            "username": new_user.username,
            "phone_number": new_user.phone_number,
            "email": new_user.email,
            "role": new_user.role,
            "group": new_user.group,
            "is_blocked": new_user.is_blocked,
            "created_at": new_user.created_at,
            "modified_at": new_user.modified_at,
        }

        response_data = UserInfo(**new_user_dict)
        return JSONResponse(content=response_data.dict(), status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"detail": e.detail}, status_code=e.status_code)


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


# @router.post("/set-new-password")
# async def set_new_password(
#         new_password_request: NewPasswordRequest,
#         reset_token: str = Query(..., description="Reset token received in the email"),
#         session: AsyncSession = Depends(get_db)
# ):
#     try:
#         user_email = await verify_reset_token(reset_token)
#         if not user_email:
#             raise HTTPException(status_code=400, detail="Invalid or expired reset token")
#
#         async with session.begin():
#             # Находим пользователя в базе данных по email
#             stmt = select(User).filter(User.email == user_email)
#             result = await session.execute(stmt)
#             user = result.scalars().first()
#
#             if not user:
#                 raise HTTPException(status_code=404, detail="User not found")
#
#             hashed_password = hash_password(new_password_request.password)
#
#             # Обновляем хешированный пароль пользователя
#             user.password = hashed_password.decode()  # Преобразуем байтовую строку в строку
#
#             logger.info(f"Updating password for user: {user.email}")
#
#             return "The password was updated successfully!"
#
#     except HTTPException as e:
#         logger.error(f"HTTPException occurred: {e.detail}")
#         raise e
#
#     except Exception as e:
#         logger.exception(f"Failed to update password: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to update password")

@router.post("/set-new-password")
async def set_new_password(
        new_password_request: NewPasswordRequest,
        reset_token: str = Query(..., description="Reset token received in the email"),
        session: AsyncSession = Depends(get_db)
):
    try:
        user_email = await verify_reset_token(reset_token)
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        async with session.begin():
            # Find the user in the database by email
            stmt = select(User).filter(User.email == user_email)
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update the user's password
            hashed_password = hash_password(new_password_request.password)
            user.password = hashed_password.decode()  # Convert bytes to string

            # Create and save a ResetPasswordMessage
            reset_message = ResetPasswordMessage(
                user_id=user.id,
                email_address=user.email,
                subject="Password Reset",
                body="Your password has been successfully reset.",
            )
            session.add(reset_message)

            logger.info(f"Updating password for user: {user.email}")

            return "The password was updated successfully!"

    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise e

    except Exception as e:
        logger.exception(f"Failed to update password: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update password")