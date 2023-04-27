from flask import Request, abort, request

from .db.models import Claim
from .utils import is_none_or_empty
from .token import JWT

class CheckFields:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.content_type.lower() == "application/json":
            if request.json is None or any([d is None for d in dict(request.json).values()]):
                abort(400, 'Неверный формат запроса')

        return self.app(environ, start_response)

def auth_required(whitelist: list[Claim]):
    def decorator(f):
        def _wrapper(*args, **kwargs):
            token = request.json['token']
            if is_none_or_empty(token):
                return 'Пожалуйста, предоставьте JSON токен', 400

            data = JWT.extract(token)
            if data is None:
                return 'Недействительный токен', 401
            
            if any([str(wl.value) in data['claims'] for wl in whitelist]):
                return f(data['email'], *args, **kwargs)
        return _wrapper
    return decorator
