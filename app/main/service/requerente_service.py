from flask_sqlalchemy import SQLAlchemy
from app.main.model.requerente import Requerente

class RequerenteService:
    
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_requerente(self, 
        pessoa_fisica, cpf_cnpj, nome,
        nome_social, genero, idoso, rg,
        orgao_emissor, estado_civil, nacionalidade,
        profissao, cep, logradouro,
        email, num_imovel, complemento, 
        bairro, estado, cidade,
        advogado_id):

        r = Requerente(
            pessoa_fisica, cpf_cnpj, nome,
            nome_social, genero, idoso, rg,
            orgao_emissor, estado_civil, nacionalidade,
            profissao, cep, logradouro,
            email, num_imovel, complemento,
            bairro, estado, cidade, advogado_id
        )

        self.db.session.add(r)
        self.db.session.commit()

        return r

    def get_requerentes(self, advogado):
        return [
            {
                "pessoa_fisica": r.pessoa_fisica,
                "cpf_cnpj": r.cpf_cnpj,
                "nome": r.nome,
                "nome_social": r.nome_social,
                "genero": r.genero,
                "idoso": r.idoso,
                "rg": r.rg,
                "orgao_emissor": r.orgao_emissor,
                "estado_civil": r.estado_civil,
                "nacionalidade": r.nacionalidade,
                "profissao": r.profissao,
                "cep": r.cep,
                "logradouro": r.logradouro,
                "email": r.email,
                "num_imovel": r.num_imovel,
                "complemento": r.complemento if r.complemento is not None else "",
                "estado": r.estado,
                "cidade": r.cidade
            }
            for r in advogado.requerentes
        ]
    
    def delete_requerente(self, advogado, requerente):
        if not requerente.advogado_id == advogado.id_advogado:
            raise PermissionError("This advogado doesn't have this requerente.")
        
        self.db.session.delete(requerente)
        self.db.session.commit()

    def get_by_id(self, id_query):
        return self.db.session.query(Requerente).filter_by(id=id_query).first()
        
    def get_by_token(self, access_token):
        return self.db.session.query(Requerente).filter_by(_access_token=access_token).first()
