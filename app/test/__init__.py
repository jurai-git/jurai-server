import pytest

from app import create_app, db
from app.test.conftest import TestConfig


@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app(config_class=TestConfig, use_ai=False, testing=True)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='module')
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
        transaction.rollback()
        connection.close()
        db.session.remove()