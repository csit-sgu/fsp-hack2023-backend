import bcrypt

def hash_pass(pswd, salt):
#    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pswd, salt)
    return hashed
