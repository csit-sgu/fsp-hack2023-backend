from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .entity import User
from .db.models import User as UserDB

class AsyncService():

    def __init__(self, T, session):
        self._T = T
        self._session: AsyncSession = session

    async def get_by_guid(self, guid: int):
        async with self._session() as session:
            user = await session.execute(select(self._T).where(self._T.guid == guid))
            return user

class UserService(AsyncService):

    def __init__(self, session):
        super.__init__(UserDB, session)

    async def get_by_login(self, login: str):
        async with self._session() as session:
            user: UserDB = await session.execute(select(self._T).where(self._T.login == login))
            return User(user.email, user.hashed_password)
        
    async def add(self, user: User) -> bool:

        model = UserDB(
            hashed_password=user.password,
            email=user.login,
        )
        
        # TODO: first_name, last_name

        async with self._session() as session:
            session.add(model)
            await session.commit()

