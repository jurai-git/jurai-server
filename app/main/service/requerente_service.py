from flask_sqlalchemy import SQLAlchemy
from app.main.model.requerente import Requerente

class RequerenteService:

    def __init__(self, db: SQLAlchemy):
        self.db = db

    def create_requerente(self,
        cpf_cnpj, nome,
        nome_social, genero, idoso, rg,
        orgao_emissor, estado_civil, nacionalidade,
        profissao, cep, logradouro,
        email, num_imovel, complemento,
        bairro, estado, cidade,
        advogado_id):

        r = Requerente(
            cpf_cnpj, nome,
            nome_social, genero, idoso, rg,
            orgao_emissor, estado_civil, nacionalidade,
            profissao, cep, logradouro,
            email, num_imovel, complemento,
            bairro, estado, cidade, advogado_id
        )

        self.db.session.add(r)
        self.db.session.commit()

        return r

    def serialize(self, r):
        return {
                "id_requerente": r.id_requerente,
                "cpf_cnpj": r.cpf_cnpj,
                "nome": r.nome,
                "nome_social": r.nome_social if r.nome_social is not None else "",
                "genero": r.genero,
                "idoso": r.idoso,
                "rg": r.rg if r.rg is not None else "",
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
                "bairro": r.bairro,
                "cidade": r.cidade
            }

    def get_requerentes(self, advogado):
        return [ self.serialize(r) for r in advogado.requerentes ]

    def update_requerente(self, advogado, requerente, data):
        if not requerente.advogado_id == advogado.id_advogado:
            raise PermissionError("This advogado doesn't have this requerente.")

        cpf_cnpj = data.get("cpf_cnpj")
        nome = data.get("nome")
        nome_social = data.get("nome_social")
        genero = data.get("genero")
        idoso = data.get("idoso")
        rg = data.get("rg")
        orgao_emissor = data.get("orgao_emissor")
        estado_civil = data.get("estado_civil")
        nacionalidade = data.get("nacionalidade")
        profissao = data.get("profissao")
        cep = data.get("cep")
        logradouro = data.get("logradouro")
        email = data.get("email")
        num_imovel = data.get("num_imovel")
        complemento = data.get("complemento")
        estado = data.get("estado")
        cidade = data.get("cidade")
        bairro = data.get("bairro")

        if cpf_cnpj: requerente.cpf_cnpj = cpf_cnpj
        if nome: requerente.nome = nome
        if nome_social is not None: requerente.nome_social = nome_social
        if genero: requerente.genero = genero
        if idoso is not None: requerente.idoso = idoso
        if rg: requerente.rg = rg
        if orgao_emissor: requerente.orgao_emissor = orgao_emissor
        if estado_civil: requerente.estado_civil = estado_civil
        if nacionalidade: requerente.nacionalidade = nacionalidade
        if profissao: requerente.profissao = profissao
        if cep: requerente.cep = cep
        if logradouro: requerente.logradouro = logradouro
        if email: requerente.email = email
        if num_imovel: requerente.num_imovel = num_imovel
        if complemento is not None: requerente.complemento = complemento
        if estado: requerente.estado = estado
        if cidade: requerente.cidade = cidade
        if bairro: requerente.bairro = bairro

        try:
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e


    def delete_requerente(self, advogado, requerente):
        if not requerente.advogado_id == advogado.id_advogado:
            raise PermissionError("This advogado doesn't have this requerente.")

        self.db.session.delete(requerente)
        self.db.session.commit()

    def get_by_id(self, id_query):
        return self.db.session.query(Requerente).filter_by(id_requerente=id_query).first()

    def get_by_token(self, access_token):
        return self.db.session.query(Requerente).filter_by(_access_token=access_token).first()
