import sys
import os
# fixes referencing img2img_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
import txt2img_server
import pytest
import json
from unittest.mock import patch

# Flask provides a way to test endpoints using the test client.
@pytest.fixture
def client():
    txt2img_server.app.config['TESTING'] = True
    with txt2img_server.app.test_client() as client:
        yield client

def mockfn(*args, **kwargs):
    print("MOCKED FUNCTION!")

def test_txt2img_no_get(client):
    # Test GET request fails
    response = client.open('/api/txt2img', method='GET')
    assert response.status_code == 405 # NOT ALLOWED!

def test_txt2img_mock(client):
    # with patch('txt2img_server.transform_to_txt2img_workflow',side_effect=mockfn) as mock_dep:
    data = {'key':'value'}
    response = client.post('/api/txt2img',
                            data=json.dumps(data),
                            content_type="application/json")
    assert response is not None