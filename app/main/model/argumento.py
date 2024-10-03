from app.main.extensions import db

class Argumento(db.Model):
    __tablename__ = "argumento"

    id_argumento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    argumento = db.Column(db.String(512), nullable=False)

    id_ai_data = db.Column(db.Integer, db.ForeignKey('ai_data.id_data'), nullable=False)

    def __init__(self, argumento, id_ai_data):
        self.argumento = argumento
