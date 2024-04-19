import os
import uuid
import time

import aio_pika
import boto3
from botocore.exceptions import ClientError
import json
import redis
from fastapi import Depends, HTTPException, Form, UploadFile, File
from pydantic import EmailStr

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import src
from src.config import Settings
from src.domain.auth.helpers import (
    create_refresh_token,
    create_reset_token,
    create_access_token,
)
from src.domain.auth.utils import (
    decode_jwt,
    hash_password,
    validate_password,
    encode_jwt,
)
from src.domain.users.schemas import CreateUser

from src.infrastructure.database.create_db import settings, get_db, engine
from src.infrastructure.models import User
from jwt import InvalidTokenError

from redis.exceptions import RedisError

from src.domain.users.crud import CRUD

session = async_sessionmaker(bind=engine, expire_on_commit=False)
crud = CRUD()


async def generate_tokens(
    username: str = Form(None),
    email: EmailStr = Form(None),
    phone_number: str = Form(None),
    password: str = Form(...),
) -> dict:
    try:
        if not (username and password):
            raise HTTPException(
                status_code=400, detail="Username and password are required"
            )

        if not (email or phone_number):
            raise HTTPException(
                status_code=400, detail="Either email or phone_number is required"
            )

        user = await crud.get_by_login(session(), username)

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        hashed_password = hash_password(password)

        if not validate_password(password, hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        access_token = encode_jwt({"user_id": str(user.id)})
        refresh_token = encode_jwt(
            {"user_id": str(user.id)},
            expire_minutes=60,
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_access_token(username: str, password: str) -> bytes:
    try:
        tokens = await generate_tokens(username=username, password=password)

        access_token = tokens.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=500, detail="Failed to generate access token"
            )

        access_token_bytes = access_token.encode()

        return access_token_bytes
    except HTTPException as e:
        raise e


async def get_refresh_token(username: str, password: str) -> bytes:
    try:
        tokens = await generate_tokens(username=username, password=password)

        refresh_token = tokens.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=500, detail="Failed to generate refresh token"
            )

        refresh_token_bytes = refresh_token.encode()

        return refresh_token_bytes
    except HTTPException as e:
        raise e


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

        redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)
        print(f"redis_client = {redis_client}")

        redis_token_value = redis_client.get(token)
        print(f"redis_token_value = {redis_token_value}")

        if redis_token_value is not None:
            raise HTTPException(status_code=401, detail="Refresh token is blacklisted")

        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        print(f"user = {user}")

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        new_access_token = create_access_token(user)
        print(f"new_access_token = {new_access_token}")

        new_refresh_token = create_refresh_token(user)
        print(f"new_refresh_token = {new_refresh_token}")

        expire_seconds = int(settings.auth_jwt.refresh_token_expire_days) * 24 * 60 * 60
        redis_client.set(token, token, ex=expire_seconds)

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

    reset_token = create_reset_token(user)  # passing the entire user object
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
    except aio_pika.exceptions.AMQPConnectionError as e:
        error_message = f"Error connecting to RabbitMQ: {str(e)}"
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


async def check_if_image(image: UploadFile = File(None)):
    print("a")
    if not image:
        print("b")
        return None
    elif image.content_type == "image/png":
        print("c")
        return image
    else:
        raise HTTPException(status_code=400, detail="Wrong file type")


import uuid

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile



# async def upload_to_s3(image: UploadFile):
#     try:
#         if not image:
#             print("7")
#             return None
#
#         bucket_name = src.config.BUCKET_NAME
#         s3_bucket_url = f"{src.config.S3_BASE_URL}/{bucket_name}"
#         print("8")
#         s3_client = boto3.client(
#             "s3",
#             endpoint_url=s3_bucket_url,
#             aws_access_key_id=src.config.AWS_SECRET_KEY_ID,
#             aws_secret_access_key=src.config.AWS_SECRET_ACCESS_KEY,
#         )
#         print("9")
#         s3_client.create_bucket(Bucket=bucket_name)
#         print("10")
#         file_content = await image.read()
#         print("11")
#         unique_filename = f"{str(uuid.uuid4())}.{image.filename.split('.')[-1]}"
#         print("12")
#         response = s3_client.put_object(
#             Bucket=bucket_name, Key=unique_filename, Body=file_content
#         )
#         print("13")
#         s3_path = f"http://{bucket_name}.{src.config.LOCALSTACK_HOST}/{bucket_name}/{unique_filename}"
#         print("14")
#         return s3_path
#     except ClientError as e:
#         print(e)
#         return None


async def upload_to_s3(image: UploadFile):
    try:
        if not image:
            print("7")
            return None

        bucket_name = src.config.BUCKET_NAME
        s3_base_url = src.config.S3_BASE_URL
        s3_client = boto3.client(
            "s3",
            endpoint_url=s3_base_url,
            aws_access_key_id=src.config.AWS_SECRET_KEY_ID,
            aws_secret_access_key=src.config.AWS_SECRET_ACCESS_KEY,
            verify=False
        )
        print("8")
        print("9")
        s3_client.create_bucket(Bucket=bucket_name)

        print("10")
        file_content = await image.read()
        print("11")
        unique_filename = f"{str(uuid.uuid4())}.{image.filename.split('.')[-1]}"
        print("12")
        response = s3_client.put_object(
            Bucket=bucket_name, Key=unique_filename, Body=file_content
        )
    except ClientError as e:
        print(e)
        return None


async def perform_signup(s3_file_path: str, user: CreateUser, session: AsyncSession) -> User:
    # Создаем нового пользователя с названием фотографии в S3
    print("15")
    hashed_password = hash_password(user.password)
    hashed_password_str = hashed_password.decode()
    print("16")
    new_user = User(
        name=user.name,
        surname=user.surname,
        username=user.username,
        password=hashed_password_str,
        phone_number=user.phone_number,
        email=user.email,
        role=user.role,
        group=user.group,
        s3_file_path=s3_file_path,  # Сохраняем путь к фотографии в S3
    )
    print("17")
    session.add(new_user)
    print("ййй")
    await session.commit()  # Добавляем пользователя в базу данных и фиксируем изменения
    print("цццц")
    await session.refresh(new_user)
    print("User ID:", new_user.id)
    print("ууу")
    print(f"new_user: {new_user}")
    print("кккк")
    return new_user
