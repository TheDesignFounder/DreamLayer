import sys
import os
# fixes referencing img2img_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
import img2img_server
import pytest

# Flask provides a way to test endpoints using the test client.
@pytest.fixture
def client():
    img2img_server.app.config['TESTING'] = True
    with img2img_server.app.test_client() as client:
        yield client

def test_img2img_no_get(client):
    # Test GET request fails
    response = client.open('/api/img2img', method='GET')
    assert response.status_code == 405 # NOT ALLOWED!