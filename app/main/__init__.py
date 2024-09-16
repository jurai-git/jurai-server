from flask import Blueprint
from flask_cors import CORS

bp = Blueprint('main', __name__)
CORS(bp)

from app.main.controller.advogado_controller import advogado_bp
bp.register_blueprint(advogado_bp, url_prefix='/advogado')

from app.main.controller.ai_controller import ai_bp
bp.register_blueprint(ai_bp, url_prefix='/ai')

from app.main.controller.requerente_controller import requerente_bp
bp.register_blueprint(requerente_bp, url_prefix='/requerente')

from app.main.controller.demanda_controller import demanda_bp
bp.register_blueprint(demanda_bp, url_prefix="/demanda")
