import json

from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    String,
    Integer,
    Column,
    DateTime,
    LargeBinary,
    ForeignKey,
    Date,
    PrimaryKeyConstraint,
)

from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from enum import Enum

from dataclasses import dataclass

Base = declarative_base()


@dataclass
class Claim(Enum):
    ATHLETE = 1
    REPRESENTATIVE = 2
    ADMINISTRATOR = 3
    PARTNER = 4

    def serialize(self) -> str:
        if self == Claim.ATHLETE:
            return 'ATHLETE'
        if self == Claim.REPRESENTATIVE:
            return 'REPRESENTATIVE'
        if self == Claim.ADMINISTRATOR:
            return 'ADMINISTRATOR'
        if self == Claim.PARTNER:
            return 'PARTNER'


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class Role(Enum):
    MEMBER = "member"
    LEAD = "lead"


class State(Enum):
    WAIT = "wait"
    CHANGES_NEEDED = "changes_needed"
    REJECT = "reject"
    CONFIRMED = "confirmed"


class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    rating = Column(Integer, nullable=True)
    datetime_create = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )


class Athlete(Base):
    __tablename__ = "athlete"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    rating = Column(Integer, nullable=True)
    role = Column(SQLEnum(Role), nullable=False)

class AthleteTeams(Base):
    __tablename__ = "athlete_teams"
    athlete_id_FK = Column(Integer, primary_key=True, nullable=False)
    team_id_FK = Column(Integer, primary_key=True, nullable=False)
    role = Column(SQLEnum(Role), nullable=False)

    __table_args__ = (PrimaryKeyConstraint(athlete_id_FK, team_id_FK),)


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class Representative(Base):
    __tablename__ = "representative"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class Partner(Base):
    __tablename__ = "partner"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    phone = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    passport = Column(String(10), nullable=False)
    birthday = Column(Date(), nullable=False)
    gender = Column(SQLEnum(Gender), nullable=True)
    organization = Column(String(255), nullable=False)
    skills = Column(Integer, nullable=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    patronymic = Column(String(255), nullable=True)
    insurance = Column(String(16), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    date_reg = Column(DateTime, default=datetime.now, nullable=False)
    date_login = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    hashed_password = Column(LargeBinary, nullable=False)
    athlete_FK = Column(Integer, ForeignKey(Athlete.id), nullable=True)
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=True)
    administrator_FK = Column(Integer, ForeignKey(Admin.id), nullable=True)
    partner_FK = Column(Integer, ForeignKey(Partner.id), nullable=True)
    personal_FK = Column(Integer, ForeignKey(Profile.id), nullable=True)
    email = Column(String(255), nullable=False)


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(255), nullable=False)
    date_create = Column(DateTime, default=datetime.now().date, nullable=False)
    date_started = Column(DateTime, nullable=True)
    date_ended = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    about = Column(String(255), nullable=True)


class EventRequest(Base):
    __tablename__ = "event_request"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=True)
    state = Column(SQLEnum(State), nullable=True)
    datetime_create = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    representative_FK = Column(Integer, ForeignKey(Representative.id), nullable=True)
    partner_FK = Column(Integer, ForeignKey(Partner.id), nullable=True)


class EventTeam(Base):
    __tablename__ = "event_team"

    event_id_FK = Column(
        Integer, ForeignKey(Event.id), nullable=False, primary_key=True
    )
    team_id_FK = Column(Integer, ForeignKey(Team.id), nullable=False, primary_key=True)

    __table_args__ = (PrimaryKeyConstraint(event_id_FK, team_id_FK),)
