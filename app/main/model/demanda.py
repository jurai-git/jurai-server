
from app.main.extensions import db

class Demanda(db.Model):
    __tablename__ = "demanda"

    # PKs
    id_demanda = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Fields
    identificacao = db.Column(db.String(128), nullable=False)
    foro = db.Column(db.String(50), nullable = False)
    status = db.Column(db.String(64), nullable = True)
    competencia = db.Column(db.String(50), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    assunto_principal = db.Column(db.String(512), nullable=False)
    pedido_liminar = db.Column(db.Boolean, nullable=False)
    segredo_justica = db.Column(db.Boolean, nullable=False)
    valor_acao = db.Column(db.Double, nullable=False)
    dispensa_legal = db.Column(db.Boolean, nullable=False)
    justica_gratuita = db.Column(db.Boolean, nullable=False)
    guia_custas = db.Column(db.Boolean, nullable=False) # TODO: trocar para arquivo
    resumo = db.Column(db.String(4096), nullable=False)

    # FKs
    ai_data = db.relationship('AiData', back_populates='demanda', uselist=False)
    id_requerente = db.Column(db.Integer, db.ForeignKey('requerente.id_requerente'), nullable=False)

    def __init__(self, identificacao,
        foro, competencia, classe,
        assunto_principal, pedido_liminar, 
        segredo_justica, valor_acao,
        dispensa_legal, justica_gratuita,
        guia_custas, resumo, status, id_requerente):

        self.identificacao = identificacao
        self.foro = foro
        self.competencia = competencia
        self.classe = classe
        self.assunto_principal = assunto_principal
        self.pedido_liminar = pedido_liminar
        self.segredo_justica = segredo_justica
        self.valor_acao = valor_acao
        self.dispensa_legal = dispensa_legal
        self.justica_gratuita = justica_gratuita
        self.guia_custas = guia_custas
        self.resumo = resumo
        self.status = status
        self.id_requerente = id_requerente


    def __eq__(self, other):
        if isinstance(other, Demanda):
            return self.id_demanda == other.id_demanda
        return False

    def __hash__(self):
        return hash(self.id_demanda)

