from io import BytesIO

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from app.main.model.advogado import Advogado
from app.main.model.advogado_pfp import AdvogadoPFP

from PIL import Image


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
            return None

    def _prepare_pfp(self, file: FileStorage):
        img = Image.open(file).convert("RGB")

        w, h = img.size

        min_size = min(w, h)
        left = (w - min_size) // 2
        top = (h - min_size) // 2
        neww = left + min_size
        newh = top + min_size

        img = img.crop((left, top, neww, newh))
        img = img.resize((512, 512), Image.LANCZOS)

        output = BytesIO()
        img.save(output, format="JPEG")
        output.seek(0)
        return output

    def add_pfp(self, advogado: Advogado, file: FileStorage):
        if "image" not in file.mimetype:
            raise ValueError("The file is in the wrong format")

        processed_img = self._prepare_pfp(file)
        pic = AdvogadoPFP(
            id_advogado = advogado.id_advogado,
            mime_type = "image/jpg",
            data = processed_img.read(),
        )

        try:
            self.db.session.merge(pic)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_pfp_by_id(self, id_advogado):
        record = self.db.session.query(AdvogadoPFP).filter_by(id_advogado=id_advogado).first()
        if not record:
            raise NoResultFound("No advogado was found with this ID")
        return BytesIO(record.data)

    def remove_pfp(self, advogado: Advogado):
        try:
            self.db.session.query(AdvogadoPFP).filter_by(id_advogado=advogado.id_advogado).delete()
            self.db.session.commit()
        except NoResultFound:
            raise NoResultFound("No advogado was found with this ID")
        except Exception as e:
            self.db.session.rollback()
            raise e

    def update_advogado(self, advogado_token, username=None, email=None, oab=None, password=None):
        advogado = self.find_by_token(advogado_token)
        if not advogado:
            return None

        if username is not None:
            advogado.username = username
        if email is not None:
            advogado.email = email
        if oab is not None:
            advogado.oab = oab
        if password is not None:
            advogado.update_password(password)

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
