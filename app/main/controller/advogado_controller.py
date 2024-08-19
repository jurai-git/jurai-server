from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

advogado_bp = Blueprint('advogado', __name__)
CORS(advogado_bp)

@cross_origin()
@advogado_bp.route('/create', methods=['POST'])
def create_advogado():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    oab = data.get('oab')
    email = data.get('email')

    if not username or not password or not oab or not email:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        if advogado_service.find_by_uname(username) or advogado_service.find_by_email(email):
            return jsonify({"message": "ERROR_CONFLICT"}), 409

        user = advogado_service.create_advogado(username, password, oab, email)
        return jsonify({"message": "SUCCESS", "access_token": user.access_token}), 201


@cross_origin()
@advogado_bp.route("/auth", methods=['POST'])
def auth():
    data = request.json
    uname = data.get('username')
    password = data.get('password')

    if not uname or not password:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        access_token = advogado_service.get_token(uname, password)
        if access_token:
            return jsonify({"message": "SUCCESS", "access_token": access_token}), 201