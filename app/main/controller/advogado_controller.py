from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

from app.main.service.advogado_service import AdvogadoService

advogado_bp = Blueprint('advogado', __name__)
CORS(advogado_bp)

@cross_origin()
@advogado_bp.route('/new', methods=['POST'])
def create_advogado():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    oab = data.get('oab')
    email = data.get('email')

    print(username)
    print(password)
    print(oab)
    print(email)

    if not username or not password or not oab or not email:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            if advogado_service.find_by_uname(username) or advogado_service.find_by_email(email):
                return jsonify({"message": "ERROR_CONFLICT"}), 409

            user = advogado_service.create_advogado(username, password, oab, email)
            return jsonify({"message": "SUCCESS", "access_token": user.access_token}), 201
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

@cross_origin()
@advogado_bp.route('/get', methods=['POST'])
def get_advogado():
    data = request.get_json()
    access_token = data.get('access_token')
    password = data.get('password')
    username = data.get('username')
    print(access_token)
    print(password)
    print(username)
    
    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']

            if not access_token:
                if not password or not username:
                    return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
                access_token = advogado_service.get_token(username, password)

            advogado = advogado_service.find_by_token(access_token)
            if advogado:
                return jsonify({
                    "message": "SUCCESS",
                    "advogado": {
                        "id": advogado.id_advogado,
                        "username": advogado.username,
                        "email": advogado.email,
                        "oab": advogado.oab,
                        "access_token": access_token
                    }
                }), 200
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

@cross_origin()
@advogado_bp.route("/token", methods=['POST'])
def auth():
    data = request.get_json()
    uname = data.get('username')
    password = data.get('password')

    if not uname or not password:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            access_token = advogado_service.get_token(uname, password)
            if access_token:
                return jsonify({"message": "SUCCESS", "access_token": access_token}), 201
            else:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

@cross_origin()
@advogado_bp.route("/requerentes", methods=['POST'])
def get_requerentes():
    # gather data
    data = request.json
    advogado_token = data.get('access_token')

    # verifications
    if not advogado_token:
        return jsonify({"message": "ERROR_REQURED_FIELDS_EMPTY"}), 400
    
    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            requerente_service = current_app.extensions['requerente_service']

            advogado = advogado_service.find_by_token(advogado_token)
            if not advogado:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

            return jsonify({"message": "SUCCESS", "requerentes_list": requerente_service.get_requerentes(advogado)}), 201
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

@cross_origin()
@advogado_bp.route("/demandas", methods=['POST'])
def get_demandas_from_requerente():
    data = request.json
    advogado_token = data.get('access_token')
    requerente_id = data.get('requerente_id')

    if not advogado_token or not requerente_id:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400
    
    with current_app.app_context():
        try:
            advogado_service = current_app.extensions['advogado_service']
            requerente_service = current_app.extensions['requerente_service']
            demanda_service = current_app.extensions['demanda_service']

            # auth advogado
            advogado = advogado_service.find_by_token(advogado_token)
            if not advogado:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

            # see if advogado has requerente
            requerente = requerente_service.get_by_id(requerente_id)
            if not requerente:
                return jsonify({"message": "ERROR_INVALID_REQUERENTE"}), 404

            if requerente not in advogado.requerentes:
                return jsonify({"message": "ERROR_DOESNT_OWN_REQUERENTE"}), 403

            return jsonify({"message": "SUCCESS", "demanda_list": demanda_service.get_demandas(requerente)})
        except Exception as e:
            print(e)
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500


@cross_origin()
@advogado_bp.route("/delete", methods=['DELETE'])
def delete_advogado():
    data = request.get_json()

    advogado_id = data.get('advogado_id')

    if not advogado_id:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        advogado_service: AdvogadoService = current_app.extensions['advogado_service']

        advogado = advogado_service.find_by_id(advogado_id)

        if not advogado:
            return jsonify({'message': 'ERROR_INVALID_ID'}), 404

        try:
            advogado_service.delete_advogado(advogado)
            return jsonify({'message': 'SUCCESS'}), 200
        except Exception as e:
            print(f'Error deleting demanda: {e}')
            return jsonify({'message': 'ERROR_DELETING_DEMANDA', 'error': str(e)}), 500
