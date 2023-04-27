from dataclasses import dataclass
from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Integer, Column, DateTime,  Enum
from datetime import datetime
from enum import Enum

Base = declarative_base()

class Claims(Enum):
    ATHLETE = 1
    REPRESENTATIVE = 2
    ADMINISTRATOR =  3
    PARTNER = 4

class User(Base):
    __tablename__ = 'users'
    uid = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    
    date_reg = Column(DateTime(), default=datetime.now, nullable=False)
    date_login = Column(DateTime(), default=datetime.now, 
            onupdate=datetime.now, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    athlete_FK = Column(Integer, nullable=True)
    representative_FK = Column(Integer, nullable=True)
    administrator_FK = Column(Integer, nullable=True)
    partner_FK = Column(Integer, nullable=True)
    email = Column(String(255), nullable=False)