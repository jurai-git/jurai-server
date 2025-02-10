from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

from app.main.controller import require_auth
from app.main.model.demanda import Demanda
from app.main.service import requerente_service
from app.main.service import advogado_service
from app.main.service.advogado_service import AdvogadoService
from app.main.service.demanda_service import DemandaService
from app.main.service.requerente_service import RequerenteService

demanda_bp = Blueprint('demanda', __name__)
CORS(demanda_bp)

@cross_origin()
@demanda_bp.route("/new", methods=['POST'])
@require_auth
def create_demanda(advogado):
    print(request.get_json())
    data = request.get_json()

    id_requerente = data.get("id_requerente")
    identificacao = data.get("identificacao")
    foro = data.get("foro")
    status = data.get("status")
    competencia = data.get("competencia")
    classe = data.get("classe")
    assunto_principal = data.get("assunto_principal")
    pedido_liminar = data.get("pedido_liminar")
    segredo_justica = data.get("segredo_justica")
    valor_acao = data.get("valor_acao")
    dispensa_legal = data.get("dispensa_legal")
    justica_gratuita = data.get("justica_gratuita")
    guia_custas = data.get("guia_custas")
    resumo = data.get("resumo")

    print(f"foro: {foro}")
    print(f"status: {status}")
    print(f"id_requerente: {id_requerente}")
    print(f"identificacao: {identificacao}")
    print(f"competencia: {competencia}")
    print(f"classe: {classe}")
    print(f"assunto_principal: {assunto_principal}")
    print(f"pedido_liminar: {pedido_liminar}")
    print(f"segredo_justica: {segredo_justica}")
    print(f"valor_acao: {valor_acao}")
    print(f"dispensa_legal: {dispensa_legal}")
    print(f"justica_gratuita: {justica_gratuita}")
    print(f"guia_custas: {guia_custas}")
    print(f"resumo: {resumo}")

    if foro is None or status is None or competencia is None or assunto_principal is None or pedido_liminar is None or segredo_justica is None or valor_acao is None or dispensa_legal is None or justica_gratuita is None or guia_custas is None or resumo is None or status is None:
        return jsonify({"message": "REQUIRED_FIELDS_LEFT_EMPTY"}), 400

    with current_app.app_context():
        requerente_service: RequerenteService = current_app.extensions['requerente_service']
        demanda_service: DemandaService = current_app.extensions['demanda_service']

        try:
            requerente = requerente_service.get_by_id(id_requerente)
            if requerente is None:
                return jsonify({"message": "ERROR_REQUERENTE_DOESNT_EXIST"}), 404

            if not requerente.advogado_id == advogado.id_advogado:
                return jsonify({"message": "ERROR_PERMISSION_DENIED"}), 403

            d = demanda_service.create_demanda(identificacao=identificacao, foro=foro, competencia=competencia, classe=classe, assunto_principal=assunto_principal, pedido_liminar=pedido_liminar, segredo_justica=segredo_justica, valor_acao=valor_acao, dispensa_legal=dispensa_legal, justica_gratuita=justica_gratuita, guia_custas=guia_custas, resumo=resumo, status=status, id_requerente=id_requerente)

            return jsonify({"message": "SUCCESS", "demanda": demanda_service.serialize(d)})
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

@cross_origin
@demanda_bp.route("/update", methods=['PUT'])
@require_auth
def update_demanda(advogado):
    data = request.get_json()

    id_demanda = data.get("id_demanda")
    id_requerente = data.get("id_requerente")

    if not id_requerente or not id_demanda:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        try:
            requerente_service = current_app.extensions['requerente_service']
            demanda_service = current_app.extensions['demanda_service']

            requerente  = requerente_service.get_by_id(id_requerente)
            if requerente is None:
                return jsonify({"message": "ERROR_REQUERENTE_DOESNT_EXIST"}), 404

            if not requerente.advogado_id == advogado.id_advogado:
                print("advogado doesnt own requerente")
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            demanda = demanda_service.get_by_id(id_demanda)
            if demanda is None:
                return jsonify({"message": "ERROR_DEMANDA_DOESNT_EXIST"}), 404

            try:
                demanda_service.update_demanda(requerente, demanda, data)
            except PermissionError as e:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": e}), 500

        return jsonify({"message": "SUCCESS"}), 200


@cross_origin()
@demanda_bp.route("/delete", methods=['DELETE'])
@require_auth
def delete_demanda(advogado):
    data = request.get_json()

    demanda_id = data.get('demanda_id')
    requerente_id = data.get('requerente_id')

    if not demanda_id or not requerente_id:
        return jsonify({"message": "ERROR_REQUIRED_FIELDS_EMPTY"}), 400

    with current_app.app_context():
        demanda_service: DemandaService = current_app.extensions['demanda_service']
        requerente_service: RequerenteService = current_app.extensions['requerente_service']

        demanda = demanda_service.get_by_id(demanda_id)
        requerente = requerente_service.get_by_id(requerente_id)
        if requerente not in advogado.requerentes:
            return jsonify({"message": "ERROR_INVALID_CREDENTIALS"})

        if not demanda or not requerente:
            return jsonify({'message': 'ERROR_INVALID_ID'}), 404

        try:
            demanda_service.delete_demanda(demanda, requerente)
            return jsonify({'message': 'SUCCESS'}), 200
        except Exception as e:
            current_app.logger.warning(f"Returning 500 due to {e}")
            return jsonify({'message': 'INTERNAL_SERVER_ERROR', 'error': str(e)}), 500
