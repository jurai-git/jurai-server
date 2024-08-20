from app.main.extensions import db

class Requerente(db.Model):
    __name__ = 'requerente'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50), nullable=False, unique=False)
    pessoa_fisica = db.Column(db.CHAR, nullable = False, unique=False)
    cpf_cnpj = db.Column(db.String(31), nullable=False, unique=False)
    advogado_id = db.Column(db.Integer, db.ForeignKey('advogado.id'), nullable=False)

    def __init__(self, nome, cpf_cnpj, advogado_id, pessoa_fisica=True):
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.advogado_id = advogado_id
        self.pessoa_fisica = pessoa_fisica
        