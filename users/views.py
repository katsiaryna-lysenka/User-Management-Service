from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from users import crud
from users.schemas import CreateUser, UserSchema
from core.models.role import State

router = APIRouter(prefix="/users", tags=["Users"])


class UserBase(BaseModel):
    id: str
    name: str
    surname: str
    username: str
    phone_number: str
    email: EmailStr
    role: State
    group: str
    is_blocked: bool
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid4())


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
