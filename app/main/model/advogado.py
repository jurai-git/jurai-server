from typing import Any

from app.main.extensions import db
from app.main.model import crypt_utils

class Advogado(db.Model):
    __tablename__ = 'advogado'

    id_advogado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    oab = db.Column(db.String(20), nullable=False, unique=False)
    _password_hash = db.Column(db.String(60), nullable=False)
    _salt = db.Column(db.LargeBinary(29), nullable=False)
    _access_token = db.Column(db.String(32), nullable=False, unique=True)
    requerentes = db.relationship('Requerente', backref='advogado' ,lazy=True)

    def __init__(self, username, email, oab, pwd, **kw: Any):
        super().__init__(**kw)
        self.username = username
        self.email = email
        self.oab = oab

        self._salt = crypt_utils.gensalt()
        self._password_hash = crypt_utils.hash_password(pwd, self._salt).decode('utf-8')
        self._access_token = crypt_utils.generate_token()

    def get_token(self, password):
        hashed_pwd = crypt_utils.hash_password(password, self._salt).decode('utf-8')
        print(hashed_pwd)
        print(self._password_hash)
        return self._access_token if hashed_pwd == self._password_hash else None

    def auth(self, token):
        return token == self._access_token

    def __str__(self):
        return self.username

    def update_password(self, new_password):
        self._salt = self.gensalt()
        self._password_hash = self.hash_password(new_password, self._salt).decode('utf-8')

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def salt(self):
        return self._salt.decode('utf-8')

    @property
    def access_token(self):
        return self._access_token
