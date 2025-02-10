from app.main.extensions import db

class AiData(db.Model):
    __tablename__ = "ai_data"

    id_data = db.Column(db.Integer, primary_key=True, autoincrement=True)
    positive_odd = db.Column(db.Double, nullable = True)
    partial_odd = db.Column(db.Double, nullable = True)
    negative_odd = db.Column(db.Double, nullable = True)

    # FKs
    id_demanda = db.Column(db.Integer, db.ForeignKey('demanda.id_demanda'))
    demanda = db.relationship('Demanda', back_populates='ai_data')

    def __init__(self, positive_odd=0, partial_odd=0, negative_odd=0):
        self.positive_odd = positive_odd
        self.partial_odd = partial_odd
        self.negative_odd = negative_odd
