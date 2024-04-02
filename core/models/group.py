import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, func, UUID, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[String] = mapped_column(String, unique=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
