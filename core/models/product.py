from sqlalchemy.orm import Mapped

from .base import Base


class Product(Base):
    __tablname__ = "products"

    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
