import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

# BASE_DIR = Path("/home/user/PycharmProjects/User_management/")


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithms: str = "RS256"
    access_token_expire_minutes: int = 15


class Settings(BaseSettings):
    db_url: str = f"postgresql+asyncpg://postgres:12345@postgresql:5432/postgres"

    # db_echo: bool = False
    db_echo: bool = True

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
