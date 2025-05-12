from flask import Blueprint
from flask_cors import CORS

main_bp = Blueprint('main', __name__)
CORS(main_bp)

from app.main.controller.advogado_controller import advogado_bp
main_bp.register_blueprint(advogado_bp, url_prefix='/advogado')

from app.main.controller.requerente_controller import requerente_bp
main_bp.register_blueprint(requerente_bp, url_prefix='/requerente')

from app.main.controller.demanda_controller import demanda_bp
main_bp.register_blueprint(demanda_bp)

def get_ai_bp() -> Blueprint:
    main_ai_bp = Blueprint('ai', __name__)
    from app.main.controller.ai_controller import ai_bp
    main_ai_bp.register_blueprint(ai_bp, url_prefix='/ai')
    return main_ai_bp
