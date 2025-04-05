from functools import wraps

from flask import request, current_app, jsonify


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bearer = request.headers.get('Authorization')
        if not bearer:
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401

        access_token = bearer.split()[1]
        with current_app.app_context():
            advogado_service = current_app.extensions['advogado_service']
            advogado = advogado_service.find_by_token(access_token)
            if not advogado:
                return jsonify({"message": "ERROR_INVALID_CREDENTIALS"}), 401
            return f(advogado, *args, **kwargs)

    return decorated