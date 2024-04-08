import core
from auth.utils import decode_jwt
from auth.views import get_access_token
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


@router.get("/my/", response_model=List[UserSchema])
async def get_all_users():

    # получаю всех пользователей из базы данных
    users = await db.get_all(session)

    # пароли из строкового формата в байты
    for user in users:
        user.password = user.password.encode()

    return users


# new

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


# @router.get("/me/", response_model=UserInfo)
# async def user_info(credentials: HTTPBasicCredentials = Depends(security)) -> UserInfo:
#     try:
#         # аутентификация пользователя
#         user = await authenticate_user(credentials.username, credentials.password)
#
#         # получаем информацию о пользователе по его ID
#         user_info = await db.get_user_info_by_id(session, str(user.id))
#
#         # преобразуем UUID в строку для поля id
#         user_info["id"] = str(user_info["id"])
#
#         # создаем экземпляр класса UserInfo с полученной информацией о пользователе
#         user_info_instance = UserInfo(**user_info)
#
#         return user_info_instance
#     except (ValueError, HTTPException) as e:
#         raise HTTPException(status_code=401, detail=str(e))


@router.get("/me/", response_model=UserInfo)
async def user_info(credentials: HTTPBasicCredentials = Depends(security)) -> UserInfo:
    try:
        # Проверяем, были ли предоставлены учетные данные
        if not (credentials.username and credentials.password):
            raise ValueError("Invalid credentials")

        # Получаем токен доступа из учетных данных пользователя
        access_token = get_access_token(credentials.username, credentials.password)

        # Извлекаем user_id из токена
        decoded_token = decode_jwt(access_token)
        user_id = str(decoded_token.get("user_id"))

        # Получаем информацию о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id)

        # Преобразуем UUID в строку для поля id
        user_info["id"] = str(user_info["id"])

        # Создаем экземпляр класса UserInfo с полученной информацией о пользователе
        user_info_instance = UserInfo(**user_info)

        return user_info_instance
    except (ValueError, HTTPException) as e:
        raise HTTPException(status_code=401, detail=str(e))


# @router.patch("/me/")
# async def update_user(access_token: str, data: CreateUser):
#     try:
#
#         decoded_token = decode_jwt(access_token)
#         user_id = str(decoded_token.get("user_id"))
#         user_info = await db.get_user_info_by_id(session, user_id)
#         user_info["id"] = str(user_info["id"])
#
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Access token has expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid access token")
#
#     user_data = data.dict()
#     user = await db.update(session, user_id, data=user_data)
#
#     return user


@router.patch("/me/")
async def update_user(access_token: str, data: CreateUser):
    try:
        # Преобразуем строку токена в байтовый формат
        access_token_bytes = access_token.encode("utf-8")

        decoded_token = decode_jwt(access_token_bytes)
        user_id = str(decoded_token.get("user_id"))
        user_info = await db.get_user_info_by_id(session, user_id)
        user_info["id"] = str(user_info["id"])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user_data = data.dict()
    user = await db.update(session, user_id, data=user_data)

    return user


@router.delete("/me/", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(access_token: str) -> None:
    try:
        # user_id из верифицированного токена
        decoded_token = decode_jwt(access_token)
        user_id = str(decoded_token.get("user_id"))

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
        user_dicts = [
            {
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
                "modified_at": user_obj.modified_at,
            }
            for user_obj in users
        ]

        return user_dicts

    elif current_user_role == State.MODERATOR.value:

        # получаем информацию о пользователях с тем же параметром group

        users = await db.get_by_group(session, current_user_group)

        user_dicts = [
            {
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
            for user in users
        ]

        return user_dicts

    else:

        # если роль USER, возвращаю сообщение об отсутствии доступа

        return {"message": "Insufficient access rights"}


# new
@router.patch("/{user_id}/")
async def update_user_for_admin(
    admin_user_id: str, target_user_id: str, data: CreateUser
):
    # Check if the admin_user_id corresponds to an admin user
    admin_user = await db.get_by_id(session, admin_user_id)
    if admin_user.role != State.ADMIN.value:
        return {"message": "Insufficient access rights"}

    # Get the target user by ID
    target_user = await db.get_by_id(session, target_user_id)

    # Convert CreateUser object to a dictionary
    user_data = data.dict()

    # Update the target user with new data
    updated_user = await db.update(session, target_user_id, user_data)

    # Construct the response dictionary
    user_dict = {
        "id": updated_user.id,
        "name": updated_user.name,
        "surname": updated_user.surname,
        "username": updated_user.username,
        "phone_number": updated_user.phone_number,
        "email": updated_user.email,
        "role": updated_user.role,
        "group": updated_user.group,
        "is_blocked": updated_user.is_blocked,
        "created_at": updated_user.created_at,
        "modified_at": updated_user.modified_at,
    }

    return user_dict


from fastapi import Query


@router.get("/users")
async def get_users_for_parameters(
    user_id: str,
    page: int = Query(1),
    limit: int = Query(30),
    filter_by_name: str = Query(None),
    sort_by: str = Query(None),
    order_by: str = Query(None, regex="^(asc|desc)$"),
):

    user = await db.get_by_id(session, user_id)

    # получаю роль текущего пользователя
    current_user_role = user.role
    current_user_group = user.group

    if current_user_role == State.ADMIN.value:

        # Получаем все группы пользователей
        all_groups = await db.get_all_groups(session)

        # Вызываем функцию get_with_parameters, передавая ей параметры из запроса
        users = await db.get_with_parameters(
            async_session=session,
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            sort_by=sort_by,
            order_by=order_by,
            groups=all_groups,  # Передаем список всех групп
        )
        return users

    elif current_user_role == State.MODERATOR.value:
        # Получаем информацию о пользователях с тем же параметром group
        users_in_group = await db.get_by_group(session, current_user_group)

        # Применяем фильтрацию, сортировку и пагинацию к пользователям из группы
        filtered_users = await db.get_with_parameters(
            async_session=session,
            page=page,
            limit=limit,
            filter_by_name=filter_by_name,
            sort_by=sort_by,
            order_by=order_by,
            groups=[
                user.group for user in users_in_group
            ],  # Передаем список всех групп
        )

        # Возвращаем отфильтрованный список пользователей из группы
        return filtered_users

    else:

        # если роль USER, возвращаю сообщение об отсутствии доступа

        return {"message": "Insufficient access rights"}
