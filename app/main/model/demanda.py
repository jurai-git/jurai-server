
from app.main.extensions import db

class Demanda(db.Model):
    __tablename__ = "demanda"

    # PKs
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Fields
    foro = db.Column(db.String(50), nullable = False)
    competencia = db.Column(db.String(50), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    assunto_principal = db.Column(db.String(512), nullable=False)
    pedido_liminar = db.Column(db.Boolean, nullable=False)
    segredo_justica = db.Column(db.Boolean, nullable=False)
    valor_acao = db.Column(db.Double, nullable=False)
    dispensa_legal = db.Column(db.Boolean, nullable=False)
    justica_gratuira = db.Column(db.Boolean, nullable=False)
    guia_custas = db.Column(db.Boolean, nullable=False)
    resumo = db.Column(db.String(4096), nullable=False)

    # FKs
    requerente_cpf_cnpj = db.Column(db.String(50), db.ForeignKey('requerente.cpf_cnpj'), nullable=False)

    def __init__(self,
        foro, competencia, classe,
        assunto_principal, pedido_liminar, 
        segredo_justica, valor_acao,
        dispensa_legal, justica_gratuira,
        guia_custas, resumo,
        requerente_cpf_cnpj):

        self.foro = foro
        self.competencia = competencia
        self.classe = classe
        self.assunto_principal = assunto_principal
        self.pedido_liminar = pedido_liminar
        self.segredo_justica = segredo_justica
        self.valor_acao = valor_acao
        self.dispensa_legal = dispensa_legal
        self.justica_gratuira = justica_gratuira
        self.guia_custas = guia_custas
        self.resumo = resumo
        self.requerente_cpf_cnpj = requerente_cpf_cnpj