from sqlalchemy import select

from entity import User
from db.models import User as UserDB

from sqlalchemy.exc import NoResultFound

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

    def get_by_login(self, login: str):
        with self._session() as session:
            try:
                user: UserDB = session.execute(select(self._T).where(self._T.login == login)).one()
            except NoResultFound:
                return None 
            return User(user.email, user.password)
        
    def add(self, user: User) -> bool:
        print(user.email, user.password)
        model = UserDB(
            hashed_password=user.password,
            email=user.email
        )
        
        # TODO: first_name, last_name

        with self._session() as session:
            session.add(model)
            session.commit()

