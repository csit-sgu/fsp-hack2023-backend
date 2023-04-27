from dataclasses import dataclass, field
from db.models import Claims

from datetime import date, datetime

@dataclass
class User:
  email: str
  password: str
  claims: list = field(default_factory=lambda: [Claims.ATHLETE])
  
@dataclass
class Event:
  id: int
  date_created: datetime
  date_started: datetime
  date_ended: datetime
  location: str
  about: str