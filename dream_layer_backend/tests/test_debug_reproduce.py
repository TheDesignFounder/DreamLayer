import json
import os
from unittest.mock import patch, MagicMock

def test_debug_reproduce(client, tmp_path):
    dummy_job = {
        "workflow": {"dummy": "data"},
        "output_path": str(tmp_path / "output.png")
    }

    os.makedirs(os.path.expanduser('~/jobs'), exist_ok=True)
    last_job_path = os.path.expanduser('~/jobs/last.json')

    # Write original content clearly
    with open(dummy_job['output_path'], 'wb') as f:
        f.write(b'original content')

    # Save the last job data
    with open(last_job_path, 'w') as f:
        json.dump(dummy_job, f)

    # Define a side effect function for mocking requests.post
    def mock_requests_post(*args, **kwargs):
        # Clearly simulate successful ComfyUI workflow execution
        with open(dummy_job['output_path'], 'wb') as f:
            f.write(b'original content')  # Restore original content clearly
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        return mock_response

    # Mutate file content clearly before calling the endpoint
    with open(dummy_job['output_path'], 'wb') as f:
        f.write(b'mutated content')

    # Mock 'requests.post' directly to prevent real HTTP calls
    with patch('requests.post', side_effect=mock_requests_post):

        response = client.get('/debug/reproduce')

        assert response.status_code == 200
        assert response.get_json() == {"match": False}
