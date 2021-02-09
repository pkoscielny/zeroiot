import pytest
from app import create_app
# from app.models import db

@pytest.fixture
def app():
    app = create_app('test')
    # with app.app_context():
    #     app.init_db()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
