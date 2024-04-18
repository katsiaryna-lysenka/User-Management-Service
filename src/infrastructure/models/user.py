import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Column, Boolean, DateTime, UUID, func, LargeBinary
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
    phone_number: Mapped[String] = mapped_column(String)
    email: Mapped[String] = mapped_column(String)
    role: Mapped[String] = mapped_column(String)
    group: Mapped[String] = mapped_column(String)
    s3_file_path: Mapped[String] = mapped_column(String, nullable=True)
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
