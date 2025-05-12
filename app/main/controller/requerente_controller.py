from flask import Blueprint, json, request, jsonify, current_app
from flask_cors import CORS, cross_origin
from sqlalchemy.exc import IntegrityError

from app.main.controller import require_auth
from app.main.service.advogado_service import AdvogadoService

requerente_bp = Blueprint('requerente', __name__)
CORS(requerente_bp)

@cross_origin()
@requerente_bp.route("/<int:id>", methods=['PATCH'])
@require_auth
def update_requerente(advogado, id):
    data = request.get_json()

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']

            # get requerente
            requerente = requerente_service.get_by_id(id)
            if requerente is None:
                return jsonify({"message": "ERROR_REQUERENTE_DOESNT_EXIST"}), 404

            try:
                requerente_service.update_requerente(advogado, requerente, data)
            except PermissionError:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403
            return jsonify({"message": "SUCCESS", "requerente": requerente_service.serialize(requerente)}), 200
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500



@cross_origin()
@requerente_bp.route("", methods=['POST'])
@require_auth
def create_requerente(advogado):
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

    # verifications
    if not cpf_cnpj or not nome or not genero or not rg or not orgao_emissor or not estado_civil or not nacionalidade or not profissao or not cep or not logradouro or not num_imovel or not email or not bairro or not estado or not cidade:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    if not idoso:
        idoso = False

    # store in db
    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']

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
                return jsonify({"message": "ERROR_CONFLICT"}), 409 # teremos que mudar a PK no futuro
            return jsonify({"message": "SUCCESS"}), 201
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500


@cross_origin()
@requerente_bp.route("/<int:requerente_id>", methods=['DELETE'])
@require_auth
def delete_requerente(advogado, requerente_id):

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']

            requerente = requerente_service.get_by_id(requerente_id)
            try:
                requerente_service.delete_requerente(advogado, requerente)
                return jsonify({"message": "SUCCESS"}), 200
            except PermissionError:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@requerente_bp.route('/<int:requerente_id>', methods=['GET'])
@require_auth
def get_requerente(advogado, requerente_id):

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']
            requerente = requerente_service.get_by_id(requerente_id)

            if requerente.advogado_id != advogado.id_advogado:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            return jsonify({
                "message": "success",
                "requerente": requerente.serialize()
            })

        except Exception as e:
            current_app.logger.error(f"Error getting requerente: {str(e)}", exc_info=True)
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            }), 500