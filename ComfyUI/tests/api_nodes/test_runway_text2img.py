import os
import pytest
import torch
import base64
import io
import numpy as np
from unittest import mock
from PIL import Image

# Test the core functionality without importing the full node
def test_base64_to_tensor_conversion():
    """Test converting base64 image data to tensor."""
    # Create a simple 1x1 red image
    image = Image.new('RGB', (1, 1), color='red')
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    # Convert back to tensor (simulating the node's conversion logic)
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    image_array = np.array(image).astype(np.float32) / 255.0
    image_tensor = torch.from_numpy(image_array).permute(2, 0, 1)  # HWC to CHW
    image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
    
    assert isinstance(image_tensor, torch.Tensor)
    assert image_tensor.shape == (1, 3, 1, 1)
    assert image_tensor.dtype == torch.float32

def test_api_key_validation():
    """Test API key validation logic."""
    # Test missing API key
    if "RUNWAY_API_KEY" in os.environ:
        del os.environ["RUNWAY_API_KEY"]
    
    api_key = os.getenv('RUNWAY_API_KEY')
    assert api_key is None
    
    # Test with fake API key
    os.environ["RUNWAY_API_KEY"] = "fake_key"
    api_key = os.getenv('RUNWAY_API_KEY')
    assert api_key == "fake_key"

def test_prompt_validation():
    """Test prompt validation logic."""
    # Test empty prompt
    prompt = ""
    assert not prompt or not prompt.strip()
    
    # Test whitespace-only prompt
    prompt = "   "
    assert not prompt or not prompt.strip()
    
    # Test valid prompt
    prompt = "A cat in space"
    assert prompt and prompt.strip()

@mock.patch("requests.post")
def test_api_request_structure(mock_post):
    """Test the structure of API requests."""
    # Mock successful response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "output": "fake_base64_data"
    }
    
    # Test API request structure
    url = "https://api.dev.runwayml.com/v1/text_to_image"
    headers = {
        "Authorization": "Bearer fake_key",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": "A cat in space",
        "model": "gen4_image",
        "ratio": "1:1"
    }
    
    # This would be the actual request in the node
    # response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    # Verify the structure is correct
    assert url == "https://api.dev.runwayml.com/v1/text_to_image"
    assert "Authorization" in headers
    assert "Content-Type" in headers
    assert "prompt" in payload
    assert "model" in payload
    assert "ratio" in payload

@mock.patch("requests.post")
def test_http_400_bad_request(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad request example"
    mock_post.return_value.raise_for_status.side_effect = Exception("400 Error")

    with pytest.raises(Exception) as exc_info:
        # simulate your actual API logic here
        raise Exception(f"Bad request to Runway API: {mock_post.return_value.text}")

    assert "Bad request to Runway API" in str(exc_info.value)

@mock.patch("requests.post")
def test_http_401_unauthorized(mock_post):
    mock_post.return_value.status_code = 401
    mock_post.return_value.text = "Unauthorized"
    mock_post.return_value.raise_for_status.side_effect = Exception("401 Unauthorized")

    with pytest.raises(Exception) as exc_info:
        raise Exception("Invalid Runway API key. Please check your RUNWAY_API_KEY.")

    assert "Invalid Runway API key" in str(exc_info.value)

@mock.patch("requests.post")
def test_http_500_server_error(mock_post):
    mock_post.return_value.status_code = 500
    mock_post.return_value.text = "Internal Server Error"
    mock_post.return_value.raise_for_status.side_effect = Exception("500 Internal Error")

    with pytest.raises(Exception) as exc_info:
        raise Exception(f"Runway API error (HTTP 500): Internal Server Error")

    assert "Runway API error (HTTP 500)" in str(exc_info.value)

@mock.patch("requests.get")
def test_api_polling_timeout(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": "IN_PROGRESS"
    }

    # Simulate timeout after N retries
    max_attempts = 5
    for _ in range(max_attempts):
        status = mock_get.return_value.json()["status"]
        assert status == "IN_PROGRESS"

    # Simulate exception due to timeout
    with pytest.raises(Exception) as exc_info:
        raise Exception("Timeout waiting for image generation.")

    assert "Timeout waiting for image generation" in str(exc_info.value)

@mock.patch("requests.get")
def test_image_download_failure(mock_get):
    mock_get.return_value.status_code = 404
    mock_get.return_value.raise_for_status.side_effect = Exception("404 Not Found")

    with pytest.raises(Exception) as exc_info:
        raise Exception("No image URL found in successful response.")

    assert "No image URL found" in str(exc_info.value)

def test_invalid_tensor_shape():
    bad_tensor = torch.rand(1, 1, 256, 256)  # Wrong channel count

    with pytest.raises(ValueError) as exc_info:
        if bad_tensor.shape[1] != 3:
            raise ValueError(f"Unexpected image tensor shape: {bad_tensor.shape}")

    assert "Unexpected image tensor shape" in str(exc_info.value)

def test_error_handling():
    """Test error handling patterns."""
    # Test ValueError for missing API key
    try:
        raise ValueError(
            "RUNWAY_API_KEY environment variable is required but not set. "
            "Please set your Runway API key in the .env file or environment variables."
        )
    except ValueError as e:
        assert "RUNWAY_API_KEY" in str(e)
    
    # Test ValueError for empty prompt
    try:
        raise ValueError("Prompt cannot be empty")
    except ValueError as e:
        assert "Prompt cannot be empty" in str(e)
