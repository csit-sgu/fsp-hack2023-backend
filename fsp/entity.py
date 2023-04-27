from dataclasses import dataclass


@dataclass
class User:
  email: str
  password: str
  first_name: int = None
  last_name: int = None
