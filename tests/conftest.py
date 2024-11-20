# tests/conftest.py
import pytest
from app import create_app
from config import TestingConfig


@pytest.fixture(scope="module")
def client():
    app = create_app(TestingConfig)
    with app.test_client() as client:
        yield client
