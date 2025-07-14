"""
Test file for recraft_text2img node as required by DreamLayer Challenge Task #3

This test file ensures that the Recraft text-to-image node properly handles:
- HTTP request mocking and response parsing  
- API key validation and error handling
- Integration with CLIPTextEncode workflow
- Timeout configuration
"""

import pytest
import os
import torch
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image
import json


class TestRecraftTextToImageDirectNode:
    """Test suite for RecraftTextToImageDirectNode as required by challenge"""

    def setup_method(self):
        """Setup test fixtures"""
        # Import here to avoid issues during test discovery
        from comfy_api_nodes.nodes_recraft import RecraftTextToImageDirectNode
        self.node = RecraftTextToImageDirectNode()
        
        self.mock_response = {
            "data": [
                {"url": "https://example.com/generated_image.png", "image_id": "test_id_1"}
            ],
            "created": 1234567890,
            "credits": 1
        }
        
        # Create a mock image tensor
        self.mock_image_tensor = torch.rand(1, 512, 512, 3)

    def test_node_structure(self):
        """Test that node has required attributes for ComfyUI integration"""
        assert hasattr(self.node, 'CATEGORY')
        assert hasattr(self.node, 'FUNCTION') 
        assert hasattr(self.node, 'RETURN_TYPES')
        assert hasattr(self.node, 'API_NODE')
        assert hasattr(self.node, 'INPUT_TYPES')
        
        assert self.node.CATEGORY == "api node/image/Recraft"
        assert self.node.FUNCTION == "api_call"
        assert self.node.API_NODE == True

    def test_missing_api_key_error(self):
        """Test that missing API key surfaces helpful message without crashing"""
        # Ensure no API key is set
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                self.node.api_call(
                    prompt="test prompt",
                    size="1024x1024", 
                    n=1,
                    seed=0
                )
            
            error_message = str(exc_info.value)
            assert "RECRAFT_API_KEY is required but not found" in error_message
            assert "Please set the RECRAFT_API_KEY environment variable" in error_message

    @patch('comfy_api_nodes.nodes_recraft.SynchronousOperation')
    @patch('comfy_api_nodes.nodes_recraft.download_url_to_bytesio')
    @patch('comfy_api_nodes.nodes_recraft.bytesio_to_image_tensor')
    def test_successful_api_call_with_mocking(self, mock_tensor_convert, mock_download, mock_operation):
        """Test successful API call with HTTP mocking as required by challenge"""
        # Setup mocks
        mock_op_instance = MagicMock()
        mock_op_instance.execute.return_value = self.mock_response
        mock_operation.return_value = mock_op_instance
        
        mock_download.return_value = BytesIO(b"fake image data")
        mock_tensor_convert.return_value = self.mock_image_tensor
        
        # Test with mocked API key
        with patch.dict(os.environ, {'RECRAFT_API_KEY': 'test_key'}):
            result = self.node.api_call(
                prompt="test prompt",
                size="1024x1024",
                n=1, 
                seed=42
            )
        
        # Verify result
        assert len(result) == 1
        assert torch.is_tensor(result[0])
        
        # Verify API call was made correctly
        mock_operation.assert_called_once()
        call_args = mock_operation.call_args
        
        # Verify endpoint configuration
        endpoint = call_args[1]['endpoint']
        assert endpoint.path == "/v1/images/generations"
        assert str(endpoint.method) == "HttpMethod.POST"
        
        # Verify request data
        request_data = call_args[1]['request'] 
        assert request_data['prompt'] == "test prompt"
        assert request_data['size'] == "1024x1024"
        assert request_data['n'] == 1
        assert request_data['model'] == "recraftv3"
        assert request_data['random_seed'] == 42
        
        # Verify API base and auth
        assert call_args[1]['api_base'] == "https://external.api.recraft.ai"
        assert call_args[1]['auth_token'] == 'test_key'

    @patch('comfy_api_nodes.nodes_recraft.SynchronousOperation')
    def test_timeout_configuration(self, mock_operation):
        """Test that timeout can be configured as required by challenge"""
        mock_op_instance = MagicMock()
        mock_operation.return_value = mock_op_instance
        
        with patch.dict(os.environ, {'RECRAFT_API_KEY': 'test_key'}):
            try:
                self.node.api_call(
                    prompt="test prompt",
                    size="1024x1024",
                    n=1,
                    seed=0
                )
            except:
                pass  # We only care about the timeout parameter
        
        # Verify timeout is configurable (default 30.0 seconds)
        call_args = mock_operation.call_args
        assert call_args[1]['timeout'] == 30.0

    def test_cliptextencode_integration(self):
        """Test that node can integrate with CLIPTextEncode block"""
        input_types = self.node.INPUT_TYPES()
        
        # Verify prompt input accepts STRING type (compatible with CLIPTextEncode)
        assert "prompt" in input_types["required"]
        prompt_config = input_types["required"]["prompt"]
        assert prompt_config[0] == "STRING"  # IO.STRING
        assert prompt_config[1]["multiline"] == True

    @patch('comfy_api_nodes.nodes_recraft.SynchronousOperation')
    def test_multiple_images_generation(self, mock_operation):
        """Test generating multiple images"""
        multi_response = {
            "data": [
                {"url": "https://example.com/image1.png"},
                {"url": "https://example.com/image2.png"}
            ]
        }
        
        mock_op_instance = MagicMock()
        mock_op_instance.execute.return_value = multi_response
        mock_operation.return_value = mock_op_instance
        
        with patch.dict(os.environ, {'RECRAFT_API_KEY': 'test_key'}):
            with patch('comfy_api_nodes.nodes_recraft.download_url_to_bytesio'):
                with patch('comfy_api_nodes.nodes_recraft.bytesio_to_image_tensor') as mock_tensor:
                    mock_tensor.return_value = self.mock_image_tensor
                    
                    result = self.node.api_call(
                        prompt="test prompt",
                        size="1024x1024", 
                        n=2,
                        seed=0
                    )
        
        # Should handle multiple images
        assert len(result) == 1  # Returns single batched tensor
        
        # Verify request asked for 2 images
        call_args = mock_operation.call_args
        assert call_args[1]['request']['n'] == 2

    def test_docstring_completeness(self):
        """Test that inline docstring documents all requirements"""
        docstring = self.node.__doc__
        
        # Check required documentation elements as per challenge
        assert "https://external.api.recraft.ai/v1/images/generations" in docstring
        assert "RECRAFT_API_KEY" in docstring
        assert "Environment Variables" in docstring
        assert "timeout" in docstring.lower()
        assert "30 seconds" in docstring
        assert "CLIPTextEncode" in docstring
        
        # Check parameter documentation
        assert "prompt:" in docstring
        assert "size:" in docstring
        assert "n:" in docstring
        assert "seed:" in docstring 
