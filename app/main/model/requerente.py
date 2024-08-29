from app.main.extensions import db
import app.main.model.crypt_utils

class Requerente(db.Model):
    __name__ = 'requerente'

    # PKs and related stuff
    pessoa_fisica = db.Column(db.CHAR, nullable = False, unique=False)
    cpf_cnpj = db.Column(db.String(50), nullable=False, unique=True, primary_key=True)


    # main fields
    nome = db.Column(db.String(50), nullable=False, unique=False)
    nome_social = db.Column(db.String(50), nullable=True, unique=False)
    genero = db.Column(db.CHAR, nullable=False)
    idoso = db.Column(db.Boolean, nullable=False)
    rg = db.Column(db.String(50), nullable=True)
    orgao_emissor = db.Column(db.String(2), nullable=False)
    estado_civil = db.Column(db.String(50), nullable=False)
    nacionalidade = db.Column(db.String(50), nullable=False)
    profissao = db.Column(db.String(50), nullable=False)
    cep = db.Column(db.String(50), nullable=False)
    logradouro = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    # address fields (one-to-one so in the same table)
    num_imovel = db.Column(db.String(50), nullable=False)
    complemento = db.Column(db.String(50), nullable=True)
    bairro = db.Column(db.String(50), nullable = False)
    estado = db.Column(db.String(50), nullable = False)
    cidade = db.Column(db.String(50), nullable = False)

    # authentication
    _password_hash = db.Column(db.String(60), nullable=False)
    _salt = db.Column(db.LargeBinary(29), nullable=False)
    _access_token = db.Column(db.String(32), nullable=False, unique=True)
    
    # FKs
    advogado_id = db.Column(db.Integer, db.ForeignKey('advogado.id'), nullable=False)
    demandas = db.relationship('Demanda', backref='Requerente', lazy=True)


    def __init__(self, 
        pessoa_fisica, cpf_cnpj, nome,
        nome_social, genero, idoso, rg,
        orgao_emissor, estado_civil, nacionalidade,
        profissao, cep, logradouro,
        email, num_imovel, complemento, 
        bairro, estado, cidade,
        advogado_id):
        
        self.pessoa_fisica = pessoa_fisica
        self.cpf_cnpj = cpf_cnpj
        self.nome = nome
        self.nome_social = nome_social
        self.genero = genero
        self.idoso = idoso
        self.rg = rg
        self.orgao_emissor = orgao_emissor
        self.estado_civil = estado_civil
        self.nacionalidade = nacionalidade
        self.profissao = profissao
        self.cep = cep
        self.logradouro = logradouro
        self.email = email
        self.num_imovel = num_imovel
        self.complemento = complemento
        self.bairro = bairro
        self.estado = estado
        self.cidade = cidade
        self.advogado_id = advogado_id

        self._password_hash = None
        self._salt = None
        self._access_token = None

    def create_password(self, password):
        self._salt = crypt_utils.gensalt()
        self._access_token = crypt_utils.generate_token()
        self._password_hash = crypt_utils.hash_password(password, self._salt)

    def get_token(self, password):
        hashed_pwd = crypt_utils.hash_password(password, self._salt).decode('utf-8')
        print(hashed_pwd)
        print(self._password_hash)
        return self._access_token if hashed_pwd == self._password_hash else None

    def auth(self, token):
        return token == self._access_token
    
    def update_password(self, new_password):
        self._salt = crypt_utils.gensalt()
        self._password_hash = crypt_utils.hash_password(new_password, self._salt).decode('utf-8')

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def salt(self):
        return self._salt.decode('utf-8')

    @property
    def access_token(self):
        return self._access_token
