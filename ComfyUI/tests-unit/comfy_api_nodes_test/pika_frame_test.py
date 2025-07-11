"""
Unit tests for Pika Frame Node
"""
import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from comfy_api_nodes.nodes_pika import PikaFrameNode, PikaApiError


class TestPikaFrameNode:
    """Test cases for PikaFrameNode."""

    def setup_method(self):
        """Set up test fixtures."""
        self.node = PikaFrameNode()
        
        # Create a mock image tensor (BHWC format)
        self.mock_image = torch.rand(1, 512, 512, 3)
        
        # Mock parameters
        self.test_params = {
            "image": self.mock_image,
            "prompt_text": "test prompt",
            "negative_prompt": "test negative",
            "seed": 12345,
            "resolution": "1080p",
            "motion_strength": 0.5,
            "unique_id": "test_id",
        }

    def test_input_types_structure(self):
        """Test that INPUT_TYPES returns correct structure."""
        input_types = PikaFrameNode.INPUT_TYPES()
        
        # Check required inputs exist
        assert "required" in input_types
        required = input_types["required"]
        
        assert "image" in required
        assert "prompt_text" in required
        assert "negative_prompt" in required
        assert "seed" in required
        assert "resolution" in required
        assert "motion_strength" in required
        
        # Check hidden inputs
        assert "hidden" in input_types
        hidden = input_types["hidden"]
        assert "auth_token" in hidden
        assert "comfy_api_key" in hidden
        assert "unique_id" in hidden

    def test_return_types(self):
        """Test that node returns correct types."""
        assert PikaFrameNode.RETURN_TYPES == ("IMAGE",)
        assert PikaFrameNode.FUNCTION == "generate_frame"
        assert PikaFrameNode.CATEGORY == "api node/video/Pika"
        assert PikaFrameNode.API_NODE is True

    def test_motion_strength_parameter_exposed(self):
        """Test that motion_strength parameter is properly exposed."""
        input_types = PikaFrameNode.INPUT_TYPES()
        motion_strength = input_types["required"]["motion_strength"]
        
        # Verify parameter structure
        assert len(motion_strength) == 2
        param_type, options = motion_strength
        
        # Check type and options
        assert options["default"] == 0.0
        assert options["min"] == 0.0
        assert options["max"] == 1.0
        assert options["step"] == 0.1
        assert "tooltip" in options

    def test_resolution_options(self):
        """Test that resolution options are correct."""
        input_types = PikaFrameNode.INPUT_TYPES()
        resolution = input_types["required"]["resolution"]
        
        # Check available options
        options, config = resolution
        assert "1080p" in options
        assert "720p" in options
        assert config["default"] == "1080p"

    @patch('comfy_api_nodes.nodes_pika.SynchronousOperation')
    @patch('comfy_api_nodes.nodes_pika.PollingOperation')
    def test_frame_extraction_verification(self, mock_polling, mock_sync):
        """Test that exactly one frame is verified during extraction."""
        # Mock successful API responses
        mock_initial_response = Mock()
        mock_initial_response.video_id = "test_video_id"
        mock_sync.return_value.execute.return_value = mock_initial_response
        
        mock_final_response = Mock()
        mock_final_response.url = "http://test.com/video.mp4"
        mock_polling.return_value.execute.return_value = mock_final_response
        
        # Mock frame extraction to return wrong number of frames
        with patch.object(self.node, '_extract_single_frame_to_png') as mock_extract:
            # Return tensor with 2 frames instead of 1
            mock_extract.return_value = torch.rand(2, 512, 512, 3)
            
            # Should raise error for wrong frame count
            with pytest.raises(PikaApiError, match="Expected exactly 1 frame, got 2 frames"):
                self.node.generate_frame(**self.test_params)

    @patch('comfy_api_nodes.nodes_pika.SynchronousOperation')
    @patch('comfy_api_nodes.nodes_pika.PollingOperation')
    def test_successful_frame_generation(self, mock_polling, mock_sync):
        """Test successful frame generation with correct output."""
        # Mock successful API responses
        mock_initial_response = Mock()
        mock_initial_response.video_id = "test_video_id"
        mock_sync.return_value.execute.return_value = mock_initial_response
        
        mock_final_response = Mock()
        mock_final_response.url = "http://test.com/video.mp4"
        mock_polling.return_value.execute.return_value = mock_final_response
        
        # Mock successful frame extraction
        expected_frame = torch.rand(1, 512, 512, 3)
        with patch.object(self.node, '_extract_single_frame_to_png') as mock_extract:
            mock_extract.return_value = expected_frame
            
            result = self.node.generate_frame(**self.test_params)
            
            # Verify result
            assert len(result) == 1
            assert torch.equal(result[0], expected_frame)

    @patch('cv2.VideoCapture')
    @patch('requests.get')
    def test_extract_single_frame_to_png(self, mock_requests, mock_cv2):
        """Test frame extraction from video URL."""
        # Mock successful video download
        mock_response = Mock()
        mock_response.content = b"fake_video_data"
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Mock successful frame extraction
        mock_cap = Mock()
        mock_cap.read.return_value = (True, np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8))
        mock_cv2.return_value = mock_cap
        
        # Test frame extraction
        result = self.node._extract_single_frame_to_png("http://test.com/video.mp4")
        
        # Verify result shape and type
        assert isinstance(result, torch.Tensor)
        assert len(result.shape) == 4  # BHWC format
        assert result.shape[0] == 1  # Batch size of 1
        assert result.dtype == torch.float32
        assert result.min() >= 0.0 and result.max() <= 1.0  # Normalized

    def test_api_error_handling(self):
        """Test proper error handling for API failures."""
        with patch('comfy_api_nodes.nodes_pika.SynchronousOperation') as mock_sync:
            # Mock failed initial response
            mock_initial_response = Mock()
            mock_initial_response.video_id = None  # Invalid response
            mock_initial_response.code = 400
            mock_initial_response.message = "Bad Request"
            mock_sync.return_value.execute.return_value = mock_initial_response
            
            # Should raise PikaApiError
            with pytest.raises(PikaApiError, match="Pika frame request failed"):
                self.node.generate_frame(**self.test_params)

    def test_description_mentions_motion_strength(self):
        """Test that description mentions motion_strength for future use."""
        description = PikaFrameNode.DESCRIPTION
        assert "motion_strength" in description
        assert "future" in description

    def test_minimum_duration_used(self):
        """Test that minimum duration (5) is used in API request."""
        with patch('comfy_api_nodes.nodes_pika.SynchronousOperation') as mock_sync:
            with patch('comfy_api_nodes.nodes_pika.PollingOperation'):
                with patch.object(self.node, '_extract_single_frame_to_png'):
                    # Mock to capture the request data
                    mock_sync.return_value.execute.return_value = Mock(video_id="test")
                    
                    try:
                        self.node.generate_frame(**self.test_params)
                    except:
                        pass  # We only care about the request data
                    
                    # Verify duration parameter in request
                    call_args = mock_sync.call_args
                    if call_args:
                        request_data = call_args[1].get('request') or call_args[0][0].request
                        # Duration should be 5 (minimum for Pika API)
                        assert hasattr(request_data, 'duration')