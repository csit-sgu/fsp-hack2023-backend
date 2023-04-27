import bcrypt

from flask import abort

def is_none_or_empty(s: str):
    return s is None or s == ''

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def make_default_asserts(body):
    if body is None: 
        abort(400, "Неверный формат запроса")
        
    if any([is_none_or_empty(v) for v in body.values()]):
        abort(400, "Некоторые из полей запроса пусты")