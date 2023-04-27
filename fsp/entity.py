from dataclasses import dataclass


@dataclass
class User:
  login: str
  password: str
  first_name: int
  last_name: int
