import os

from flask import Flask, request, session, abort
from flask_cors import CORS

from .db.utils import init_connection
from .utils import is_none_or_empty, hash_password
from .service import UserService, EventService, ServiceManager

from .db.models import Event
from .entity import User, Claim
from .middleware import CheckFields, auth_required
from .token import JWT
from .logger import logger

import bcrypt

app = Flask(__name__)
app.wsgi_app = CheckFields(app.wsgi_app) # проверка на пустоту JSON-объектов

CORS(app)

log = logger(app)

secret = os.environ.get('SECRET')
if secret is None:
    raise RuntimeError('Please, set the SECRET environment variable')
app.secret_key = secret

engine, sess = init_connection('postgresql+psycopg2://postgres:postgres@localhost/postgres')

services = ServiceManager(sess)

@app.post('/auth/login')
def login():
    user_service = services.get(UserService)
    
    body = request.json
    password = body['password']
    email = body['email']
        
    user: User = user_service.get_by_login(email)

    hashed_password = user.password
    
    if user is None or not bcrypt.checkpw(password.encode('utf-8'), 
                                          hashed_password):
        
        abort(400, "Пользователь не существует или не найден")

    token = JWT.create({ 'email': user.email, 'claims': user.claims })

    return { 'token': token }, 200

@app.post('/auth/register')
def register():
    user_service = services.get(UserService)

    body = dict(request.json)

    user: User = user_service.get_by_login(body['email'])

    # Если пользователь уже существует
    if user is not None:
        abort(400, "Этот пользователь уже существует")

    body['password'] = hash_password(body['password'])

    try:
        user = User(**body)
        ok = user_service.add(user)
    except NameError:
        abort(400, "Неверный набор аргументов")
    except Exception:
        abort(400, "Непредвиденная ошибка на сервере")

    return ('', 201) if ok else ('', 400)

@auth_required([Claim.ADMINISTRATOR, Claim.REPRESENTATIVE, Claim.PARTNER])
@app.post('/events')
def add_event(email: str):

    event_service: EventService = services.get(EventService)
    
    body = dict(request.json)
    
    try:
        event_service.add(Event(**body))
    except Exception as e:
        abort(400, e)

@auth_required([Claim.ADMINISTRATOR, Claim.PARTNER, Claim.ATHLETE, Claim.REPRESENTATIVE])
@app.get('/events')
def get_event(email: str):
    
    event_service: EventService = services.get(EventService)
    
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    
    try:
        response = event_service.get(page, per_page)
        return response
    except Exception as e:
        abort(400, e)
