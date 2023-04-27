import json

from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Integer, Column, DateTime, \
        LargeBinary, Text, ForeignKey, Date, PrimaryKeyConstraint

from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum

from dataclasses import dataclass

Base = declarative_base()

@dataclass
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

class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True)
    datetime_create = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)

class Athlete(Base):
    __tablename__ = 'athlete'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    team_FK = Column(Integer, ForeignKey(Team.id), nullable=False)
    rating = Column(Integer, nullable=True)
    role = Column(SQLEnum(Role), nullable=False)

class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    
class Representative(Base):
    __tablename__ = 'representative'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

class Partner(Base):
    __tablename__ = 'partner'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

class Profile(Base):
    __tablename__ = 'profile'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    phone = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    passport = Column(String(10), nullable=False)
    birthday = Column(Date(), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=True)
    organization = Column(String(255), nullable=False)
    skills_FK = Column(Integer, nullable=True)
    about = Column(Text, nullable=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    patronymic = Column(String(255), nullable=True)
    insurance = Column(String(16), nullable=False)

class User(Base):
    __tablename__ = 'users'
    
    uid = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date_reg = Column(DateTime, default=datetime.now, nullable=False)
    date_login = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    athlete_FK = Column(Integer, ForeignKey(Athlete.id), nullable=True)
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=True)
    administrator_FK = Column(Integer, ForeignKey(Admin.id), nullable=True)
    partner_FK = Column(Integer,ForeignKey(Partner.id),nullable=True)
    personal_FK = Column(Integer, ForeignKey(Profile.id), nullable=True)
    email =  Column(String(255), nullable=False)

class Event(Base):
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    date_create = Column(DateTime, default=datetime.now().date, nullable=False)
    date_started = Column(DateTime, nullable=True)
    date_ended = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    about = Column(String(255), nullable=True)

class EventRequest(Base):
    __tablename__ = 'event_request'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=True)
    state = Column(SQLEnum(State), nullable=True)
    datetime_create = Column(DateTime, default=datetime.now, 
            onupdate=datetime.now, nullable=False)
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=False)

class EventTeam(Base):
    __tablename__ = 'event_team'
    
    event_id_FK = Column(Integer, ForeignKey(Event.id), nullable=False, primary_key=True)
    team_id_FK = Column(Integer, ForeignKey(Team.id), nullable=False, primary_key=True)
    
    __table_args__ = (
        PrimaryKeyConstraint(event_id_FK, team_id_FK), 
    )
