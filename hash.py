import bcrypt

def hash_pass(pswd):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pswd, salt)
    return hashed

