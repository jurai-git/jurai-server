from MySQLdb import Error
from flask import current_app
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound

from app.main.model.advogado import Advogado


class AdvogadoService:

    def __init__(self, db: SQLAlchemy):
        self.db: SQLAlchemy = db

    def create_advogado(self, username, pwd, oab, email):
        user = Advogado(username=username, email=email, pwd=pwd, oab=oab)

        try:
            self.db.session.add(user)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

        return user


    def get_token(self, username, password):
        try:
            advogado = Advogado.query.filter_by(username=username).one()
            token = advogado.get_token(password)
            if token:
                print(token)
                return token
            return None

        except NoResultFound:
            print("NoResultFound")
            return None

    def update_advogado(self, advogado_id, **kwargs):
        advogado = self.find_by_id(advogado_id)
        if not advogado:
            return None

        if 'username' in kwargs:
            advogado.username = kwargs['username']
        if 'email' in kwargs:
            advogado.email = kwargs['email']
        if 'oab' in kwargs:
            advogado.oab = kwargs['oab']
        if 'password' in kwargs:
            advogado.update_password(kwargs['password'])

        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

        return advogado

    def get_all(self):
        return self.db.session.query(Advogado).all()

    def find_by_id(self, id):
        return self.db.session.query(Advogado).filter_by(id_advogado=id).first()

    def find_by_uname(self, username):
        return self.db.session.query(Advogado).filter_by(username=username).first()

    def find_by_token(self, token):
        return self.db.session.query(Advogado).filter_by(_access_token=token).first()

    def find_by_email(self, email):
        return self.db.session.query(Advogado).filter_by(email=email).first()

    def delete_advogado(self, advogado):
        try:
            self.db.session.delete(advogado)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e
