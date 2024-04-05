from datetime import datetime
from typing import Annotated, Optional
from uuid import uuid4

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict

from core.models.role import State


class CreateUser(BaseModel):
    id: str
    name: str
    surname: str
    username: Annotated[str, MinLen(3), MaxLen(20)]
    phone_number: str
    email: EmailStr
    role: State
    group: str
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(uuid4())


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
