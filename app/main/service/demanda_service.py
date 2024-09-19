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
        guia_custas, resumo, status, id_requerente
        ):
        
        d = Demanda(
            identificacao, foro, competencia, classe, assunto_principal, pedido_liminar,
            segredo_justica, valor_acao, dispensa_legal, justica_gratuita,
            guia_custas, resumo, status, id_requerente
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
                "status": d.status
            }
    
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
        return self.db.query(Demanda).filter_by(id=id_query).first()
