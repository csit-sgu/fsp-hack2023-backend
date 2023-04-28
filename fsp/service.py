from sqlalchemy import select, update

from .entity import User, Event, Profile, EventRequest
from .db.models import User as UserDB, \
        Event as EventDB, \
        Profile as ProfileDB, \
        EventRequest as EventRequestDB
from .db.models import Claim, Athlete, Admin, Representative, Partner, Team, AthleteTeams

from .utils import retrieve_fields, collect_results

class Service():

    def __init__(self, T, session):
        self._T = T
        self._session = session

    def get_by_id(self, id: int):
        with self._session() as session:
            entity = session.execute(select(self._T).where(self._T.id == id)).fethone()
            if entity[0] is not None:
                return entity[0]
            else:
                return None


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
    def __init__(self, session):
        super().__init__(ProfileDB, session)
        
        
    def update(self, email, fields):
        with self._session() as session:
            row = session.execute(select(UserDB).where(UserDB.email == email)).fetchone()
            user: UserDB = row[0]
            profile = session.execute(select(self._T)
                    .where(self._T.id == user.id)).fetchone()
            if profile is None:
                
                session.add(ProfileDB(id=user.id, **fields))
            else:
                session.query(ProfileDB).update(fields)
            session.commit()
                
    def get(self, email):
        with self._session() as session:
            result = session.execute(select(self._T)
                    .where(self._T.email == email)).fetchone()
            try:
                profile: ProfileDB = result[0]
                return Profile(
                    profile.phone, 
                    profile.address, 
                    profile.passport,
                    profile.birthday,
                    profile.gender,
                    profile.organization,
                    profile.name,
                    profile.surname,
                    profile.patronymic,
                    profile.insurance)
            except:
                return None
            
class RequestService(Service):
    def __init__(self, session) -> None:
        super().__init__(EventRequestDB, session)

    
    def add(self, event_request: EventRequest):
        with self._session() as session:
            session.add(EventRequestDB(**retrieve_fields(event_request)))
            session.commit()
            
    def get_requests(self, email):
        with self._session as session:
            user: UserDB = session.execute(select(UserDB)
                                           .where(UserDB.email == email)) \
                    .fetch_one()[0]
            
        id = user.id
        rows = session.execute(select(self._T).where(self._T.id == id)).all()
        
        return collect_results(self._T, rows)
        
    def add(self, event_request):
        pass


class AthleteService(Service):
    def __init__(self, session) -> None:
        super().__init__(Athlete, session)

    def get(self, page: int, per_page: int, order: bool = False) -> list[Athlete]:
        with self._session() as session:
            result = session.execute(
                select(self._T)
                .order_by(Athlete.rating if order else Athlete.rating.desc())
                .offset(page * per_page)
                .limit(per_page)
            ).all()
            
            return result

class TeamService(Service):
    def __init__(self, session) -> None:
        super().__init__(Team, session)

    def get(self, page: int, per_page: int, order: bool = False) -> list[Team]:
        with self._session() as session:
            result = session.execute(
                select(self._T)
                .order_by(Team.rating if order else Team.rating.desc())
                .offset(page * per_page)
                .limit(per_page)
            ).all()
            
            return result
        
    def get_by_name(self, name: str) -> Team | None:
        with self._session() as session:
            rows = session.execute(
                select(self._T).where(Team.name == name)
            ).fetchone()

            if rows[0] is not None:
                return rows[0]
            else:
                return None
        
class AthleteTeamsService:

    def __init__(self, session) -> None:
        super().__init__(Team, session)

    def get_all_by_team_id(self, team_id: int) -> list[AthleteTeams]:
        with self._session() as session:
            rows = session.execute(
                select(self._T).where(AthleteTeams.team_id_FK == team_id)
            ).all()

            return rows

class ServiceManager:
    def __init__(self, session, services=[]) -> None:
        self.services = dict(zip(services, map(lambda service: service(session), services)))
        self.session = session
          
    def get(self, required_type):
        if required_type not in self.services:
            self.services.update({required_type : required_type(self.session)})
        
        return self.services[required_type]