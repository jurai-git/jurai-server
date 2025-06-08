from typing import List, Tuple

from flask import Blueprint, current_app, request
from flask.wrappers import Response
from flask_cors import CORS, cross_origin

from app.main.controller import require_auth
from app.main.model.dto.semantic_search_dto import SemanticSearchDTO
from app.main.util import pdf_utils as pdf, normalizer

from keras.src.saving import load_model
from models.probability.inference import *
from models.probability.utils import *

ai_bp = Blueprint('ai', __name__)
CORS(ai_bp)

ALLOWED_EXTENSIONS = ['pdf']

prob_model = load_model('models/probability/probability.keras')
prob_tokenizer = build_tokenizer_from_csv(
    'models/datasets/dataset.csv',
    32_000,
    '<00V>'
)

@cross_origin()
@require_auth
@ai_bp.route('/probability', methods=['POST'])
def probability_model(advogado):
    try:
        text = ''
        json = request.get_json()

        if 'text' in json:
            text = json.get('text').strip()
        elif 'pdf' in request.files:
            text = normalizer.get_ementa(pdf.as_text(request.files['pdf'])).strip()
        else:
            return jsonify({'message': 'ERROR_REQUIRED_FIELDS_EMPTY'}), 400

        return prob_inference(prob_model, prob_tokenizer, text)
    except Exception as e:
        current_app.logger.warning(f"Returning 500 due to {e}")
        return jsonify({'message': "INTERNAL_SERVER_ERROR", "error": str(e)}), 500

@cross_origin()
@ai_bp.route('/tjmg-semantic-search', methods=['GET'])
@require_auth
def semantic_search(advogado):
    data = request.get_json()
    search = data.get('search')

    if not search:
        return jsonify({
            'status': 'error',
            'message': 'ERROR_REQUIRED_FIELDS_EMPTY'
        }), 400

    with current_app.app_context():
        ai_service = current_app.extensions['ai_service']
        processo_service = current_app.extensions['processo_service']

        dtos = ai_service.retrieve_or_return_error(search, processo_service)

        if type(dtos) == tuple: # error
            return dtos

        return jsonify({
            'status': 'SUCCESS',
            'entries': [dto.serialize() for dto in dtos]
        })

@cross_origin()
@ai_bp.route('/rag', methods=['GET'])
@require_auth
def rag(advogado):
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({
            'status': 'error',
            'message': 'ERROR_REQUIRED_FIELDS_EMPTY'
        }), 400

    with current_app.app_context():
        ai_service = current_app.extensions['ai_service']
        processo_service = current_app.extensions['processo_service']

        refined_query = ai_service.refine_query(query)
        search_result = ai_service.retrieve_or_return_error(refined_query, processo_service)

        if type(search_result) == tuple: # error
            return search_result

        return ai_service.generate_final_answer_or_error(query, search_result)



