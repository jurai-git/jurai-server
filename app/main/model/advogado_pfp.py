
from app.main.extensions import db
from sqlalchemy.dialects.mysql import MEDIUMBLOB

class AdvogadoPFP(db.Model):
    __tablename__ = 'advogado_pfp'

    id_advogado = db.Column(db.Integer, db.ForeignKey('advogado.id_advogado'), primary_key=True)
    mime_type = db.Column(db.String(50), nullable=False)
    data = db.Column(MEDIUMBLOB, nullable=False)

    advogado = db.relationship('Advogado', back_populates='advogado_pfp', lazy=True)