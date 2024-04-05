from datetime import timedelta, datetime

import jwt
import bcrypt
from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithms: str = settings.auth_jwt.algorithms,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    to_encoded = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encoded.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encoded,
        private_key,
        algorithms=algorithms,
    )

    return encoded


def decode_jwt(
    token: str | bytes,
    private_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithms: str = settings.auth_jwt.algorithms,
):
    decoded = jwt.decode(
        token,
        private_key,
        algorithms=[algorithms],
    )

    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
