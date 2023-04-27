from dataclasses import dataclass, field
from db.models import Claims

from datetime import datetime

@dataclass
class User:
  email: str
  password: str
  claims: list = field(default_factory=lambda: [Claims.ATHLETE])
  
@dataclass
class Event:
  name: str
  date_started: datetime
  date_ended: datetime
  location: str
  about: str
  
  def __post_init__(self):
    self.date_started = datetime.strptime(self.date_started, '%y/%m/%d %H:%M:%S')
    self.date_ended = datetime.strptime(self.date_ended, '%y/%m/%d %H:%M:%S')