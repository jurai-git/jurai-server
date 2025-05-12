from sqlite3 import IntegrityError

from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

from app.main.controller import require_auth, check_required_fields
from app.main.service.advogado_service import AdvogadoService
from app.main.service.requerente_service import RequerenteService

advogado_bp = Blueprint('advogado', __name__)
CORS(advogado_bp)

@cross_origin()
@advogado_bp.route('', methods=['POST'])
def create_advogado():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    oab = data.get('oab')
    email = data.get('email')

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
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@advogado_bp.route('/auth', methods=['POST'])
def auth_advogado():
    data = request.get_json()
    headers = request.headers

    bearer = headers.get('Authorization')
    access_token = None
    if bearer:
        access_token = bearer.split()[1]
    password = data.get('password')
    username = data.get('username')
    
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
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@advogado_bp.route('', methods=['GET'])
@require_auth
def get_advogado(advogado):
    return jsonify({
        "message": "SUCCESS",
        "advogado": {
            "id": advogado.id_advogado,
            "username": advogado.username,
            "email": advogado.email,
            "oab": advogado.oab,
            "access_token": advogado.access_token
        }
    }), 200

@cross_origin()
@advogado_bp.route("", methods=['DELETE'])
@require_auth
def delete_advogado(advogado):

    with current_app.app_context():
        advogado_service: AdvogadoService = current_app.extensions['advogado_service']
        requerente_service: RequerenteService = current_app.extensions['requerente_service']

        if not advogado:
            return jsonify({'message': 'ERROR_INVALID_CREDENTIALS'}), 404

        try:
            for requerente in advogado.requerentes:
                requerente_service.delete_requerente(advogado, requerente)

            advogado_service.delete_advogado(advogado)
            return jsonify({'message': 'SUCCESS'}), 200
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({'message': 'INTERNAL_SERVER_ERROR'}), 500

@cross_origin()
@advogado_bp.route("", methods=['PATCH'])
@require_auth
def update_advogado(advogado):
    data = request.get_json()

    with current_app.app_context():
        advogado_service: AdvogadoService = current_app.extensions['advogado_service']

        try:
            result = advogado_service.update_advogado(advogado.access_token,
                username = data.get("username"),
                password = data.get("password"),
                oab = data.get('oab'),
                email = data.get('email'),
            )
        except IntegrityError:
            return jsonify({
                "message": "ERROR_CONFLICT"
            }), 409
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR"
            }), 500
        if result is None:
            return jsonify({
                "message": "ERROR_INVALID_CREDENTIALS"
            }), 401

        return jsonify({"message": "success", "access_token": result.access_token}), 200

@cross_origin()
@advogado_bp.route("/requerente/<int:id_requerente>/demandas", methods=['GET'])
@require_auth
def get_demandas(advogado, id_requerente):

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']
            demanda_service = current_app.extensions['demanda_service']

            requerente = requerente_service.get_by_id(id_requerente)

            if not requerente:
                return jsonify({"message": "ERROR_INVALID_ID"}), 404

            if not requerente.advogado_id == advogado.id_advogado:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            return jsonify({"message": "SUCCESS", "demanda_list": demanda_service.get_demandas(requerente)}), 200
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@advogado_bp.route("/requerentes", methods=['GET'])
@require_auth
def get_requerentes(advogado):
    # gather data
    # verifications

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']

            return jsonify({"message": "SUCCESS", "requerentes_list": requerente_service.get_requerentes(advogado)}), 200
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500