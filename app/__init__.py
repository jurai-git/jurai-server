import os

from flask import Flask, jsonify, request
from flask_cors import cross_origin

from dotenv import load_dotenv
from app.config import Config
from app.main.service.advogado_service import AdvogadoService
from app.main.service.requerente_service import RequerenteService
from app.main.service.demanda_service import DemandaService
from app.main.extensions import db
from app.main import get_ai_bp

def create_app(use_ai=True, config_class=Config):
    # create the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    os.makedirs(app.config['VAR_FOLDER'], exist_ok=True)
    load_dotenv()

    # db initialization
    host = os.getenv("MYSQL_HOST")
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db_name = os.getenv("MYSQL_DB")
    app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql+mysqlconnector://" + user + ":" + password + "@" + host + ":3306/" + db_name)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'max_overflow': 5,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'echo': False,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 5,
        }
    }


    db.init_app(app)
    app.extensions['db'] = db
    with app.app_context():
        from app.main.model.advogado import Advogado
        from app.main.model.requerente import Requerente
        from app.main.model.demanda import Demanda
        from app.main.model.ai_data import AiData
        from app.main.model.argumento import Argumento
        db.create_all()

    # service initialization
    advogado_service = AdvogadoService(db)
    app.extensions['advogado_service'] = advogado_service
    requerente_service = RequerenteService(db)
    app.extensions['requerente_service'] = requerente_service
    demanda_service = DemandaService(db)
    app.extensions['demanda_service'] = demanda_service

    @app.before_request
    def before_request():
        request.charset = 'utf-8'

    @app.route("/", methods=['GET'])
    def index():
        return jsonify({"url_map": app.url_map.__str__()}), 200


    @app.route("/teapot/")
    def teapot():
        return jsonify({"message": "IM_A_TEAPOT"}), 418

    from app.main import main_bp as main_bp
    app.register_blueprint(main_bp)

    if use_ai:
        print("using ai")
        app.register_blueprint(get_ai_bp())

    return app
