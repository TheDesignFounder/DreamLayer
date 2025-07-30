"""Tests for Runway Text-to-Image Node

This test file validates the runway_text2img node implementation
with mocked HTTP calls as specified in the requirements.
"""

import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Optional

# Mock the ComfyUI modules that might not be available during testing
@pytest.fixture(autouse=True)
def mock_comfy_modules():
    with patch.dict('sys.modules', {
        'comfy': MagicMock(),
        'comfy.utils': MagicMock(),
        'comfy.cli_args': MagicMock(),
        'comfy.comfy_types': MagicMock(),
        'comfy.comfy_types.node_typing': MagicMock(),
        'server': MagicMock(),
        'comfy_api': MagicMock(),
        'comfy_api.input_impl': MagicMock(),
        'comfy_api.util': MagicMock(),
        'comfy_api.input.video_types': MagicMock(),
        'comfy_api.input.basic_types': MagicMock(),
        'comfy_api_nodes': MagicMock(),
        'comfy_api_nodes.apis': MagicMock(),
        'comfy_api_nodes.apis.client': MagicMock(),
        'comfy_api_nodes.apinode_utils': MagicMock(),
        'comfy_api_nodes.mapper_utils': MagicMock(),
    }):
        # Also create mock args
        mock_args = MagicMock()
        import sys
        sys.modules['comfy.cli_args'].args = mock_args
        yield


class TestRunwayText2ImgNode:
    """Test cases for the runway_text2img node"""

    @pytest.fixture
    def node_class(self):
        """Import and return the runway_text2img node class"""
        from comfy_api_nodes.nodes_runway import runway_text2img
        return runway_text2img

    @pytest.fixture
    def mock_env_with_api_key(self):
        """Mock environment with RUNWAY_API_KEY present"""
        with patch.dict(os.environ, {'RUNWAY_API_KEY': 'test_api_key_123'}):
            yield

    @pytest.fixture
    def mock_env_without_api_key(self):
        """Mock environment with RUNWAY_API_KEY absent"""
        with patch.dict(os.environ, {}, clear=True):
            yield

    @pytest.fixture
    def sample_prompt(self):
        """Sample text prompt for testing"""
        return "A beautiful landscape with mountains and lakes"

    @pytest.fixture
    def mock_image_tensor(self):
        """Mock image tensor for testing"""
        return torch.rand(1, 512, 512, 3)

    @pytest.fixture
    def mock_successful_response(self):
        """Mock successful API response"""
        return {
            'id': 'task_123',
            'status': 'PENDING'
        }

    @pytest.fixture
    def mock_completed_task(self):
        """Mock completed task response"""
        return {
            'id': 'task_123',
            'status': 'SUCCEEDED',
            'output': ['https://example.com/generated_image.png']
        }

    def test_node_has_correct_attributes(self, node_class):
        """Test that the node has required attributes"""
        assert hasattr(node_class, 'INPUT_TYPES')
        assert hasattr(node_class, 'RETURN_TYPES')
        assert hasattr(node_class, 'FUNCTION')
        assert hasattr(node_class, 'CATEGORY')
        assert node_class.RETURN_TYPES == ("IMAGE",)
        assert node_class.FUNCTION == "generate_image"

    def test_input_types_structure(self, node_class):
        """Test that INPUT_TYPES has correct structure"""
        input_types = node_class.INPUT_TYPES()

        # Check required inputs
        assert "required" in input_types
        assert "prompt" in input_types["required"]

        # Check optional inputs
        if "optional" in input_types:
            pass  # Optional inputs are allowed

        # Check hidden inputs for API key
        assert "hidden" in input_types

    def test_missing_api_key_raises_clear_error(self, node_class, mock_env_without_api_key, sample_prompt):
        """Test that missing RUNWAY_API_KEY raises a clear, non-crashing error"""
        node = node_class()

        with pytest.raises(EnvironmentError) as exc_info:
            node.generate_image(prompt=sample_prompt)

        # Verify error message is clear and mentions the environment variable
        error_msg = str(exc_info.value).lower()
        assert "runway_api_key" in error_msg
        assert "environment" in error_msg or "env" in error_msg

    @patch('requests.post')
    @patch('requests.get')
    def test_successful_generation_flow(self, mock_get, mock_post, node_class,
                                      mock_env_with_api_key, sample_prompt,
                                      mock_successful_response, mock_completed_task):
        """Test successful image generation flow with mocked HTTP calls"""
        # Mock initial POST request
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_successful_response

        # Mock polling GET request
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_completed_task

        # Mock image download
        with patch('comfy_api_nodes.apinode_utils.download_url_to_image_tensor') as mock_download:
            mock_download.return_value = torch.rand(1, 512, 512, 3)

            node = node_class()
            result = node.generate_image(prompt=sample_prompt)

            # Verify result is a tuple with image tensor
            assert isinstance(result, tuple)
            assert len(result) == 1
            assert isinstance(result[0], torch.Tensor)

            # Verify API calls were made correctly
            mock_post.assert_called_once()
            post_call_args = mock_post.call_args

            # Check URL
            assert "api.dev.runwayml.com/v1/text_to_image" in post_call_args[0][0]

            # Check headers contain API key
            headers = post_call_args[1]['headers']
            assert 'Authorization' in headers
            assert 'test_api_key_123' in headers['Authorization']

            # Check request payload
            payload = post_call_args[1]['json']
            assert 'promptText' in payload
            assert payload['promptText'] == sample_prompt

    @patch('requests.post')
    def test_api_error_handling(self, mock_post, node_class, mock_env_with_api_key, sample_prompt):
        """Test proper handling of API errors"""
        # Mock API failure
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {'error': 'Bad request'}

        node = node_class()

        with pytest.raises(Exception) as exc_info:
            node.generate_image(prompt=sample_prompt)

        # Verify error is properly handled and informative
        assert "400" in str(exc_info.value) or "Bad request" in str(exc_info.value)

    @patch('requests.post')
    @patch('requests.get')
    def test_polling_timeout_handling(self, mock_get, mock_post, node_class,
                                    mock_env_with_api_key, sample_prompt, mock_successful_response):
        """Test handling of polling timeout scenarios"""
        # Mock initial successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_successful_response

        # Mock polling that never completes (always returns PENDING)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'id': 'task_123', 'status': 'PENDING'}

        node = node_class()

        # This should eventually timeout or handle the infinite polling case
        with patch('time.sleep'):  # Speed up the test
            with pytest.raises((TimeoutError, Exception)):
                node.generate_image(prompt=sample_prompt, timeout=1)  # Short timeout for testing

    def test_docstring_completeness(self, node_class):
        """Test that the node has comprehensive documentation"""
        # Check class docstring
        assert node_class.__doc__ is not None
        docstring = node_class.__doc__.lower()

        # Should document the RUNWAY_API_KEY requirement
        assert "runway_api_key" in docstring or "api key" in docstring

        # Should mention timeout configuration
        assert "timeout" in docstring

        # Should document parameters
        assert "parameter" in docstring or "param" in docstring

    def test_node_registration(self):
        """Test that the node is properly registered in NODE_CLASS_MAPPINGS"""
        from comfy_api_nodes.nodes_runway import NODE_CLASS_MAPPINGS

        # Check that runway_text2img is in the mappings
        assert "runway_text2img" in NODE_CLASS_MAPPINGS

        # Verify it points to the correct class
        node_class = NODE_CLASS_MAPPINGS["runway_text2img"]
        assert hasattr(node_class, 'generate_image')

    def test_prompt_validation(self, node_class, mock_env_with_api_key):
        """Test validation of prompt input"""
        node = node_class()

        # Empty prompt should raise validation error
        with pytest.raises(ValueError):
            node.generate_image(prompt="")

        # None prompt should raise validation error
        with pytest.raises((ValueError, TypeError)):
            node.generate_image(prompt=None)

    @patch('requests.post')
    @patch('requests.get')
    def test_reference_image_handling(self, mock_get, mock_post, node_class,
                                    mock_env_with_api_key, sample_prompt, mock_image_tensor,
                                    mock_successful_response, mock_completed_task):
        """Test handling of optional reference images"""
        # Mock successful responses
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_successful_response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_completed_task

        with patch('comfy_api_nodes.apinode_utils.download_url_to_image_tensor') as mock_download:
            with patch('comfy_api_nodes.apinode_utils.upload_images_to_comfyapi') as mock_upload:
                mock_download.return_value = torch.rand(1, 512, 512, 3)
                mock_upload.return_value = ['https://example.com/ref_image.png']

                node = node_class()
                result = node.generate_image(prompt=sample_prompt, reference_image=mock_image_tensor)

                # Verify reference image was uploaded
                mock_upload.assert_called_once()

                # Verify API call includes reference image
                post_call_args = mock_post.call_args
                payload = post_call_args[1]['json']
                assert 'referenceImages' in payload or 'reference_images' in payload


class TestIntegrationWithComfyUI:
    """Test integration aspects with ComfyUI workflow system"""

    def test_works_after_clip_text_encode(self):
        """Test that the node can work after CLIPTextEncode in a workflow graph"""
        # This is more of a design verification test
        # In a real ComfyUI workflow, this would be tested with actual workflow execution
        from comfy_api_nodes.nodes_runway import runway_text2img

        # Verify the node accepts string input (which CLIPTextEncode would output)
        input_types = runway_text2img.INPUT_TYPES()
        assert "prompt" in input_types["required"]

        # Verify it returns IMAGE type that downstream nodes can use
        assert runway_text2img.RETURN_TYPES == ("IMAGE",)

    def test_comfyui_tensor_format(self, mock_env_with_api_key):
        """Test that returned images are in proper ComfyUI tensor format"""
        # ComfyUI expects images as [batch, height, width, channels] tensors
        from comfy_api_nodes.nodes_runway import runway_text2img

        with patch('requests.post') as mock_post:
            with patch('requests.get') as mock_get:
                with patch('comfy_api_nodes.apinode_utils.download_url_to_image_tensor') as mock_download:
                    # Mock a properly formatted ComfyUI image tensor
                    mock_tensor = torch.rand(1, 512, 512, 3)  # [batch, height, width, channels]
                    mock_download.return_value = mock_tensor

                    mock_post.return_value.status_code = 200
                    mock_post.return_value.json.return_value = {'id': 'task_123'}

                    mock_get.return_value.status_code = 200
                    mock_get.return_value.json.return_value = {
                        'id': 'task_123',
                        'status': 'SUCCEEDED',
                        'output': ['https://example.com/image.png']
                    }

                    node = runway_text2img()
                    result = node.generate_image(prompt="test prompt")

                    # Verify tensor format
                    assert isinstance(result[0], torch.Tensor)
                    assert len(result[0].shape) == 4  # [batch, height, width, channels]
                    assert result[0].shape[0] >= 1    # At least 1 image in batch
                    assert result[0].shape[3] == 3    # RGB channels