"""
Tests for Runway Text-to-Image Node

This test suite validates the RunwayText2ImgNode implementation including:
- Environment variable handling
- Input validation
- API request formatting
- Response parsing
- Error handling
- Image tensor conversion
"""

import os
import pytest
import torch
import numpy as np
from unittest.mock import patch, Mock, MagicMock
from io import BytesIO
from PIL import Image
import httpx

# Import the node to test
from dream_layer_backend.comfy_nodes.api_nodes.runway_text2img import RunwayText2ImgNode


class TestRunwayText2ImgNode:
    """Test suite for RunwayText2ImgNode."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.node = RunwayText2ImgNode()
        
        # Create a sample image for testing
        self.sample_image = Image.new("RGB", (512, 512), color="red")
        self.sample_image_bytes = BytesIO()
        self.sample_image.save(self.sample_image_bytes, format="PNG")
        self.sample_image_bytes = self.sample_image_bytes.getvalue()
    
    def test_input_types_structure(self):
        """Test that INPUT_TYPES returns the correct structure."""
        input_types = RunwayText2ImgNode.INPUT_TYPES()
        
        assert "required" in input_types
        assert "optional" in input_types
        
        required = input_types["required"]
        optional = input_types["optional"]
        
        # Check all required inputs are present
        assert "promptText" in required
        assert "ratio" in required
        assert "timeout" in required
        
        # Check optional inputs
        assert "seed" in optional
        
        # Check input types
        assert required["promptText"][0] == "STRING"
        assert required["timeout"][0] == "INT"
        assert optional["seed"][0] == "INT"
        
        # Check default values
        assert required["ratio"][1]["default"] == "1024:1024"
        assert required["timeout"][1]["default"] == 120
        assert optional["seed"][1]["default"] == -1
    
    def test_node_metadata(self):
        """Test that node metadata is correctly set."""
        assert hasattr(RunwayText2ImgNode, "DESCRIPTION")
        assert hasattr(RunwayText2ImgNode, "CATEGORY")
        assert hasattr(RunwayText2ImgNode, "RETURN_TYPES")
        assert hasattr(RunwayText2ImgNode, "RETURN_NAMES")
        assert hasattr(RunwayText2ImgNode, "FUNCTION")
        
        assert RunwayText2ImgNode.CATEGORY == "api node/image/runway"
        assert RunwayText2ImgNode.RETURN_TYPES == ("IMAGE",)
        assert RunwayText2ImgNode.RETURN_NAMES == ("image",)
        assert RunwayText2ImgNode.FUNCTION == "generate_image"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises_error(self):
        """Test that missing RUNWAY_API_KEY raises RuntimeError."""
        with pytest.raises(RuntimeError, match="RUNWAY_API_KEY not set"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    def test_empty_prompt_raises_error(self):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="promptText cannot be empty"):
            self.node.generate_image("")
        
        with pytest.raises(ValueError, match="promptText cannot be empty"):
            self.node.generate_image("   ")  # whitespace only
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    def test_invalid_ratio_raises_error(self):
        """Test that invalid ratio values raise ValueError."""
        # Invalid ratio format
        with pytest.raises(ValueError, match="Ratio must be one of"):
            self.node.generate_image("test", ratio="invalid:ratio")
        
        # Ratio not in supported list
        with pytest.raises(ValueError, match="Ratio must be one of"):
            self.node.generate_image("test", ratio="999:999")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    def test_invalid_timeout_raises_error(self):
        """Test that invalid timeout values raise ValueError."""
        with pytest.raises(ValueError, match="Timeout must be at least 30 seconds"):
            self.node.generate_image("test", timeout=10)
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_successful_generation(self, mock_client):
        """Test successful image generation workflow with task polling."""
        # Mock HTTP client
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation response
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        
        # Mock task status response (completed)
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {
            "status": "SUCCEEDED",
            "output": ["https://example.com/generated-image.png"]
        }
        
        # Mock image download
        mock_image_response = Mock()
        mock_image_response.raise_for_status.return_value = None
        mock_image_response.content = self.sample_image_bytes
        
        # Set up the call sequence: POST (create), GET (status), GET (image)
        mock_context.post.return_value = mock_create_response
        mock_context.get.side_effect = [mock_status_response, mock_image_response]
        
        # Execute
        result = self.node.generate_image(
            promptText="A beautiful landscape",
            ratio="1024:1024",
            timeout=120
        )
        
        # Verify result
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], torch.Tensor)
        
        # Check tensor shape: [batch, height, width, channels]
        tensor = result[0]
        assert tensor.dim() == 4
        assert tensor.shape[0] == 1  # batch size
        assert tensor.shape[3] == 3  # RGB channels
        
        # Verify task creation call
        mock_context.post.assert_called_once()
        create_call_args = mock_context.post.call_args
        
        # Check URL
        assert create_call_args[0][0] == "https://api.dev.runwayml.com/v1/text_to_image"
        
        # Check headers
        headers = create_call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer sk-test-key"
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Runway-Version"] == "2024-11-06"
        
        # Check payload
        payload = create_call_args[1]["json"]
        assert payload["model"] == "gen4_image"
        assert payload["promptText"] == "A beautiful landscape"
        assert payload["ratio"] == "1024:1024"
        assert "seed" not in payload  # Should not be included when -1
        
        # Verify polling and image download calls
        assert mock_context.get.call_count == 2
        get_calls = mock_context.get.call_args_list
        
        # First call should be task status
        assert get_calls[0][0][0] == "https://api.dev.runwayml.com/v1/tasks/task-123"
        
        # Second call should be image download
        assert get_calls[1][0][0] == "https://example.com/generated-image.png"
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_timeout_error_handling(self, mock_client):
        """Test timeout error handling."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        mock_context.post.side_effect = httpx.TimeoutException("Timeout")
        
        with pytest.raises(RuntimeError, match="Request timed out"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    @patch("time.time")
    @patch("time.sleep")
    def test_task_polling_timeout(self, mock_sleep, mock_time, mock_client):
        """Test task polling timeout handling."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        mock_context.post.return_value = mock_create_response
        
        # Mock time progression to simulate timeout
        mock_time.side_effect = [0, 150]  # Start at 0, then 150 seconds later (past 120s timeout)
        
        # Mock status as always PENDING
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {"status": "PENDING"}
        mock_context.get.return_value = mock_status_response
        
        with pytest.raises(RuntimeError, match="Task did not complete within 120 seconds"):
            self.node.generate_image("test prompt", timeout=120)
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_http_error_handling(self, mock_client):
        """Test HTTP error handling."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Test 401 Unauthorized
        mock_response = Mock()
        mock_response.status_code = 401
        mock_context.post.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=mock_response
        )
        
        with pytest.raises(RuntimeError, match="Invalid RUNWAY_API_KEY"):
            self.node.generate_image("test prompt")
        
        # Test 429 Rate Limit
        mock_response.status_code = 429
        mock_context.post.side_effect = httpx.HTTPStatusError(
            "Rate Limited", request=Mock(), response=mock_response
        )
        
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            self.node.generate_image("test prompt")
        
        # Test other HTTP errors
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_context.post.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        
        with pytest.raises(RuntimeError, match="Runway API error 500"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_no_task_id_in_response(self, mock_client):
        """Test handling of response with no task ID."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"error": "something went wrong"}
        mock_context.post.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="No task ID returned from Runway API"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_task_failure_handling(self, mock_client):
        """Test handling of task failure status."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        mock_context.post.return_value = mock_create_response
        
        # Mock task status response (failed)
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {
            "status": "FAILED",
            "failure": {"reason": "Content moderation failure"}
        }
        mock_context.get.return_value = mock_status_response
        
        with pytest.raises(RuntimeError, match="Task failed: Content moderation failure"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_task_succeeded_no_output(self, mock_client):
        """Test handling of successful task with no output."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        mock_context.post.return_value = mock_create_response
        
        # Mock task status response (succeeded but no output)
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {
            "status": "SUCCEEDED",
            "output": []
        }
        mock_context.get.return_value = mock_status_response
        
        with pytest.raises(RuntimeError, match="Task succeeded but no output found"):
            self.node.generate_image("test prompt")
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_image_conversion_from_different_modes(self, mock_client):
        """Test image conversion from different PIL modes."""
        # Create RGBA image
        rgba_image = Image.new("RGBA", (512, 512), color=(255, 0, 0, 128))
        rgba_bytes = BytesIO()
        rgba_image.save(rgba_bytes, format="PNG")
        rgba_bytes = rgba_bytes.getvalue()
        
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        
        # Mock task status (completed)
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {
            "status": "SUCCEEDED",
            "output": ["https://example.com/generated-image.png"]
        }
        
        # Mock image download with RGBA image
        mock_image_response = Mock()
        mock_image_response.raise_for_status.return_value = None
        mock_image_response.content = rgba_bytes
        
        # Set up call sequence
        mock_context.post.return_value = mock_create_response
        mock_context.get.side_effect = [mock_status_response, mock_image_response]
        
        # Execute
        result = self.node.generate_image("test prompt")
        
        # Verify result is still RGB
        tensor = result[0]
        assert tensor.shape[3] == 3  # Should be converted to RGB
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_custom_parameters(self, mock_client):
        """Test that custom parameters are correctly passed to API."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        
        # Mock task creation
        mock_create_response = Mock()
        mock_create_response.raise_for_status.return_value = None
        mock_create_response.json.return_value = {"id": "task-123"}
        
        # Mock task status (completed)
        mock_status_response = Mock()
        mock_status_response.raise_for_status.return_value = None
        mock_status_response.json.return_value = {
            "status": "SUCCEEDED",
            "output": ["https://example.com/generated-image.png"]
        }
        
        # Mock image download
        mock_image_response = Mock()
        mock_image_response.raise_for_status.return_value = None
        mock_image_response.content = self.sample_image_bytes
        
        # Set up call sequence
        mock_context.post.return_value = mock_create_response
        mock_context.get.side_effect = [mock_status_response, mock_image_response]
        
        # Execute with custom parameters
        self.node.generate_image(
            promptText="Custom prompt",
            ratio="1920:1080",
            seed=12345,
            timeout=180
        )
        
        # Verify custom parameters in API call
        payload = mock_context.post.call_args[1]["json"]
        assert payload["model"] == "gen4_image"
        assert payload["promptText"] == "Custom prompt"
        assert payload["ratio"] == "1920:1080"
        assert payload["seed"] == 12345
    
    def test_node_class_export(self):
        """Test that the node class is properly exported."""
        from dream_layer_backend.comfy_nodes.api_nodes.runway_text2img import __all__
        assert "RunwayText2ImgNode" in __all__
    
    @patch.dict(os.environ, {"RUNWAY_API_KEY": "sk-test-key"})
    @patch("httpx.Client")
    def test_general_exception_handling(self, mock_client):
        """Test handling of general exceptions."""
        mock_context = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_context
        mock_context.post.side_effect = Exception("Network error")
        
        with pytest.raises(RuntimeError, match="Failed to generate image: Network error"):
            self.node.generate_image("test prompt")


if __name__ == "__main__":
    pytest.main([__file__]) 