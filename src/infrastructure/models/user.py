import uuid
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Column, Boolean, DateTime, UUID, func
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[String] = mapped_column(String)
    surname: Mapped[String] = mapped_column(String)
    username: Mapped[String] = mapped_column(String)
    password: Mapped[String] = mapped_column(String)
    phone_number: Mapped[String] = mapped_column(String(15))
    email: Mapped[String] = mapped_column(String(100))
    role: Mapped[String] = mapped_column(String(20))
    group: Mapped[String] = mapped_column(String(50))
    is_blocked: Mapped[Boolean] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
