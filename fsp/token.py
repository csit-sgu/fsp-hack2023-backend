import jwt
import os

from .db.models import Claim

_SECRET = os.environ.get("SECRET")
if _SECRET is None:
    raise RuntimeError('Please, set the SECRET environment variable')

class JWT:

    @staticmethod
    def create(claims: list[Claim]) -> str:
        return jwt.encode(claims, _SECRET, algorithm='HS256')
    
    @staticmethod
    def extract(token: str) -> dict[str, str] | None:
        try:
            return jwt.decode(token, _SECRET, algorithms=['HS256'])
        except jwt.InvalidTokenError as e:
            print(f'Not decoding the token: {e}')
            return None
