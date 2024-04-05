from core.models import user, User
from users.schemas import CreateUser


# def create_user(user_in: CreateUser) -> dict:
#     user = user_in.model_dump()
#     return {
#         "success": True,
#         "user": user,
#     }

from core.config import settings

db_url = settings.db_url


def create_user(user_in: CreateUser) -> dict:
    # db_url.add(user_in)
    # db_url.commit()
    # db_url.refresh(user_in)
    # db_url.close()
    return {
        "success": True,
        "user": user_in,
    }
