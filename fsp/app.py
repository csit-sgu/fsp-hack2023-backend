import os
from flask import Flask, request, session, abort
from flask_cors import CORS

from db.utils import init_connection
from utils import is_none_or_empty, hash_password, make_default_asserts
from service import ServiceManager, UserService, EventService

from entity import User, Event

import bcrypt

app = Flask(__name__)
CORS(app)

secret = os.environ.get('SECRET')
if secret is None:
    raise RuntimeError('Please, set the SECRET environment variable')
app.secret_key = secret

engine, sess = init_connection('postgresql+psycopg2://postgres:postgres@localhost/postgres')

services = ServiceManager(sess)

@app.post('/auth/login')
def login():
    """
    Аутентифицирует пользователя по `login` и `password`.
    Проверяет предоставленный логин, в случае успеха
    устанавливает поля `login` и `claims` во Flask
    session-куки.

    400 Bad Request, если логин неверный или пользователя с
    именем `login` не существует.
    """
    
    user_service = ServiceManager.get(UserService)
    
    body = request.json
    
    make_default_asserts(body)
        
    password = body['password']
    email = body['email']

    # логин или пароль не предоставлены
    if is_none_or_empty(email) or is_none_or_empty(password):
        abort(400)
        
    user = user_service.get_by_login(email)
    # пользователя с таким именем не существует
    if user is None:
        abort(400)


    hashed_password = user.password
    
    if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        abort(400)

    session['email'] = user.email
    session['claims'] = user.claims
    
    return '', 200

@app.post('/auth/register')
def register():
    """
    Регистрирует нового пользователя по `login` и `password`.
    Возможно добавить `first_name`, `last_name` и другую
    обязательную информацию.
    
    При успешной регистрации ответ 201 Created.
    Если имя занято, возвращает 400 Bad Request.
    """
    
    user_service = ServiceManager(UserService)

    body = dict(request.json)
    make_default_asserts(body)
    
    user: User = user_service.get_by_login(body['email'])

    # Если пользователь уже существует
    if user is not None:
        abort(400, "Этот пользователь уже существует")

    body['password'] = hash_password(body['password'])

    try:
        user = User(**body)
        ok = user_service.add(user)
    except Exception as e:
        print(e)
        abort(400, e)
    
    ok = True

    return ('', 201) if ok else ('', 400)

@app.post('/events')
def add_event():
    
    event_service: EventService = ServiceManager.get(EventService)
    
    body = dict(request.json)
    
    try:
        event = Event(**body)
        response = event_service.add(Event(**body))
    except Exception as e:
        abort(400, e)
        
@app.get('/events')
def get_event():
    
    event_service: EventService = ServiceManager.get(EventService)
    
    page = request.args.get('page')
    per_page = request.args.get('per_page')
    
    body = dict(request.json)
    
    try:
        event = Event(**body)
        response = event_service.get(page, per_page)
    except Exception as e:
        abort(400, e)