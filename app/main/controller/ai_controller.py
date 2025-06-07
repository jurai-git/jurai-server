from typing import List

from flask import Blueprint, current_app, request
from flask_cors import CORS, cross_origin

from app.main.controller import require_auth
from app.main.model.dto.semantic_search_dto import SemanticSearchDTO
from app.main.model.processo import Processo
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

        entries = ai_service.semantic_search(search)
        processos = processo_service.get_all_by_num_tjmg([entry.numero_tjmg for entry in entries])

        if len(processos) == 0 or len(entries) == 0:
            return jsonify({
                'status': 'error',
                'message': 'ERROR_NO_ENTRIES_FOUND'
            }), 404

        if len(processos) != len(entries):
            return jsonify({
                'status': 'error',
                'message': 'INTEGRITY_ERROR'
            }), 500

        dtos: List[SemanticSearchDTO] = []
        for i, _ in enumerate(processos):
            dtos.append(SemanticSearchDTO(processos[i], entries[i].similarity))

        return jsonify({
            'status': 'SUCCESS',
            'entries': [dto.serialize() for dto in dtos]
        })
