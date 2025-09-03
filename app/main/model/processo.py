from app.main.extensions import db

class Processo(db.Model):
    __tablename__ = 'processo'

    numero_tjmg = db.Column(db.String(32), primary_key=True, nullable=False)
    acordao = db.Column(db.Text, nullable=False)
    ementa = db.Column(db.String(8192), nullable=False)
    sumula = db.Column(db.String(256), nullable=False)

    def serialize(self):
        return {
            'numero_tjmg': self.numero_tjmg,
            'acordao': self.acordao,
            'ementa': self.ementa,
            'sumula': self.sumula
        }