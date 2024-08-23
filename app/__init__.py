import os

from flask import Flask, jsonify, request
from flask.cli import load_dotenv
from flask_cors import cross_origin

from dotenv import load_dotenv
from app.config import Config
from app.main.service.advogado_service import AdvogadoService
from app.main.service.requerente_service import RequerenteService
from app.main.extensions import db

def create_app(config_class=Config):
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
    app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+mysqlconnector://' + user + ":" + password + "@" + host + ":3306/" + db_name)
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)
    app.extensions['db'] = db
    with app.app_context():
        from app.main.model.advogado import Advogado
        from app.main.model.requerente import Requerente
        db.create_all()
    # service initialization
    advogado_service = AdvogadoService(db)
    app.extensions['advogado_service'] = advogado_service
    requerente_service = RequerenteService(db)
    app.extensions['requerente_service'] = requerente_service

    @app.before_request
    def before_request():
        request.charset = 'utf-8'

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app