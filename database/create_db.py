from core.models.base import Base
from core.config import engine
import asyncio


async def create_db():

    async with engine.begin() as conn:
        from core.models import Group, Role, User, DatabaseHelper

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


asyncio.run(create_db())
