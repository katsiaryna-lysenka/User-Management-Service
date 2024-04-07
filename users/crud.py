from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from core.models import User
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, async_session
from sqlalchemy import select
from core.config import settings

db_url = settings.db_url


class CRUD:
    async def get_all(self, async_session: async_sessionmaker[AsyncSession]):

        async with async_session() as session:
            statement = select(User).order_by(User.id)

            result = await session.execute(statement)
            users = result.scalars().all()

            return users

    async def add(self, async_session: async_sessionmaker[AsyncSession], user: User):

        async with async_session() as session:
            session.add(user)
            await session.commit()

        return user

    async def get_by_id(
        self, async_session: async_sessionmaker[AsyncSession], user_id: str
    ):

        async with async_session() as session:
            statement = select(User).filter(User.id == user_id)

            result = await session.execute(statement)

            return result.scalars().one()

    async def update(
            self, async_session: async_sessionmaker[AsyncSession], user_id, data
    ):
        async with async_session() as session:
            statement = select(User).filter(User.id == user_id)

            result = await session.execute(statement)

            user = result.scalars().one()

            user.name = data["name"]
            user.surname = data["surname"]
            user.username = data["username"]
            user.password = data["password"]
            user.phone_number = data["phone_number"]
            user.email = data["email"]
            user.role = data["role"]
            user.group = data["group"]
            user.is_blocked = data["is_blocked"]

            await session.commit()

            return user

    async def delete(self, async_session: async_sessionmaker[AsyncSession], user_id: str):
        async with async_session() as session:
            user = await session.get(User, user_id)
            if user:
                await session.delete(user)
                await session.commit()
            else:
                raise HTTPException(status_code=404, detail="User not found")

    async def get_by_login(
            self, async_session: AsyncSession, login: str
    ) -> User:

        async with async_session() as session:
            statement = select(User).filter(
                (User.username == login) | (User.email == login) | (User.phone_number == login)
            )

            result = await session.execute(statement)

            user = result.scalars().first()
            if user is None:
                raise ValueError("User not found")

            return user

    async def get_user(self, async_session: async_sessionmaker[AsyncSession], user_id: str) -> User:
        async with async_session() as session:
            statement = select(User).filter(User.id == user_id)
            result = await session.execute(statement)
            user = result.scalars().one_or_none()
            if not user:
                raise ValueError(f"User with id {user_id} not found")
            return user

    async def get_user_info_by_id(self, async_session: async_sessionmaker[AsyncSession], user_id: str) -> dict:
        try:
            if not user_id:
                raise ValueError("User ID is not provided")

            user = await self.get_user(async_session, user_id)
            if not user:
                raise ValueError("User not found in database")

            user_info = {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
                "group": user.group
            }
            return user_info
        except NoResultFound:
            raise ValueError("User not found in database")
        except ValueError as ve:
            raise ValueError(f"An error occurred: {ve}")
        except SQLAlchemyError as se:
            raise ValueError(f"A database error occurred: {se}")
        except AttributeError as ae:
            raise ValueError(f"Attribute error occurred: {ae}")
        except Exception as e:
            raise ValueError(f"An unexpected error occurred while fetching user information: {e}")

    async def get_by_group(
        self, async_session: async_sessionmaker[AsyncSession], current_user_group: str
    ):

        async with async_session() as session:
            statement = select(User).filter(User.group == current_user_group)

            result = await session.execute(statement)

            return result.scalars().all()


