from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, String, Integer, Column, Text, DateTime, Boolean, Enum
from datetime import datetime
import enum

class Claims(enum.Enum):
    ATHLETE
    REPRESENTATIVE 
    ADMINISTRATOR
    PARTNER

Base = DeclarativeBase()

@dataclass
class User(Base):
    uid = Column(Integer, primary_key=True, nullable=False)
    claims = Column(Enum(Claims),nullable=False)
    date_reg = Column(DateTime(), default=datetime.now, nullable=False)
    date_login = Column(DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    athlete_FK = Column(Integer, nullable=True)
    representative_FK = Column(Integer, nullable=True)
    administrator_FK = Column(Integer, nullable=True)
    partner_FK = Column(Integer, nullable=True)
    email: Column(String(255), nullable=False)