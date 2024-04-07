from pydantic import ConfigDict

from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional
from uuid import uuid4


class CreateUser(BaseModel):
    id: str = str(uuid4())  # генерирую значения поля `id` при создании объекта
    name: str
    surname: str
    username: constr(min_length=3, max_length=20)
    password: str
    phone_number: str
    email: EmailStr
    role: str
    group: str
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    class Config:
        # добавляю параметр `allow_mutation=False`, чтобы предотвратить мутацию объекта
        allow_mutation = False


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


class Partial(BaseModel):
    class Config:
        extra = "ignore"


class LoginInput(Partial):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str

    class Config:
        orm_mode = True


class UserInfo(BaseModel):
    id: str
    name: str
    surname: str
    username: str
    email: str
    phone_number: str
    role: str
    group: str
