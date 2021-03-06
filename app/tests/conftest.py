import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app('test')
    yield app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def add_air_state(client):
    air_state = {
        'type': 'air_state',
        'attributes': {
            'temperature': '20.1',
            'humidity': '51.2',
            'location': 'kitchen',
            'device': 'dev1_esp',
        },
    }
    with client:
        client.post(
            '/air_state',
            json={'data': air_state},
            content_type='application/vnd.api+json',
        )
    yield air_state


@pytest.fixture
def add_insolation(client):
    insolation = {
        'type': 'insolation',
        'attributes': {
            'insolation': '420',
            'device': 'dev1_esp',
        },
    }
    with client:
        client.post(
            '/insolation',
            json={'data': insolation},
            content_type='application/vnd.api+json',
        )
    yield insolation
