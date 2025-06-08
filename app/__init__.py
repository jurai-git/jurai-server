import os

from flask import Flask, jsonify, request, send_from_directory

from dotenv import load_dotenv
from app.config import Config
from app.main.service.advogado_service import AdvogadoService
from app.main.service.email_service import EmailService
from app.main.service.processo_service import ProcessoService
from app.main.service.requerente_service import RequerenteService
from app.main.service.demanda_service import DemandaService
from app.main.extensions import db, redis
from app.main import get_ai_bp
from app.main.model.advogado_pfp import AdvogadoPFP

def create_app(use_ai=True, config_class=Config):
    # create the app
    load_dotenv()
    app = Flask(__name__, static_folder='static', static_url_path='', instance_relative_config=True)
    app.config.from_object(config_class)
    os.makedirs(app.config['VAR_FOLDER'], exist_ok=True)

    # check for env variables
    required_env_vars = [
        'MYSQL_HOST',
        'MYSQL_USER',
        'MYSQL_PASSWORD',
        'MYSQL_DB',
        'SMTP_SENDER',
        'SMTP_PASSWORD'
    ]
    if use_ai:
        required_env_vars.append('GEMINI_API_KEY')
        required_env_vars.append('PINECONE_API_KEY')
        required_env_vars.append('PINECONE_INDEX_URL')

    missing = [var for var in required_env_vars if not os.getenv(var)]

    if missing:
        raise RuntimeError(f'Missing env vars: {", ".join(missing)}')

    db_host = os.getenv('MYSQL_HOST')
    db_user = os.getenv('MYSQL_USER')
    db_password = os.getenv('MYSQL_PASSWORD')
    db_name = os.getenv('MYSQL_DB')

    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_sender = os.getenv('SMTP_SENDER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    # db initialization
    app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+mysqlconnector://' + db_user + ':' + db_password + '@' + db_host + ':3306/' + db_name)
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
        from app.main.model.advogado_pfp import AdvogadoPFP
        db.create_all()

    # service initialization
    advogado_service = AdvogadoService(db)
    app.extensions['advogado_service'] = advogado_service
    requerente_service = RequerenteService(db)
    app.extensions['requerente_service'] = requerente_service
    demanda_service = DemandaService(db)
    app.extensions['demanda_service'] = demanda_service
    processo_service = ProcessoService(db)
    app.extensions['processo_service'] = processo_service

    email_service = EmailService(smtp_sender, smtp_password, smtp_server=smtp_host, smtp_port=smtp_port)
    app.extensions['email_service'] = email_service

    # initialize redis
    app.extensions['redis'] = redis

    # if using AI, initialize RAG, AI service and gemini client
    if use_ai:
        from app.main.ai_extensions import retriever
        app.extensions['retriever'] = retriever

        from app.main.ai_extensions import gemini_client
        app.extensions['gemini_client'] = gemini_client

        from app.main.service.ai_service import AIService
        ai_service = AIService(db, retriever=retriever, gemini_client=gemini_client)
        app.extensions['ai_service'] = ai_service


    # requests configs
    @app.after_request
    def cors_postprocess(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response

    @app.before_request
    def handle_options():
        request.charset = 'utf-8'
        if request.method == 'OPTIONS':
            return '', 204

    @app.route("/", methods=['GET'])
    def index():
        return jsonify({"url_map": app.url_map.__str__()}), 200

    @app.route('/teapot/')
    def teapot():
        return jsonify({'message': 'IM_A_TEAPOT'}), 418

    @app.route('/recovery/<path:filename>')
    def serve_recovery_static(filename):
        return send_from_directory(app.static_folder, filename)

    @app.route('/recovery/')
    def serve_recovery_index():
        return send_from_directory(app.static_folder, 'index.html')

    from app.main import main_bp as main_bp
    app.register_blueprint(main_bp)

    # register AI endpoints
    if use_ai:
        print('using ai')
        app.register_blueprint(get_ai_bp())

    return app
