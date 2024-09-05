from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

demanda_bp = Blueprint('demanda', __name__)
CORS(demanda_bp)

@cross_origin()
@demanda_bp.route("/new", methods=['POST'])
def create_demanda():
    data = request.json

    advogado_token = data.get("access_token")
    requerente_pk = data.get("requerente_cpf_cnpj")

    with current_app.app_context():
        advogado_service = current_app.extensions['advogado_service']
        requerente_service = current_app.extensions['requerente_service']
        demanda_service = current_app.extensions['demanda_service'] 
