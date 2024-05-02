import uuid
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from sqlalchemy import String, DateTime, UUID, func


class ResetPasswordMessage(Base):
    __tablename__ = 'reset_password_messages'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    email_address: Mapped[String] = mapped_column(String(255), nullable=False)
    subject: Mapped[String] = mapped_column(String(255), nullable=False)
    body: Mapped[String] = mapped_column(String, nullable=False)
    published_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    sent_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

