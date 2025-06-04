import secrets
import traceback
from sqlite3 import IntegrityError
from types import TracebackType

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_cors import CORS, cross_origin
from redis import Redis
from sqlalchemy.exc import NoResultFound

from app.main.service.email_service import EmailService
from app.main.controller import require_auth
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
@advogado_bp.route('/pfp', methods=['DELETE'])
@require_auth
def delete_picture(advogado):
    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']

        try:
            advogado_service.remove_pfp(advogado)
        except NoResultFound:
            return jsonify({
                'message': 'ERROR_INVALID_ID'
            }), 400
        except Exception as e:
            current_app.logger.warning(f"Returning 500 on delete_picture due to {e}")
            return jsonify({
                'message': 'INTERNAL_SERVER_ERROR'
            }), 500

    return jsonify({
        'message': 'SUCCESS'
    }), 200

@cross_origin()
@advogado_bp.route('/pfp', methods=['POST', 'PATCH'])
@require_auth
def add_picture(advogado):
    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        file = request.files.get('picture')

        if not file:
            return jsonify({
                'status': 'error',
                'message': 'REQUIRED_FIELDS_EMPTY'
            }), 400

        try:
            advogado_service.add_pfp(advogado, file)
        except Exception as e:
            current_app.logger.warning(f"Returning 500 on add_picture due to {e}")
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR"
            }), 500

    return jsonify({
        'message': 'SUCCESS'
    }), 200

@cross_origin()
@advogado_bp.route("/<int:id_advogado>/pfp", methods=['GET'])
def get_advogado_picture(id_advogado: int):

    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        try:
            return send_file(advogado_service.get_pfp_by_id(id_advogado), mimetype="image/jpeg")
        except NoResultFound:
            return jsonify({
                'message': 'ERROR_INVALID_ID'
            }), 404
        except Exception as e:
            current_app.logger.warning(f"Returning 500 on get_advogado_picture due to {e}")
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR"
            }), 500


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

# pasword reset (via email)
# TODO: only allow one reset email per minute, for a max of 10 resets in one hor
@cross_origin()
@advogado_bp.route('/request-reset/<email>', methods=['POST'])
def request_reset(email: str):
    token = secrets.token_urlsafe(32)

    with current_app.app_context():
        redis: Redis = current_app.extensions['redis']
        email_service: EmailService = current_app.extensions['email_service']
        advogado_service: AdvogadoService = current_app.extensions['advogado_service']
        advogado = advogado_service.find_by_email(email)

        if advogado is None:
            return jsonify({
                'status': 'error',
                'message': 'ERROR_ADVOGADO_NOT_FOUND'
            }), 404


        redis.setex(f"pwreset:{token}", 3600, email)
        email_service.send_pwd_recovery(email, advogado.username, f'{request.host_url}/recovery?token={token}&username={advogado.username}')
        return jsonify({'message': 'SUCCESS'}), 200


@cross_origin()
@advogado_bp.route('/reset-password/', methods=['POST'])
def reset_password():
    data = request.get_json(),
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({
            'status': 'error',
            'message': 'REQUIRED_FIELDS_EMPTY'
        }), 400

    with current_app.app_context():
        redis: Redis = current_app.extensions['redis']
        advogado_service: AdvogadoService = current_app.extensions['advogado_service']

        email = redis.get(f'pwreset:{token}')
        if not email:
            return jsonify({
                'status': 'error',
                'message': 'INVALID_PASSWORD_RESET_TOKEN'
            }), 401

        advogado = advogado_service.find_by_email(email)
        if advogado is None:
            current_app.logger.debug(f"The email related to the password token was invalid. The account which requested the password reset was probably deleted.")
            return jsonify({
                'status': 'error',
                'message': 'INVALID_PASSWORD_RESET_TOKEN'
            }), 401

        advogado_service.update_advogado(advogado.access_token, password=new_password)
        redis.delete(f'pwreset:{token}')
        return jsonify({'message': 'SUCCESS'}), 200
