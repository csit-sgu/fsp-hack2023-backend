from dataclasses import dataclass
from db.models import Claims

@dataclass
class User:
  email: str
  password: str
  claims: list = [ Claims.ATHLETE ]
  