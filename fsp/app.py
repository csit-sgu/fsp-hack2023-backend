import os

from flask import Flask, request, session, abort
from flask_cors import CORS

import json

from .db.utils import init_connection
from .utils import  hash_password, retrieve_fields

from sqlalchemy import Row
from .service import ServiceManager, UserService, EventService, ProfileService, RequestService
from .settings import config

from .db.models import Event
from .entity import User, Claim, EventRequest
from .middleware import CheckFields, auth_required
from .token import JWT

from sqlalchemy import Row
from typing import List
import bcrypt

app = Flask(__name__)
app.wsgi_app = CheckFields(app.wsgi_app) # проверка на пустоту JSON-объектов
CORS(app, supports_credentials=True)

app.secret_key = config.secret

engine, sess = init_connection(
    f'{config.database_dialect}+{config.database_driver}://' + 
    f'{config.database_admin_username}:{config.database_admin_password}@' +
    f'{config.database_url}/{config.database_name}'
)

services = ServiceManager(sess)

@app.post('/auth/login')
def login():
    user_service = services.get(UserService)
    
    body = dict(request.json)
    password = body['password']
    email = body['email']
        
    user: User = user_service.get_by_login(email)
    
    if user is None or not bcrypt.checkpw(password.encode('utf-8'), 
                                          user.password):
        
        abort(400, "Пользователь не существует или не найден")
    
    
    claims = list(map(lambda x: x.value, user.claims))
    
    token = JWT.create({'email': user.email, 'claims': claims})

    return {'token': token}, 200

@app.post('/auth/register')
def register():
    user_service = services.get(UserService)
    profile_service: ProfileService = services.get(ProfileService)

    body = dict(request.json)
    auth_data = body['auth']
    email = auth_data['email']
    user: User = user_service.get_by_login(email)

    
    if user is not None:
        abort(400, "Этот пользователь уже существует")

    auth_data['password'] = hash_password(auth_data['password'])
    try:
        user = User(**auth_data)
        print(user)
        user_service.add(user)
        ok = True
    except NameError as e:
        print(f"Что-то пошло не так: {e}")
        abort(400, f"Неверный набор аргументов: {e}")
    except Exception as e:
        print(f"Что-то пошло не так: {auth_data}")
        abort(500, f"Что-то пошло не так: {e}")
    
    try:
        profile_service.update(email, body['profile'])
    except Exception as e:
        print(f"Что-то пошло не так: {e}")
        abort(500, f"Что-то пошло не так: {e}")
        
    return ('', 201)

@auth_required([Claim.ADMINISTRATOR, Claim.REPRESENTATIVE, Claim.PARTNER])
@app.post('/events')
def add_event():

    event_service: EventService = services.get(EventService)
    body = dict(request.json)
    
    try:
        event_service.add(Event(**body))
    except Exception as e:
        abort(400, e)

    return ('', 201)

@auth_required([Claim.ADMINISTRATOR, Claim.PARTNER, 
                Claim.ATHLETE, Claim.REPRESENTATIVE])
@app.get('/events')
def get_event():
    
    event_service: EventService = services.get(EventService)
    page = int(request.args.get('page'))
    per_page = int(request.args.get('per_page'))
    
    try:
        result: List[Row] = event_service.get(page, per_page)
        
        events = []
        for row in result:
            event = row[0]
            new_event = Event(
                name=event.name, date_started=str(event.date_started), 
                date_ended=str(event.date_ended),
                location=event.location, about=event.about
            )
            events.append(retrieve_fields(new_event))
        return json.dumps(events), 200
    except Exception as e:
        print(e)
        abort(400, e)
        
@auth_required([Claim.ADMINISTRATOR])
@app.get('/profile/<email>')
def get_profile():
    
    profile_service: ProfileService = services.get(ProfileService)
    
    try:
        result: List[Row] = profile_service.get(request.args['email'])
        return json.dumps(retrieve_fields(result)), 200
    except Exception as e:
        abort(400, e)
        
@auth_required([Claim.ADMINISTRATOR])
@app.post('/profile')
def update_profile(email):
    
    profile_service: ProfileService = services.get(ProfileService)
    body = dict(request.json)
    
    try:
        profile_service.update(email, **body['profile'])
    except Exception as e:
        abort(400, e)
        
    return ('', 201)

@auth_required([Claim.ADMINISTRATOR])
@app.get('/request')
def add_request(email):
    
    request_service: RequestService = services.get(RequestService)
    body = dict(request.json)
    
    try:
        request_service.add(email, EventRequest(**body))
    except Exception as e:
        abort(400, e)
        
    return ('', 201)


@auth_required([Claim.ADMINISTRATOR])
@app.post('/request')
def get_requests(email):
    
    request_service: RequestService = services.get(RequestService)
    
    try:
        requests = request_service.get_requests(email)
        return json.dumps(requests), '201'
    except Exception as e:
        abort(400, e)
