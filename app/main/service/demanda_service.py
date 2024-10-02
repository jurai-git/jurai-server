from app.main.model.demanda import Demanda
from app.main.model.requerente import Requerente

class DemandaService:

    def __init__(self, db):
        self.db = db

    def create_demanda(self, identificacao,
        foro, competencia, classe,
        assunto_principal, pedido_liminar, 
        segredo_justica, valor_acao,
        dispensa_legal, justica_gratuita,
        guia_custas, resumo, id_requerente
        ):
        
        d = Demanda(
            identificacao, foro, competencia, classe, assunto_principal, pedido_liminar,
            segredo_justica, valor_acao, dispensa_legal, justica_gratuita,
            guia_custas, resumo, id_requerente
        )

        try:
            self.db.session.add(d)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

        return d

    def serialize(self, d: Demanda):
        return {
                "id": d.id_demanda,
                "identificacao": d.identificacao,
                "foro": d.foro,
                "competencia": d.competencia,
                "classe": d.classe,
                "assunto_principal": d.assunto_principal,
                "pedido_liminar": d.pedido_liminar,
                "segredo_justica": d.segredo_justica,
                "valor_acao": d.valor_acao,
                "dispensa_legal": d.dispensa_legal,
                "justica_gratuita": d.justica_gratuita,
                "guia_custas": d.guia_custas,
                "resumo": d.resumo,
                # "status": d.status
            }

    def update_demanda(self, requerente, demanda, data):
        if demanda not in requerente.demandas:
            raise PermissionError("This requerente doesn't own this demanda")

        identificacao = data.get("identificacao")
        foro = data.get("foro")
        competencia = data.get("competencia")
        classe = data.get("classe")
        assunto_principal = data.get("assunto_principal")
        pedido_liminar = data.get("pedido_liminar")
        segredo_justica = data.get("segredo_justica")
        valor_acao = data.get("valor_acao")
        dispensa_legal = data.get("dispensa_legal")
        justica_gratuita = data.get("jutica_gratuita")
        guia_custas = data.get("guia_custas")
        resumo = data.get("resumo")
        status = data.get("status")

        if identificacao: demanda.identificacao = identificacao
        if foro: demanda.foro = foro
        if competencia: demanda.competencia = competencia
        if classe: demanda.classe = classe
        if assunto_principal: demanda.assunto_principal = assunto_principal
        if pedido_liminar is not None: demanda.pedido_liminar = pedido_liminar
        if segredo_justica is not None: demanda.segredo_justica = segredo_justica
        if valor_acao: demanda.valor_acao = valor_acao
        if dispensa_legal is not None: demanda.dispensa_legal = dispensa_legal
        if justica_gratuita is not None: demanda.justica_gratuita = justica_gratuita
        if guia_custas is not None: demanda.guia_custas = guia_custas
        if resumo: demanda.resumo = resumo
        if status: demanda.status = status

        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_demandas(self, requerente: Requerente):
        return [self.serialize(d) for d in requerente.demandas]
    
    def delete_demanda(self, demanda: Demanda, requerente: Requerente):
        if not demanda.id_requerente == requerente.id_requerente:
            raise PermissionError("This requerente doesn't own this demanda")
        
        try:
            self.db.session.delete(demanda)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e

    def get_by_id(self, id_query):
        return self.db.session.query(Demanda).filter_by(id_demanda=id_query).first()
