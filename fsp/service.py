from sqlalchemy import select

from entity import User, Event
from db.models import User as UserDB, \
    Event as EventDB, \
    Profile as ProfileDB

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
            rows = session.execute(select(self._T).where(self._T.email == email)).fetchone()
            if rows is not None:
                return User(rows[0].email, rows[0].hashed_password)
            else:
                return None
            
    def add(self, user: User):
        model = UserDB(
            hashed_password=user.password,
            email=user.email
        )

        with self._session() as session:
            session.add(model)
            session.commit()
            
class EventService(Service):
    
    def __init__(self, session):
        super().__init__(EventDB, session)
        
    def add(self, event: Event):
        
        with self._session() as session:
            session.add(EventDB(
                name=event.name,
                date_started=event.date_started,
                date_ended = event.date_ended,
                location=event.location,
                about=event.about
            ))
            session.commit()
            
    def get(self, page, per_page):
        with self._session() as session:
            result = session.execute(select(self._T)
                .offset(page * per_page) 
                .limit(per_page)).all()
            
            return result
        
class ProfileService(Service):
    def __init__(self, T, session):
        super().__init__(ProfileService, session)
        
    # def add(self, profile: Profile):
    
class ServiceManager:
    
    def __init__(self, session, services=[]) -> None:
        self.services = dict(zip(services, map(lambda service: service(session), services)))
        self.session = session
          
    def get(self, required_type):
        if required_type not in self.services:
            self.services.update({required_type : required_type(self.session)})
        
        return self.services[required_type]
