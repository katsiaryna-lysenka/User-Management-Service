import enum
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
