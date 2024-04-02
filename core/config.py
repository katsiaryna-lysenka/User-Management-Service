import os
from os import getenv
from typing import Optional, Dict, Any

from pydantic_settings import BaseSettings
from sqlalchemy.sql.functions import user


class Settings(BaseSettings):
    db_url: str = f"postgresql+asyncpg://postgres:12345@postgresql:5432/postgres"

    # db_echo: bool = False
    db_echo: bool = True


settings = Settings()
