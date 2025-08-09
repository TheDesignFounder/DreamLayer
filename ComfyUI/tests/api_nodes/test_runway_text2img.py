import pytest
from unittest import mock
from io import BytesIO
from PIL import Image
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../custom_nodes')))
from runway_text2img import RunwayText2Image



@pytest.fixture
def dummy_image_bytes():
    """Returns PNG bytes of a 1x1 black image."""
    img = Image.new("RGB", (1, 1))
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

@mock.patch("runway_text2img.requests.get")
@mock.patch("runway_text2img.requests.post")
@mock.patch("runway_text2img.os.getenv")
def test_runway_text2img_node_success(mock_getenv, mock_post, mock_get, dummy_image_bytes):
    # Mock environment variable
    mock_getenv.return_value = "fake_api_key"

    # Mock POST response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwBchNsxAEthMtT_uv1MInGKEi4A0W2b1mx1flcpNOoUMkiy0CCnLfKF55jqIiRB9Mx-Y&usqp=CAU"}

    # Mock GET image download
    mock_get.return_value.content = dummy_image_bytes

    # Instantiate node
    node = RunwayText2Image()

    # Run node
    outputs = node.generate_image(prompt="test prompt", poll_timeout=10)

    # Validate output
    assert isinstance(outputs, tuple)
    assert isinstance(outputs[0], Image.Image)
    assert outputs[0].size == (1, 1)

@mock.patch("runway_text2img.os.getenv")
def test_runway_text2img_missing_api_key(mock_getenv):
    mock_getenv.return_value = None
    node = RunwayText2Image()

    with pytest.raises(RuntimeError, match="RUNWAY_API_KEY"):
        node.generate_image(prompt="test", poll_timeout=10)
