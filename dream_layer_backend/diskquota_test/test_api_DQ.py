import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from txt2img_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_txt2img_returns_507_on_low_disk(mocker, client):
    # Patch disk usage to simulate low disk
    mocker.patch('shutil.disk_usage', return_value=(100*1024**3, 99.9*1024**3, 0.1*1024**3))
    # Minimal valid POST. Adjust as appropriate.
    json_payload = {"prompt": "test", "negative_prompt": ""}
    response = client.post('/api/txt2img', json=json_payload)
    assert response.status_code == 507
    data = response.get_json()
    assert "quota" in data["message"].lower() or "disk" in data["message"].lower()