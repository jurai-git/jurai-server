from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

requerente_bp = Blueprint('requerente', __name__)
CORS(requerente_bp)


@cross_origin()
@requerente_bp.route("/", methods=['POST'])
def create_requerente():
    # gather data
    data = request.json
    name = data.get('name')
    cpf_cnpj = data.get('cpf_cnpj')
    pessoa_fisica = data.get('pessoa_fisica')
    advogado_token = data.get('access_token')

    # verifications
    if not name or not cpf_cnpj or not pessoa_fisica or not advogado_token:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    
    # store in db
    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        requerente_service = current_app.extensions['requerente_service']
        
        advogado = advogado_service.find_by_token(advogado_token)
        if advogado is None:
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
        
        id = advogado.id
        requerente_service.create_requerente(nome=name, pessoa_fisica=pessoa_fisica, cpf_cnpj=cpf_cnpj, advogado_id=id)
        return jsonify({"message": "SUCCESS"}), 201


@cross_origin()
@requerente_bp.route("/", methods=['DELETE'])
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
            return jsonify({"message": "ERROR_ACCESS_DENIED"}), 401
