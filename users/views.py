from auth.utils import decode_jwt
from users.crud import CRUD
from core.config import engine
from users.schemas import CreateUser, UserSchema, UserInfo
from http import HTTPStatus
from typing import List, Union
from core.models import User
from core.models.role import State
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import APIRouter, HTTPException
import jwt

session = async_sessionmaker(bind=engine, expire_on_commit=False)
db = CRUD()

router = APIRouter(prefix="/user", tags=["Users"])


# @router.get("/my/", response_model=List[UserSchema])
# async def get_all_users():
#
#     # получаю всех пользователей из базы данных
#     users = await db.get_all(session)
#
#     # пароли из строкового формата в байты
#     for user in users:
#         user.password = user.password.encode()
#
#     return users

@router.get("/me/", response_model=UserInfo)
async def user_info(access_token: str) -> UserInfo:
    try:
        # извлекаю user_id из верифицированного токена
        decoded_token = decode_jwt(access_token)
        user_id = str(decoded_token.get('user_id'))

        # получаю информации о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id)

        # преобразую UUID в строку для поля id
        user_info['id'] = str(user_info['id'])

        # создаю экземпляр класса UserInfo с полученной информацией о пользователе
        user_info_instance = UserInfo(**user_info)

        return user_info_instance
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")


@router.patch("/me/")
async def update_user(access_token: str, data: CreateUser):
    try:

        decoded_token = decode_jwt(access_token)
        user_id = str(decoded_token.get('user_id'))
        user_info = await db.get_user_info_by_id(session, user_id)
        user_info['id'] = str(user_info['id'])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_data = data.dict()
    user = await db.update(
        session, user_id, data=user_data
    )

    return user


@router.delete("/me/", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(access_token: str) -> None:
    try:
        # user_id из верифицированного токена
        decoded_token = decode_jwt(access_token)
        user_id = str(decoded_token.get('user_id'))

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    await db.delete(session, user_id)


@router.get("/{user_id}/")
async def get_user_by_id(user_id: str) -> Union[List[dict], dict]:

    user = await db.get_by_id(session, user_id)

    # получаю роль текущего пользователя
    current_user_role = user.role
    current_user_group = user.group

    if current_user_role == State.ADMIN.value:
        # получаю всех пользователей из базы данных
        users = await db.get_all(session)

        # преобразую пароли из строкового формата в байты
        for user_obj in users:
            user_obj.password = user_obj.password.encode()

        # преобразую объекты пользователя в словари
        user_dicts = [{
            "id": user_obj.id,
            "name": user_obj.name,
            "surname": user_obj.surname,
            "username": user_obj.username,
            "phone_number": user_obj.phone_number,
            "email": user_obj.email,
            "role": user_obj.role,
            "group": user_obj.group,
            "is_blocked": user_obj.is_blocked,
            "created_at": user_obj.created_at,
            "modified_at": user_obj.modified_at
        } for user_obj in users]

        return user_dicts

    elif current_user_role == State.MODERATOR.value:

        # получаем информацию о пользователях с тем же параметром group

        users = await db.get_by_group(session, current_user_group)

        user_dicts = [{

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
            "modified_at": user.modified_at

        } for user in users]

        return user_dicts

    else:

        # если роль USER, возвращаю сообщение об отсутствии доступа

        return {"message": "Insufficient access rights"}