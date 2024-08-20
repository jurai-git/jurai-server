from flask import Blueprint
from flask_cors import CORS

bp = Blueprint('main', __name__)
CORS(bp)

from app.main.controller.advogado_controller import advogado_bp
bp.register_blueprint(advogado_bp, url_prefix='/user')

from app.main.controller.ai_controller import ai_bp
bp.register_blueprint(ai_bp, url_prefix='/ai')