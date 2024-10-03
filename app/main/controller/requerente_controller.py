from flask import Blueprint, json, request, jsonify, current_app
from flask_cors import CORS, cross_origin
from sqlalchemy.exc import IntegrityError

from app.main.service.advogado_service import AdvogadoService

requerente_bp = Blueprint('requerente', __name__)
CORS(requerente_bp)

@cross_origin
@requerente_bp.route("/update", methods=['PUT'])
def update_requerente():
    data = request.get_json()

    id_requerente = data.get("id_requerente")

    access_token = data.get("access_token")

    # verifications
    if not id_requerente:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            requerente_service = current_app.extensions['requerente_service']

            # get advogado
            advogado = advogado_service.find_by_token(access_token)
            if advogado is None:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

            # get requerente
            requerente = requerente_service.get_by_id(id_requerente)
            if requerente is None:
                return jsonify({"message": "ERROR_REQUERENTE_DOESNT_EXIST"}), 404

            try:
                requerente_service.update_requerente(advogado, requerente, data)
            except PermissionError:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403
            return jsonify({"message": "SUCCESS", "requerente": requerente_service.serialize(requerente)}), 200
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500



@cross_origin()
@requerente_bp.route("/new", methods=['POST'])
def create_requerente():
    # gather data
    data = request.get_json()

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

    advogado_token = data.get('access_token')

    # verifications
    if not cpf_cnpj or not nome or not genero or not rg or not orgao_emissor or not estado_civil or not nacionalidade or not profissao or not cep or not logradouro or not num_imovel or not email or not bairro or not estado or not cidade:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    if not idoso:
        idoso = False

    # store in db
    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            requerente_service = current_app.extensions['requerente_service']

            advogado = advogado_service.find_by_token(advogado_token)
            if advogado is None:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

            id = advogado.id_advogado
            try:
                requerente_service.create_requerente(
                    cpf_cnpj=cpf_cnpj, nome=nome, nome_social=nome_social,
                    genero=genero, idoso=idoso, rg=rg, orgao_emissor=orgao_emissor, estado_civil=estado_civil,
                    nacionalidade=nacionalidade, profissao=profissao, cep=cep, logradouro=logradouro,
                    email=email, num_imovel=num_imovel, complemento=complemento, bairro=bairro,
                    estado=estado, cidade=cidade, advogado_id=id
                )
            except IntegrityError as e:
                print(e._message)
                return jsonify({"message": "REQUERENTE_ALREADY_EXISTS"}), 409 # teremos que mudar a PK no futuro
            return jsonify({"message": "SUCCESS"}), 201
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500


@cross_origin()
@requerente_bp.route("/remove", methods=['DELETE'])
def delete_requerente():
    # gather data
    data = request.get_json()
    advogado_token = data.get('access_token')
    requerente_id = data.get('requerente_id')

    if not advogado_token or not requerente_id:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
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
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500


@cross_origin()
@requerente_bp.route("/demandas", methods=['POST'])
def get_demandas():
    data = request.get_json()
    advogado_token = data.get('access_token')
    id_requerente = data.get("id_requerente")

    if not id_requerente:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
            advogado_service: AdvogadoService = current_app.extensions['advogado_service']
            requerente_service = current_app.extensions['requerente_service']
            demanda_service = current_app.extensions['demanda_service']

            advogado = advogado_service.find_by_token(advogado_token)

            if not advogado:
                return jsonify({"ERROR_INVALID_CREDENTIALS"}), 401

            requerente = requerente_service.get_by_id(id_requerente)

            if not requerente:
                return jsonify({"message": "ERROR_REQUERENTE_DOESNT_EXIST"}), 404

            if not requerente.advogado_id == advogado.id_advogado:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            return jsonify({"message": "SUCCESS", "demanda_list": demanda_service.get_demandas(requerente)}), 200
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500


