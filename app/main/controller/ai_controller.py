import os
import random
import string

from flask import Blueprint, current_app, request, jsonify
from flask_cors import CORS, cross_origin
from app.main.util import pdf_utils as pdf, normalizer
import traceback

from keras.src.saving import load_model
from models.inference import *
from models.utils import *

ai_bp = Blueprint('ai', __name__)
CORS(ai_bp)

ALLOWED_EXTENSIONS = ['pdf']

prob_model = load_model('models/probability.keras')
prob_tokenizer = build_tokenizer_from_csv(
    'models/datasets/normalized_dataset__ementa_probability_ai.csv',
    32_000,
    '<00V>'
)

@cross_origin()
@ai_bp.route('/probability', methods=['POST'])
def probability_model():
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
        print(traceback.format_exc(e))
        return jsonify({'message': "INTERNAL_SERVER_ERROR", "error": str(e)}), 500
