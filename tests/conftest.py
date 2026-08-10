import pytest
from app import create_app
from app.extensions import db as _db
from config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()          # build all tables fresh, in memory
        yield app
        _db.session.remove()
        _db.drop_all()            # tear down after the test finishes

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    return _db