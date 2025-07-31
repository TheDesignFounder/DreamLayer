import pytest
import os
from unittest.mock import patch, Mock
import numpy as np
from PIL import Image
import io
import requests

from custom_nodes.luma_api.luma_text2img import LumaText2Img
from custom_nodes.luma_api.luma_client import LumaAPIClient


class TestLumaText2Img:
    """Test suite for LumaText2Img node"""

    @pytest.fixture
    def luma_node(self):
        """Create a LumaText2Img node instance"""
        return LumaText2Img()

    @pytest.fixture
    def mock_env_with_key(self):
        """Mock environment with LUMA_API_KEY"""
        with patch.dict(os.environ, {'LUMA_API_KEY': 'test_api_key_123'}):
            # Recreate the node with the mocked environment
            node = LumaText2Img()
            yield node

    @pytest.fixture
    def mock_env_without_key(self):
        """Mock environment without LUMA_API_KEY"""
        with patch.dict(os.environ, {}, clear=True):
            # Recreate the node with the mocked environment
            node = LumaText2Img()
            yield node

    def test_input_types(self, luma_node):
        """Test that INPUT_TYPES returns correct structure"""
        input_types = luma_node.INPUT_TYPES()

        assert "required" in input_types
        required = input_types["required"]

        # Check all required parameters exist
        expected_params = [
            "prompt", "negative_prompt", "width", "height",
            "num_images", "guidance_scale", "num_inference_steps", "seed"
        ]

        for param in expected_params:
            assert param in required

    def test_return_types(self, luma_node):
        """Test that RETURN_TYPES is correct"""
        assert luma_node.RETURN_TYPES == ("IMAGE",)

    def test_function_name(self, luma_node):
        """Test that FUNCTION name is correct"""
        assert luma_node.FUNCTION == "generate_image"

    def test_category(self, luma_node):
        """Test that CATEGORY is correct"""
        assert luma_node.CATEGORY == "image generation"

    def test_validate_api_key_with_key(self, mock_env_with_key):
        """Test API key validation when key is present"""
        # Should not raise an exception
        mock_env_with_key.validate_api_key()

    def test_validate_api_key_without_key(self, mock_env_without_key):
        """Test API key validation when key is missing"""
        with pytest.raises(ValueError, match="LUMA_API_KEY environment variable is not set"):
            mock_env_without_key.validate_api_key()

    def test_validate_dimensions_valid(self, luma_node):
        """Test dimension validation with valid dimensions"""
        valid_sizes = [1024, 1152, 1344]

        for size in valid_sizes:
            # Should not raise an exception
            luma_node.validate_dimensions(size, size)

    def test_validate_dimensions_invalid(self, luma_node):
        """Test dimension validation with invalid dimensions"""
        invalid_sizes = [512, 768, 1536, 2048]

        for size in invalid_sizes:
            with pytest.raises(ValueError, match="Invalid dimensions"):
                luma_node.validate_dimensions(size, size)

    def test_create_generation_request_basic(self, luma_node):
        """Test request payload creation with basic parameters"""
        payload = luma_node.client.create_generation_request(
            prompt="test prompt",
            negative_prompt="",
            width=1024,
            height=1024,
            num_images=1,
            guidance_scale=7.5,
            num_inference_steps=20,
            seed=-1
        )

        assert payload["prompt"] == "test prompt"
        assert payload["width"] == 1024
        assert payload["height"] == 1024
        assert payload["num_images"] == 1
        assert payload["guidance_scale"] == 7.5
        assert payload["num_inference_steps"] == 20
        assert "negative_prompt" not in payload
        assert "seed" not in payload

    def test_create_generation_request_with_negative_prompt(self, luma_node):
        """Test request payload creation with negative prompt"""
        payload = luma_node.client.create_generation_request(
            prompt="test prompt",
            negative_prompt="blurry, low quality",
            width=1024,
            height=1024,
            num_images=1,
            guidance_scale=7.5,
            num_inference_steps=20,
            seed=-1
        )

        assert payload["prompt"] == "test prompt"
        assert payload["negative_prompt"] == "blurry, low quality"

    def test_create_generation_request_with_seed(self, luma_node):
        """Test request payload creation with seed"""
        payload = luma_node.client.create_generation_request(
            prompt="test prompt",
            negative_prompt="",
            width=1024,
            height=1024,
            num_images=1,
            guidance_scale=7.5,
            num_inference_steps=20,
            seed=12345
        )

        assert payload["seed"] == 12345

    @patch('requests.post')
    def test_send_generation_request_success(self, mock_post, mock_env_with_key):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "test_generation_id"}
        mock_post.return_value = mock_response

        result = mock_env_with_key.client.send_generation_request({
            "prompt": "test prompt",
            "width": 1024,
            "height": 1024
        })

        assert result["id"] == "test_generation_id"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_send_generation_request_failure(self, mock_post, mock_env_with_key):
        """Test failed API request"""
        mock_post.side_effect = requests.exceptions.RequestException("API Error")

        with pytest.raises(RuntimeError, match="Failed to send generation request"):
            mock_env_with_key.client.send_generation_request({
                "prompt": "test prompt",
                "width": 1024,
                "height": 1024
            })

    @patch('requests.get')
    def test_poll_for_completion_success(self, mock_get, mock_env_with_key):
        """Test successful polling for completion"""
        # Mock initial pending response
        mock_response_pending = Mock()
        mock_response_pending.json.return_value = {"status": "pending"}

        # Mock final completed response
        mock_response_completed = Mock()
        mock_response_completed.json.return_value = {
            "status": "completed",
            "images": [{"url": "https://example.com/image.jpg"}]
        }

        mock_get.side_effect = [mock_response_pending, mock_response_completed]

        result = mock_env_with_key.client.poll_for_completion("test_id")

        assert result["status"] == "completed"
        assert len(result["images"]) == 1

    @patch('requests.get')
    def test_poll_for_completion_failed(self, mock_get, mock_env_with_key):
        """Test failed polling for completion"""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "failed", "error": "Generation failed"}
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="Generation failed"):
            mock_env_with_key.client.poll_for_completion("test_id")

    @patch('requests.get')
    def test_download_image_success(self, mock_get, luma_node):
        """Test successful image download"""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        image_bytes = io.BytesIO()
        test_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        mock_response = Mock()
        mock_response.content = image_bytes.getvalue()
        mock_get.return_value = mock_response

        result = luma_node.client.download_image("https://example.com/image.jpg")

        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)
        assert result.dtype == np.float32

    @patch('requests.get')
    def test_download_image_failure(self, mock_get, luma_node):
        """Test image download failure"""
        mock_get.side_effect = requests.exceptions.RequestException("Download failed")

        with pytest.raises(RuntimeError, match="Failed to download image"):
            luma_node.client.download_image("https://example.com/image.jpg")

    @patch('custom_nodes.luma_api.luma_client.LumaAPIClient.send_generation_request')
    @patch('custom_nodes.luma_api.luma_client.LumaAPIClient.poll_for_completion')
    @patch('custom_nodes.luma_api.luma_client.LumaAPIClient.download_image')
    def test_generate_image_success(self, mock_download, mock_poll, mock_send, mock_env_with_key):
        """Test successful image generation end-to-end"""
        # Mock the API responses
        mock_send.return_value = {"id": "test_generation_id"}
        mock_poll.return_value = {
            "status": "completed",
            "images": [{"url": "https://example.com/image.jpg"}]
        }

        # Create a test image array
        test_image_array = np.random.rand(512, 512, 3).astype(np.float32)
        mock_download.return_value = test_image_array

        # Test the main function
        result = mock_env_with_key.generate_image(
            prompt="test prompt",
            negative_prompt="",
            width=1024,
            height=1024,
            num_images=1,
            guidance_scale=7.5,
            num_inference_steps=20,
            seed=-1
        )

        # Check result format
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], np.ndarray)
        assert result[0].shape == (1, 512, 512, 3)  # Batch dimension added

    def test_generate_image_empty_prompt(self, mock_env_with_key):
        """Test generation with empty prompt"""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            mock_env_with_key.generate_image(
                prompt="",
                negative_prompt="",
                width=1024,
                height=1024,
                num_images=1,
                guidance_scale=7.5,
                num_inference_steps=20,
                seed=-1
            )

    def test_generate_image_invalid_dimensions(self, mock_env_with_key):
        """Test generation with invalid dimensions"""
        with pytest.raises(ValueError, match="Invalid dimensions"):
            mock_env_with_key.generate_image(
                prompt="test prompt",
                negative_prompt="",
                width=512,  # Invalid
                height=512,  # Invalid
                num_images=1,
                guidance_scale=7.5,
                num_inference_steps=20,
                seed=-1
            )

    def test_generate_image_missing_api_key(self, mock_env_without_key):
        """Test generation without API key"""
        with pytest.raises(ValueError, match="LUMA_API_KEY environment variable is not set"):
            mock_env_without_key.generate_image(
                prompt="test prompt",
                negative_prompt="",
                width=1024,
                height=1024,
                num_images=1,
                guidance_scale=7.5,
                num_inference_steps=20,
                seed=-1
            )

    def test_node_registration(self):
        """Test that the node is properly registered"""
        from custom_nodes.luma_api import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        assert "LumaText2Img" in NODE_CLASS_MAPPINGS
        assert NODE_CLASS_MAPPINGS["LumaText2Img"] == LumaText2Img

        assert "LumaText2Img" in NODE_DISPLAY_NAME_MAPPINGS
        assert NODE_DISPLAY_NAME_MAPPINGS["LumaText2Img"] == "Luma Text to Image"


if __name__ == "__main__":
    pytest.main([__file__]) 