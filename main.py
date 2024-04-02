from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from items_views import router as items_router
import uvicorn
from users.views import router as users_router
from core.models import Base, db_helper, Group, User, Role, DatabaseHelper


app = FastAPI()
# app.include_router(router=router_v1, prefix=settings.api_v1_prefix)
app.include_router(items_router)
app.include_router(users_router)


@app.get("/")
def hello_index():
    return {
        "message": "Hello index!",
    }


@app.get("/hello")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}!"}


@app.get("/calc/add")
def add(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=5000, host="0.0.0.0")
