import pytest
from src.api.app import create_app
from src.api.config import Config


@pytest.fixture(scope='function')
def app():
    app = create_app(Config())
    return app


@pytest.fixture(scope='function')
def client(app):
    test_client = app.test_client()
    yield test_client
