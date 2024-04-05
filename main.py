from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

from core.config import settings
from healthcheck.views import router
import uvicorn
from users.views import router as users_router
from api_v1.demo_auth.demo_jwt_auth import router as jwt_router
from core.models import Base, db_helper, Group, User, Role, DatabaseHelper
from api_v1.demo_auth.views import router as router_v1
from auth.views import router


app = FastAPI()
app.include_router(router=router_v1)
app.include_router(users_router)
app.include_router(jwt_router)
app.include_router(router=router)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=5000, host="0.0.0.0")
