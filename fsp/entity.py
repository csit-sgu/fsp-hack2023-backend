from dataclasses import dataclass, field
from db.models import Claims

@dataclass
class User:
  email: str
  password: str
  claims: list =field(default_factory=lambda: [Claims.ATHLETE])
  