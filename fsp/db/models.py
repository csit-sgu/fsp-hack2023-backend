from dataclasses import dataclass
from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Integer, Column, DateTime,  Enum, LargeBinary
from datetime import datetime
from enum import Enum

Base = declarative_base()

class Claims(Enum):
    ATHLETE = 1
    REPRESENTATIVE = 2
    ADMINISTRATOR =  3
    PARTNER = 4

class Gender(Enum):
    MALE = 1
    FEMALE = 2

class Role(Enum):
    MEMBER = 1
    LEAD = 2

class State(Enum):
    WAIT = 1
    CHANGES_NEEDED = 2
    REJECT = 3 
    CONFIRMED = 4
Base = DeclarativeBase()

@dataclass
class Team(base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True)
    datetime_create = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)

@dataclass
class Athlete(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    team_FK = Column(Integer, ForeignKey(Team.id), nullable=False)
    rating = Column(Integer, nullable=True)
    role = Column(Role(Enum), nullable=False)

@dataclass
class Admin(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    
@dataclass
class Representative(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

@dataclass
class Partner(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

@dataclass
class Personal(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    phone = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    passport = Column(String(255), nullable=False)
    birthday = Column(Date(), nullable=False)
    gender = Column(Gender(Enum), nullable=True)
    organization = Column(String(255), nullable=False)
    skills = Column(Text, nullable=False)
    about = Column(Text, nullable=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    pathernal = Column(String(255), nullable=True)

@dataclass
class User(Base):
    uid = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date_reg = Column(DateTime, default=datetime.now, nullable=False)
    date_login = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    athlete_FK = Column(Integer, ForeignKey(Athlete.id), nullable=True)
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=True)
    administrator_FK = Column(Integer, ForeignKey(Admin.id), nullable=True)
    partner_FK = Column(Integer,ForeignKey(Partner.id),nullable=True)
    personal_FK = Column(Integer, ForeignKey(Personal.id), nullable=True)
    email: Column(String(255), nullable=False)

@dataclass
class Events(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    date_create = Column(Date, default=datetime.datetime.now().date(), nullable=False)
    date_start = Column(Date, nullable=True)
    date_end = Column(Date, nullable=True)
    location = Column(String(255), nullable=True)
    about = Column(String(255), nullable=True)

@dataclass
class EventRequest(Base):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ev_id = Column(Integer, ForeignKey(Events.id), nullable=True)
    state = Column(State(Enum), nullable=True)
    datetime_create = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=False)


@dataclass
class EventConcats(Base):
    user_id = Column(Integer, ForeignKey(), nullable=False)
    ev_id = Column(Integer, nullable=False)

@dataclass
class EventTeams(Base):
    ev_id_FK = Column(Integer, ForeignKey(Events.id), nullable=False)
    team_id_FK = Column(Integer, ForeignKey(Team.id), nullable=False)


