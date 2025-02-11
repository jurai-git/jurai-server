import os

from flask import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    VAR_FOLDER = os.path.join(os.getcwd(), 'var/')

import pytest

from app import create_app, db
from app.test.conftest import TestConfig


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app(config_class=TestConfig, use_ai=False, testing=True)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def session(app):
    """Create a new database session for each test with rollback."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        options = dict(bind=connection)
        db.session = db.create_scoped_session(options=options)
        yield db.session
        db.session.expire_all()
        transaction.rollback()
        connection.close()
        db.session.remove()