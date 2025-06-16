from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS, cross_origin

from app.main.controller import require_auth
from app.main.model.demanda import Demanda
from app.main.service import requerente_service
from app.main.service import advogado_service
from app.main.service.advogado_service import AdvogadoService
from app.main.service.ai_service import AIService
from app.main.service.chat_service import ChatService
from app.main.service.demanda_service import DemandaService
from app.main.service.requerente_service import RequerenteService

demanda_bp = Blueprint('demanda', __name__)
CORS(demanda_bp)

@cross_origin()
@demanda_bp.route("/requerente/<int:id_requerente>/demanda", methods=['POST'])
@require_auth
def create_demanda(advogado, id_requerente):
    data = request.get_json()

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

    if foro is None or status is None or competencia is None or assunto_principal is None or pedido_liminar is None or segredo_justica is None or valor_acao is None or dispensa_legal is None or justica_gratuita is None or guia_custas is None or resumo is None:
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
            return jsonify({"message": "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@demanda_bp.route("/demanda/<int:demanda_id>", methods=['DELETE'])
@require_auth
def delete_demanda(advogado, demanda_id):

    with current_app.app_context():
        demanda_service: DemandaService = current_app.extensions['demanda_service']

        try:
            demanda = demanda_service.get_by_id(demanda_id)

            if not demanda:
                return jsonify({'message': 'ERROR_INVALID_ID'}), 404

            demanda_service.delete_demanda(demanda, advogado.id_advogado)
            return jsonify({'message': 'SUCCESS'}), 200

        except Exception as e:
            current_app.logger.error(f"Error deleting demanda: {str(e)}", exc_info=True)
            return jsonify({
                'message': 'INTERNAL_SERVER_ERROR',
                'error': str(e)
            }), 500


@cross_origin()
@demanda_bp.route("/demanda/<int:id_demanda>", methods=['PATCH'])
@require_auth
def update_demanda(advogado, id_demanda):
    data = request.get_json()

    with current_app.app_context():
        try:
            demanda_service = current_app.extensions['demanda_service']

            demanda = demanda_service.get_by_id(id_demanda)
            if not demanda:
                return jsonify({"message": "ERROR_DEMANDA_DOESNT_EXIST"}), 404

            if demanda.requerente.advogado_id != advogado.id_advogado:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            try:
                demanda_service.update_demanda(demanda, data)
                return jsonify({"message": "SUCCESS"}), 200
            except PermissionError:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

        except Exception as e:
            current_app.logger.error(f"Error updating demanda: {str(e)}", exc_info=True)
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            }), 500


@cross_origin()
@demanda_bp.route("/demanda/<int:id_demanda>", methods=['GET'])
@require_auth
def get_demanda(advogado, id_demanda):

    with current_app.app_context():
        try:
            demanda_service = current_app.extensions['demanda_service']
            demanda = demanda_service.get_by_id(id_demanda)

            if not demanda:
                return jsonify({"message": "ERROR_DEMANDA_DOESNT_EXIST"}), 404

            if not demanda or demanda.requerente.advogado_id != advogado.id_advogado:
                return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

            return jsonify({
                "message": "SUCCESS",
                "demanda": demanda.serialize()
            }), 200

        except Exception as e:
            current_app.logger.error(f"Error getting demanda: {str(e)}", exc_info=True)
            return jsonify({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            }), 500

@cross_origin()
@demanda_bp.route("/demanda/<int:id_demanda>/rag", methods=['POST'])
@require_auth
def chat_with_demanda(advogado, id_demanda):
    data = request.get_json()
    query = data.get("query")
    if query is None or query.strip() == "":
        return jsonify({"message": "REQUIRED_FIELDS_LEFT_EMPTY"}), 400

    wants_rag = data.get("rag")
    wants_rag = wants_rag is not None and wants_rag.strip() != ""

    with current_app.app_context():
        # first, load the demanda
        demanda_service = current_app.extensions['demanda_service']
        demanda = demanda_service.get_by_id(id_demanda)

        if not demanda:
            return jsonify({"message": "ERROR_DEMANDA_DOESNT_EXIST"}), 404

        if demanda.requerente.advogado_id != advogado.id_advogado:
            return jsonify({"message": "ERROR_ACCESS_DENIED"}), 403

        ai_service: AIService = current_app.extensions['ai_service']

        response = ai_service.generate_answer_with_history_or_error(query, wants_rag, demanda.id_demanda)
        print(response)
        return jsonify({"response": response}), 200

@cross_origin()
@demanda_bp.route("/demanda/<int:id_demanda>/rag", methods=['GET'])
@require_auth
def get_chat(advogado, id_demanda):

    with current_app.app_context():
        chat_service = current_app.extensions['chat_service']

        chat = chat_service.get_or_create_chat(id_demanda)

        return jsonify({
            "chat": chat.serialize()
        }), 200