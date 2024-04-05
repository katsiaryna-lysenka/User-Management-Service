from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.views import get_username_by_static_auth_token, get_auth_user_username
from core.models import User
from users import crud
from users.schemas import CreateUser, UserSchema

router = APIRouter(prefix="/users", tags=["Users"])


class UserBase(BaseModel):
    name: str
    surname: str
    username: str
    phone_number: str
    email: str
    role: str
    group: str
    image_s3_path: Optional[str]
    is_blocked: bool


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


@router.post("/")
def create_user(user: CreateUser):
    return crud.create_user(user_in=user)


# @router.get("/me", response_model=User)
# def read_users_me(
#     current_user: str = Depends(get_username_by_static_auth_token),
# ):
#     user = crud.get_user_by_username(current_user)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
