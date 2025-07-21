import os  # Used to set or delete the RUNWAY_API_KEY environment variable
import pytest  # Provides tools like `raises()` for asserting exceptions
from unittest.mock import patch, mock_open  # Used to mock file handling and HTTP requests

# Import the class you're testing
from comfy_api_nodes.runway.runway_img2img import RunwayImg2Img


# Test that the node works properly when the API call succeeds
@patch("builtins.open", new_callable=mock_open, read_data=b"image bytes")  # Mocks file open call
@patch("requests.post")  # Mocks the HTTP POST request to Runway API
def test_runway_node_process(mock_post, mock_file):
    # Simulate a successful API response with status code 200 and JSON body
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}

    # Set a fake API key to satisfy the environment check
    os.environ["RUNWAY_API_KEY"] = "fake-key"

    # Initialize and call the node
    node = RunwayImg2Img()
    result = node.process("image.png", "a prompt")

    # Assert that the response JSON matches the mocked response
    assert result["status"] == "success"


# Test that an appropriate error is raised when the API key is missing
def test_missing_api_key():
    # Ensure the environment variable is not set
    if "RUNWAY_API_KEY" in os.environ:
        del os.environ["RUNWAY_API_KEY"]

    # Check that initializing the node raises an EnvironmentError
    with pytest.raises(EnvironmentError, match="Missing RUNWAY_API_KEY"):
        RunwayImg2Img()
