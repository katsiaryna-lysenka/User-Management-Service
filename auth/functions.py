import aio_pika

import json

import redis
from redis import Redis
from fastapi import Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.helpers import (
    create_refresh_token,
    create_reset_token,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
    create_access_token,
)
from auth.utils import decode_jwt
from core.config import settings, get_db
from core.models import User
from jwt import InvalidTokenError

from redis_manager_field import redis_manager
from redis_manager_field.redis_manager import RedisManager


async def get_refreshed_token(token: str, session: AsyncSession = Depends(get_db)):
    try:
        payload = await decode_jwt(token)
        print(f"payload = {payload}")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    print(f"user_id = {user_id}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Инициализация клиента Redis
    redis_client = RedisManager.redisClient
    print(f"redis_client = {redis_client}")

    if redis_client is None:
        raise HTTPException(status_code=500, detail="Redis connection not available")

    # Получаем значение токена из Redis
    redis_token_value = await redis_client.get(token)
    print(f"redis_token_value = {redis_token_value}")
    if redis_token_value is not None:
        raise HTTPException(status_code=401, detail="Refresh token is blacklisted")

    # Получаем пользователя из базы данных, используя user_id
    result = await session.execute(select(User).filter(User.user_id == user_id))
    user = result.scalar_one_or_none()
    print(f"user = {user}")

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Генерируем новый access токен
    new_access_token = create_access_token(user)
    print(f"new_access_token = {new_access_token}")

    # Генерируем новый refresh токен
    new_refresh_token = create_refresh_token(user)
    print(f"new_refresh_token = {new_refresh_token}")

    # Добавляем старый refresh токен в черный список в Redis
    await redis_client.setex(
        token, 1, settings.auth_jwt.refresh_token_expire_days * 24 * 60 * 60
    )
    print("Добавляем старый refresh токен в черный список в Redis")

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


async def perform_reset_password(email: str, session: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == email)
    user = await session.execute(query)
    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user)  # Передаем весь объект пользователя

    try:
        await publish_reset_email_message(email, reset_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "Reset email sent successfully"}


async def publish_reset_email_message(email: str, reset_token: str):
    try:
        connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{settings.RABBITMQ_HOST}/"  # ошибка тут!!
        )
    except aio_pika.exceptions.AMQPConnectionError as e:
        error_message = f"Error connecting to RabbitMQ: {str(e)}"
        print(error_message)
        return

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("reset-password-stream", durable=True)

        message_body = {
            "email": email,
            "reset_token": reset_token,
            "message": f"Reset your password by clicking the following link: "
            f"http://127.0.0.1:5000/auth/set-new-password?token={reset_token}\nThe link will deactivate in"
            f" 5 minutes",
        }
        print(message_body)

        json_message_body = json.dumps(message_body)

        message = aio_pika.Message(
            body=json_message_body.encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await channel.default_exchange.publish(
            message, routing_key="reset-password-stream"
        )

    await connection.close()
