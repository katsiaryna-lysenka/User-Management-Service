import aio_pika

import json
import redis
from fastapi import Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.helpers import (
    create_refresh_token,
    create_reset_token,
    create_access_token,
)
from src.auth.utils import decode_jwt
from src.core.config import settings, get_db
from src.core.models import User
from jwt import InvalidTokenError

from redis.exceptions import RedisError


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

    try:
        # созданю объекта Redis
        redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
        print(f"redis_client = {redis_client}")

        # полученю значение токена из Redis
        redis_token_value = redis_client.get(token)
        print(f"redis_token_value = {redis_token_value}")

        if redis_token_value is not None:
            raise HTTPException(status_code=401, detail="Refresh token is blacklisted")

        # получаю пользователя из базы данных, используя user_id
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        print(f"user = {user}")

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # генерирую новый access токен
        new_access_token = create_access_token(user)
        print(f"new_access_token = {new_access_token}")

        # генерирую новый refresh токен
        new_refresh_token = create_refresh_token(user)
        print(f"new_refresh_token = {new_refresh_token}")

        # добавляю старый refresh токен в черный список в Redis
        expire_seconds = int(settings.auth_jwt.refresh_token_expire_days) * 24 * 60 * 60
        redis_client.set(token, token, ex=expire_seconds)
        print("Добавляю старый refresh токен в черный список в Redis")

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except RedisError:

        raise HTTPException(status_code=500, detail="Redis error occurred")


async def perform_reset_password(email: str, session: AsyncSession = Depends(get_db)):
    query = select(User).filter(User.email == email)
    user = await session.execute(query)
    user = user.scalar_one_or_none()
    print(f"user = {user}")

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user)  # передаю весь объект пользователя
    print(f"reset_token = {reset_token}")

    try:
        await publish_reset_email_message(email, reset_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "Reset email sent successfully"}


async def publish_reset_email_message(email: str, reset_token: str):
    try:
        connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{settings.rabbitmq_host}/"
        )
        print("I have a connect")
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
