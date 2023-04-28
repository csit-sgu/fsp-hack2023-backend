import jwt
import os

from datetime import datetime, timedelta
from .db.models import Claim
from .settings import config

class JWT:
    @staticmethod
    def create(claims: dict) -> str:
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

    @staticmethod
    def extract(token: str | None) -> dict | None:
        if token is None:
            return None

        try:
            return jwt.decode(token, config.secret, algorithms=["HS256"])
        except jwt.InvalidTokenError as e:
            print(f"Not decoding the token: {e}")
            return None
