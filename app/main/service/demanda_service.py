from app.main.model.demanda import Demanda
from app.main.model.requerente import Requerente

class DemandaService:

    def __init__(self, db):
        self.db = db

    def create_demanda(self, identificacao,
        foro, competencia, classe,
        assunto_principal, pedido_liminar, 
        segredo_justica, valor_acao,
        dispensa_legal, justica_gratuira,
        guia_custas, resumo,
        requerente_cpf_cnpj
        ):
        
        d = Demanda(
            identificacao, foro, competencia, classe, assunto_principal, pedido_liminar,
            segredo_justica, valor_acao, dispensa_legal, justica_gratuira,
            guia_custas, resumo, requerente_cpf_cnpj
        )

        self.db.session.add(d)
        self.db.session.commit()

        return d
    
    def get_demandas(self, requerente: Requerente):
        return [
            {
                "id": d.id_advogado,
                "identificacao": d.identificacao,
                "foro": d.foro,
                "competencia": d.competencia,
                "classe": d.classe,
                "assunto_principal": d.assunto_principal,
                "pedido_liminar": d.pedido_liminar,
                "segredo_justica": d.segredo_justica,
                "valor_acao": d.valor_acao,
                "dispensa_legal": d.dispensa_legal,
                "justica_gratuita": d.justica_gratuira,
                "guia_custas": d.guia_custas,
                "resumo": d.resumo,
            }
            for d in requerente.demandas
        ]
    
    def delete_demanda(self, demanda: Demanda, requerente: Requerente):
        if not demanda.requerente_cpf_cnpj == requerente.cpf_cnpj:
            raise PermissionError("This requerente doesn't own this demanda")
        
        self.db.session.delete(demanda)
        self.db.session.commit()
    
    def get_by_id(self, id_query):
        return self.db.query(Demanda).filter_by(id=id_query).first()