from sqlalchemy import select, update

from .entity import User, Event
from .db.models import User as UserDB, Event as EventDB
from .db.models import Claim, Athlete, Admin, Representative, Partner

class Service():

    def __init__(self, T, session):
        self._T = T
        self._session = session

    def get_by_guid(self, guid: int):
        with self._session() as session:
            user = session.execute(select(self._T).where(self._T.guid == guid))
            return user

class ClaimService():

    def __init__(self, session):
        self._session = session
    
    def set_role_by_claims(self, db_user: UserDB, claims: list[Claim]):
        with self._session() as session:
            if Claim.ATHLETE in claims:
                athlete = Athlete()
                session.add(athlete)
                db_user.athlete_FK = athlete.id
            if Claim.ADMINISTRATOR in claims:
                admin = Admin()
                session.add(admin)
                db_user.administrator_FK = admin.id
            if Claim.REPRESENTATIVE in claims:
                repr = Representative()
                session.add(repr)
                db_user.representative_FK = repr.id
            if Claim.PARTNER in claims:
                partner = Partner()
                session.add(partner)
                db_user.partner_FK = partner.id
            print(f'Set foreign keys for the user: {db_user}')
            session.commit()


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
        with self._session as session:
            session.add(event)
            session.commit()
            
    def get(self, page, per_page):
        with self._session as session:
            result = session.execute(select(self._T)
                .offset(page * per_page) 
                .limit(per_page)).all()
            
            return result
    
class ServiceManager:
    
    def __init__(self, session, services=[]) -> None:
        self.services = dict(zip(services, map(lambda service: service(session), services)))
        self.session = session
          
    def get(self, required_type):
        if required_type not in self.services:
            self.services.update({required_type : required_type(self.session)})
        
        return self.services[required_type]
