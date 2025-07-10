import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dream_layer import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client