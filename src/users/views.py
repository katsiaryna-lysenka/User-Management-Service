from src.auth.utils import decode_jwt
from src.users.crud import CRUD
from src.core.config import engine
from src.users.schemas import UserSchema, UserInfo, UpdateUser
from http import HTTPStatus
from typing import List
from src.core.models.role import State
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import APIRouter
import jwt
from fastapi import Query
from fastapi import HTTPException

session = async_sessionmaker(bind=engine, expire_on_commit=False)
db = CRUD()

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/all_users_free/", response_model=List[UserSchema])
async def get_all_users():

    # получаю всех пользователей из базы данных
    users = await db.get_all(session)

    # пароли из строкового формата в байты
    for user in users:
        user.password = user.password.encode()

    return users


@router.get("/me/", response_model=UserInfo)
async def user_info(access_token: str) -> UserInfo:
    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)

        user_id = str(decoded_token.get("user_id"))

        # получаю информацию о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id)

        # преобразую UUID в строку для поля id
        user_info["id"] = str(user_info["id"])

        # создаю экземпляр класса UserInfo с полученной информацией о пользователе
        user_info_instance = UserInfo(**user_info)

        return user_info_instance
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.patch("/me/", response_model=UpdateUser)
async def update_user(data: UpdateUser, access_token: str) -> UpdateUser:
    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)
        user_id = str(decoded_token.get("user_id"))

        if user_id is None:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # обновление информации о пользователе
        updated_user = await db.update(session, user_id, data)

        return updated_user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")


@router.delete("/me/", status_code=HTTPStatus.NO_CONTENT)
async def delete_user(access_token: str) -> None:
    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)
        user_id = str(decoded_token.get("user_id"))

        # получаю информацию о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id)

        # преобразую UUID в строку для поля id
        user_info["id"] = str(user_info["id"])

        await db.delete(session, user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")


@router.get("/{user_id}/", response_model=UserInfo)
async def get_user_by_id(access_token: str, user_id: str) -> UserInfo:
    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)
        user_id_main = str(decoded_token.get("user_id"))

        # получаю информацию о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id_main)

        # извлекаю роль пользователя из информации о пользователе
        user_role = user_info.get("role")

        # проверяю роль пользователя и выполняем соответствующие действия
        if user_role == State.ADMIN.value:
            # получаю информацию о пользователе по его ID
            user_info = await db.get_user_info_by_id(session, user_id)
            user_info["id"] = str(user_info["id"])

            # создаю экземпляр класса UserInfo с полученной информацией о пользователе
            user_info_instance = UserInfo(**user_info)

            return user_info_instance

        elif user_role == State.MODERATOR.value:
            # получаю информацию о пользователе по его ID
            user_info = await db.get_user_info_by_id(session, user_id)
            if (
                user_info["group"]
                == (await db.get_user_info_by_id(session, user_id))["group"]
            ):
                user_info["id"] = str(user_info["id"])

                # создаю экземпляр класса UserInfo с полученной информацией о пользователе
                user_info_instance = UserInfo(**user_info)

                return user_info_instance
            else:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            raise HTTPException(status_code=403, detail="Access denied")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/", response_model=UpdateUser)
async def update_user_for_admin(
    access_token: str,
    user_id: str,
    data: UpdateUser,
) -> UpdateUser:
    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)
        user_id_main = str(decoded_token.get("user_id"))

        # получаю информацию о пользователе по его ID
        user_info = await db.get_user_info_by_id(session, user_id_main)

        # извлекю роль пользователя из информации о пользователе
        user_role = user_info.get("role")

        # проверяю роль пользователя
        if user_role != State.ADMIN.value:
            raise HTTPException(status_code=403, detail="Insufficient access rights")

        # обновляю информацию о пользователе
        updated_user = await db.update(session, user_id, data)

        return updated_user

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users")
async def get_users_for_parameters(
    access_token: str,
    page: int = Query(1),
    limit: int = Query(30),
    filter_by_name: str = Query(None),
    sort_by: str = Query(None),
    order_by: str = Query(None, pattern="^(asc|desc)$"),
):

    try:
        # извлекаю user_id из токена
        decoded_token = await decode_jwt(access_token)
        user_id_main = str(decoded_token.get("user_id"))

        # получаю информацию о пользователе по его id
        user_info = await db.get_user_info_by_id(session, user_id_main)

        # извлекаю роль пользователя из информации о пользователе
        user_role = user_info.get("role")

        if user_role == State.ADMIN.value:
            # получаем все группы пользователей
            all_groups = await db.get_all_groups(session)

            # вызываю функцию get_with_parameters, передавая ей параметры из запроса
            users = await db.get_with_parameters(
                async_session=session,
                page=page,
                limit=limit,
                filter_by_name=filter_by_name,
                sort_by=sort_by,
                order_by=order_by,
                groups=all_groups,  # передаю список всех групп
            )
            return users

        elif user_role == State.MODERATOR.value:
            # получаю group текущего пользователя
            user_group = user_info["group"]

            # вызываю функцию get_with_parameters с указанием группы пользователя
            users = await db.get_with_parameters(
                async_session=session,
                page=page,
                limit=limit,
                filter_by_name=filter_by_name,
                sort_by=sort_by,
                order_by=order_by,
                groups=[user_group],  # передаю группу текущего пользователя
            )
            return users

        else:
            # если роль user, возвращаю сообщение об отсутствии доступа
            return {"message": "insufficient access rights"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
