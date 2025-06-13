import secrets
import bcrypt

def gensalt():
    return bcrypt.gensalt()


def generate_token():
    return secrets.token_hex(16)


def hash_password(password, salt):
    return bcrypt.hashpw(password.encode('utf-8'), salt)
