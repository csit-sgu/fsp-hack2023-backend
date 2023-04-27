import bcrypt

def is_none_or_empty(s: str):
    return s is None or s == ''

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password