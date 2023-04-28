import jwt
import os

from datetime import datetime, timedelta
from .db.models import Claim
<<<<<<< HEAD
from .settings import config
=======

_SECRET = os.environ.get("SECRET")
if _SECRET is None:
    raise RuntimeError("Please, set the SECRET environment variable")

>>>>>>> dd2bb88 (Проверенные эндпоинты + начало функционала работа с командами)

class JWT:
    @staticmethod
    def create(claims: dict) -> str:
<<<<<<< HEAD
        curr_time = datetime.now(tz=datetime.timezone.utc)
        delta = timedelta(seconds=config.token_expiration_time_sec)

        return jwt.encode(
            {
                **claims,
                'iat': curr_time,
                'exp': curr_time + delta
            },
            config.secret,
            algorithm="HS256"
        )
=======
        return jwt.encode(claims, _SECRET, algorithm="HS256")
>>>>>>> dd2bb88 (Проверенные эндпоинты + начало функционала работа с командами)

    @staticmethod
    def extract(token: str | None) -> dict | None:
        if token is None:
            return None

        try:
<<<<<<< HEAD
            return jwt.decode(token, config.secret, algorithms=["HS256"])
=======
            return jwt.decode(token, _SECRET, algorithms=["HS256"])
>>>>>>> dd2bb88 (Проверенные эндпоинты + начало функционала работа с командами)
        except jwt.InvalidTokenError as e:
            print(f"Not decoding the token: {e}")
            return None
