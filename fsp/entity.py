from dataclasses import dataclass, field
from db.models import Claims

from datetime import datetime

from db.models import Gender

@dataclass
class User:
  email: str
  password: str
  claims: list = field(default_factory=lambda: [Claims.ATHLETE])
  
@dataclass
class Event:
  name: str
  date_started: str
  date_ended: str
  location: str
  about: str
    
@dataclass
class Profile:
  phone: str
  address: str
  passport: str
  birthday: datetime.date
  gender: Gender
  organization: str
  name: str
  surname: str
  patronymic: str
  insurance: str