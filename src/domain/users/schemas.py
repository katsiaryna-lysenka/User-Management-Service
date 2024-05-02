from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, constr
from typing import Optional, ClassVar

from src.infrastructure.models import Role


class CreateUser(BaseModel):
    name: str
    surname: str
    username: constr(min_length=3, max_length=20)
    password: constr(min_length=8, max_length=12)
    phone_number: str
    email: EmailStr
    role: Role
    group: str = "Cat"


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
    group: str = "Cat"
    is_blocked: bool = False


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class NewPasswordRequest(BaseModel):
    password: str