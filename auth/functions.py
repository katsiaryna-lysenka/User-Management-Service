import aio_pika

import json

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.helpers import create_refresh_token, create_reset_token
from core.config import settings, get_db
from core.models import User


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
            f"amqp://guest:guest@{settings.RABBITMQ_HOST}/"
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
