from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin
from sqlalchemy.exc import IntegrityError

requerente_bp = Blueprint('requerente', __name__)
CORS(requerente_bp)


@cross_origin()
@requerente_bp.route("/new", methods=['POST'])
def create_requerente():
    # gather data
    data = request.json

    pessoa_fisica = data.get("pessoa_fisica")
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
    
    
    """
            pessoa_fisica, cpf_cnpj, nome,
            nome_social, genero, idoso, rg,
            orgao_emissor, estado_civil, nacionalidade,
            profissao, cep, logradouro,
            email, num_imovel, complemento,
            bairro, estado, cidade, advogado_id
    """
    advogado_token = data.get('access_token')

    # verifications
    if not cpf_cnpj or not nome or not genero or not rg or not orgao_emissor or not estado_civil or not nacionalidade or not profissao or not cep or not logradouro or not num_imovel or not email or not bairro or not estado or not cidade:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    if not idoso:
        idoso = True
    
    # store in db
    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        requerente_service = current_app.extensions['requerente_service']
        
        advogado = advogado_service.find_by_token(advogado_token)
        if advogado is None:
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
        
        id = advogado.id_advogado
        try:
            requerente_service.create_requerente(
                pessoa_fisica=pessoa_fisica, cpf_cnpj=cpf_cnpj, nome=nome, nome_social=nome_social, 
                genero=genero, idoso=idoso, rg=rg, orgao_emissor=orgao_emissor, estado_civil=estado_civil,
                nacionalidade=nacionalidade, profissao=profissao, cep=cep, logradouro=logradouro,
                email=email, num_imovel=num_imovel, complemento=complemento, bairro=bairro,
                estado=estado, cidade=cidade, advogado_id=id
            )
        except IntegrityError as e:
            print(e._message)
            return jsonify({"message": "REQUERENTE_ALREADY_EXISTS"}), 409 # teremos que mudar a PK no futuro
        return jsonify({"message": "SUCCESS"}), 201


@cross_origin()
@requerente_bp.route("/remove", methods=['DELETE'])
def delete_requerente():
    # gather data
    data = request.json
    advogado_token = data.get('access_token')
    requerente_id = data.get('requerente_id')

    if not advogado_token or not requerente_id:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    
    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        requerente_service = current_app.extensions['requerente_service']
        advogado = advogado_service.find_by_token(advogado_token)
        if not advogado:
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

        requerente = requerente_service.get_by_id(requerente_id)
        try:
            requerente_service.delete_requerente(advogado, requerente)
            return jsonify({"message": "SUCCESS"}), 200
        except:
            return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403


@cross_origin()
@requerente_bp.route("/demandas", methods=['POST'])
def get_demandas():
    data = request.json
    requerente_token = data.get('access_token')

    if not requerente_token:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    
    with current_app.app_context():
        requerente_service = current_app.extensions['requerente_service']
        demanda_service = current_app.extensions['demanda_service']

        requerente = requerente_service.get_by_token(requerente_token)
        if not requerente:
            return jsonify({"ERROR_INVALID_CREDENTIALS"}), 401
        
        return jsonify({"message": "SUCCESS", "demanda_list": demanda_service.get_demandas(requerente)})

