from flask import blueprints, Blueprint
from flask_cors import CORS

bp = Blueprint('main', __name__)
CORS(bp)

from app.main.controller.advogado_controller import advogado_bp
bp.register_blueprint(advogado_bp, url_prefix='/user')