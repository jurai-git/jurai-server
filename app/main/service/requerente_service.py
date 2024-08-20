from flask_sqlalchemy import SQLAlchemy
from app.main.model.requerente import Requerente

class RequerenteService:
    
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_requerente(self, nome, pessoa_fisica, cpf_cnpj, advogado_id):
        r = Requerente(
            nome, cpf_cnpj, advogado_id, pessoa_fisica
        )

        self.db.session.add(r)
        self.db.session.commit()

        return r

    def get_requerentes(self, advogado):
        return [
             {
            "id": r.id,
            "name": r.nome,
            "cpf_cnpj": r.cpf_cnpj,
            "pessoa_fisica": r.pessoa_fisica
            }
            for r in advogado.requerentes
        ]
    
    def delete_requerente(self, advogado, requerente):
        if not requerente.advogado_id == advogado.id:
            raise PermissionError("This advogado doesn't have this requerente.")
            return
        
        self.db.session.delete(requerente)
        self.db.session.commit()


    def get_by_id(self, requerente_id):
        return self.db.session.query(Requerente).filter_by(id=requerente_id).first()

    def get_by_cpf_cnpj(self, cpf_cnpj):
        return self.db.session.query(Requerente).filter_by(cpf_cnpj=cpf_cnpj).first()
        
