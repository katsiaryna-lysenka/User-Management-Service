from pydantic import ConfigDict

from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional, ClassVar
from uuid import uuid4

from src.core.models import Role


class CreateUser(BaseModel):
    id: str = str(uuid4())  # генерирую значения поля `id` при создании объекта
    name: str
    surname: str
    username: constr(min_length=3, max_length=20)
    password: str
    phone_number: str
    email: EmailStr
    role: Role
    group: str
    image_path: Optional[str] = None
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None


class UserSchema(BaseModel):
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class Partial(BaseModel):
    extra: ClassVar[str] = "ignore"


class LoginInput(Partial):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str


class UserInfo(BaseModel):
    id: str
    name: str
    surname: str
    username: str
    email: str
    phone_number: str
    role: str
    group: str


class UpdateUser(BaseModel):
    name: str
    surname: str
    username: constr(min_length=3, max_length=20)
    password: str
    phone_number: str
    email: EmailStr
    role: str
    group: str
    is_blocked: bool = False
    modified_at: Optional[datetime] = None


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
