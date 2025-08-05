import os
import pytest
import torch
import base64
import io
import numpy as np
from unittest import mock
from PIL import Image
from comfy_api_nodes.nodes_runway import RunwayText2ImgNode
from ComfyUI.utils.json_util import merge_json_recursive

@mock.patch("requests.post")
@mock.patch("requests.get")
def test_generate_success(mock_get, mock_post):
    """Test full flow with mocked API."""
    node = RunwayText2ImgNode()
    
    # Fake "task created" response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"id": "task123"}

    # Fake polling that returns successful status and output URL
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "status": "SUCCEEDED",
        "output": ["https://fake-image.com/image.png"]
    }

    # Mock final image download
    img = Image.new("RGB", (64, 64), color="blue")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    mock_image_bytes = img_buffer.getvalue()
    
    with mock.patch("requests.get") as mock_download:
        mock_download.return_value.status_code = 200
        mock_download.return_value.content = mock_image_bytes

        os.environ["RUNWAY_API_KEY"] = "fake_key"
        result = node.generate(prompt="Test", ratio="1:1", timeout=10)

        assert isinstance(result, tuple)
        assert isinstance(result[0], torch.Tensor)
        assert result[0].shape[1] == 3  # Channels

def test_api_key_missing():
    """Should raise ValueError if RUNWAY_API_KEY is not set."""
    node = RunwayText2ImgNode()
    if "RUNWAY_API_KEY" in os.environ:
        del os.environ["RUNWAY_API_KEY"]

    with pytest.raises(ValueError) as exc_info:
        node.generate(prompt="Test", ratio="1:1")
    
    assert "RUNWAY_API_KEY environment variable is missing" in str(exc_info.value)

def test_empty_prompt_raises():
    node = RunwayText2ImgNode()
    os.environ["RUNWAY_API_KEY"] = "fake_key"
    
    with pytest.raises(ValueError) as exc_info:
        node.generate(prompt="   ", ratio="1:1")
    
    assert "Prompt cannot be empty" in str(exc_info.value)

@mock.patch("requests.post")
def test_http_401(mock_post):
    node = RunwayText2ImgNode()
    os.environ["RUNWAY_API_KEY"] = "fake_key"

    mock_post.return_value.status_code = 401
    mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")

    with pytest.raises(PermissionError) as exc_info:
        node.generate(prompt="A dog flying", ratio="1:1")
    
    assert "Invalid API key" in str(exc_info.value)
