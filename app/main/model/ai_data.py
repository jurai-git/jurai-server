from app.main.extensions import db

class AiData(db.Model):
    __tablename__ = "ai_data"

    id_data = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # FKs
    id_demanda = db.Column(db.Integer, db.ForeignKey('demanda.id_demanda'))
    demanda = db.relationship('Demanda', back_populates='ai_data')

    argumentos = db.relationship('Argumento', backref='ai_data' ,lazy=True)
