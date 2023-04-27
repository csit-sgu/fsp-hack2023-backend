from sqlalchemy import select

from entity import User
from db.models import User as UserDB

class Service():

    def __init__(self, T, session):
        self._T = T
        self._session = session

    def get_by_guid(self, guid: int):
        with self._session() as session:
            user = session.execute(select(self._T).where(self._T.guid == guid))
            return user

class UserService(Service):

    def __init__(self, session):
        super().__init__(UserDB, session)

    def get_by_login(self, email: str) -> User:
        with self._session() as session:
            row = session.execute(select(self._T).where(self._T.email == email)).fetchone()
            if row is not None:
                
                return User(row[0].email, row[0].hashed_password)
            else:
                return None
            
    def add(self, user: User) -> bool:
        print(user.email, user.password)
        model = UserDB(
            hashed_password=user.password,
            email=user.email
        )

        with self._session() as session:
            session.add(model)
            session.commit()

