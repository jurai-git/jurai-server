import os
import random
import string

from flask import Blueprint, current_app, request, jsonify
from flask_cors import CORS, cross_origin
from app.main.util import pdf_utils as pdf, normalizer

ai_bp = Blueprint('ai', __name__)
CORS(ai_bp)

ALLOWED_EXTENSIONS = ['pdf']

@cross_origin()
@ai_bp.route('/odds', methods=['POST'])
def odds_from_document():

    with current_app.app_context():
        folder = current_app.config.get('VAR_FOLDER')

    file_id = ''.join(random.choices(string.ascii_letters, k=8))
    file = request.files.get('file')
    file.save(os.path.join(folder, 'pdf_entry_' + file_id + '.pdf'))
    ementa = normalizer.get_ementa(pdf.as_text(file))
    return jsonify({"message": "SUCCESS", "ementa": ementa}), 201

