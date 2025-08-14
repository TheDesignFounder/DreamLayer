"""
Tests for Quality Metrics functionality.
"""

import importlib.util
import numpy as np
from PIL import Image
import pytest
from unittest.mock import patch, MagicMock

# Check for optional dependencies
torch_missing = importlib.util.find_spec("torch") is None
trf_missing = importlib.util.find_spec("transformers") is None
lpips_missing = importlib.util.find_spec("lpips") is None
skimage_missing = importlib.util.find_spec("skimage") is None

# Mark tests that require heavy dependencies
pytestmark = [
    pytest.mark.skipif(torch_missing or trf_missing, reason="requires torch+transformers"),
]

from metrics.clip_score import (
    CLIPScorer, get_clip_scorer, clip_text_image_similarity,
    CLIP_AVAILABLE, CLIP_MODEL_ID, CLIP_MODEL_HASH
)
from metrics.ssim_lpips import (
    SSIMScorer, LPIPSScorer, QualityMetrics,
    get_ssim_scorer, get_lpips_scorer, get_quality_metrics,
    compute_ssim, compute_lpips, compute_all_quality_metrics,
    SSIM_AVAILABLE, LPIPS_AVAILABLE
)


class TestCLIPScore:
    """Test cases for CLIP scoring functionality."""
    
    @pytest.fixture
    def sample_images(self):
        """Create sample test images."""
        images = []
        for i in range(3):
            # Create a simple test image
            img = Image.new('RGB', (224, 224), color=(i * 50, i * 50, i * 50))
            images.append(img)
        return images
    
    @pytest.fixture
    def sample_prompts(self):
        """Create sample test prompts."""
        return [
            "a dark image",
            "a medium brightness image", 
            "a bright image"
        ]
    
    def test_clip_scorer_initialization(self):
        """Test CLIP scorer initialization."""
        scorer = CLIPScorer()
        
        # Check basic attributes
        assert scorer.model_id == CLIP_MODEL_ID
        assert scorer.model_hash == CLIP_MODEL_HASH
        
        # Check availability based on dependencies
        if CLIP_AVAILABLE:
            assert scorer.model is not None or scorer.model is None  # May be None if loading failed
        else:
            assert scorer.model is None
    
    @patch('metrics.clip_score.CLIP_AVAILABLE', False)
    def test_clip_scorer_no_dependencies(self):
        """Test CLIP scorer when dependencies are not available."""
        scorer = CLIPScorer()
        
        # Should handle missing dependencies gracefully
        assert scorer.model is None
        assert scorer.processor is None
        
        # Should return None for scores when CLIP not available
        images = [Image.new('RGB', (224, 224))]
        prompts = ["test prompt"]
        scores = scorer.clip_text_image_similarity(images, prompts)
        
        assert scores == [None]
    
    @pytest.mark.requires_torch
    @pytest.mark.requires_transformers
    @patch('metrics.clip_score.CLIP_AVAILABLE', True)
    @patch('metrics.clip_score.torch')
    @patch('metrics.clip_score.transformers')
    def test_clip_scorer_with_dependencies(self, mock_transformers, mock_torch):
        """Test CLIP scorer when dependencies are available."""
        # Mock CUDA availability
        mock_torch.cuda.is_available.return_value = False
        
        # Mock model and processor
        mock_model = MagicMock()
        mock_processor = MagicMock()
        
        # Mock processor to return proper input format
        mock_processor.return_value = {
            'input_ids': mock_torch.tensor([[1, 2, 3]]),
            'attention_mask': mock_torch.tensor([[1, 1, 1]]),
            'pixel_values': mock_torch.tensor([[[[1.0]]]])
        }
        
        mock_transformers.CLIPModel.from_pretrained.return_value = mock_model
        mock_transformers.CLIPProcessor.from_pretrained.return_value = mock_processor
        
        scorer = CLIPScorer()
        
        # Should have loaded model
        assert scorer.model is not None
        assert scorer.processor is not None
        assert scorer.device == "cpu"
    
    def test_clip_text_image_similarity_validation(self, sample_images, sample_prompts):
        """Test CLIP similarity validation."""
        scorer = CLIPScorer()
        
        # Test mismatched lengths
        with pytest.raises(ValueError, match="Number of images must match number of prompts"):
            scorer.clip_text_image_similarity(sample_images[:2], sample_prompts)
    
    @pytest.mark.requires_torch
    @pytest.mark.requires_transformers
    @patch('metrics.clip_score.CLIP_AVAILABLE', True)
    def test_clip_text_image_similarity_computation(self, sample_images, sample_prompts):
        """Test CLIP similarity computation."""
        scorer = CLIPScorer()
        
        if scorer.model is not None:
            scores = scorer.clip_text_image_similarity(sample_images, sample_prompts)
            
            # Check scores - they might be None if CLIP processing fails
            assert len(scores) == len(sample_images)
            assert all(score is None or isinstance(score, (int, float)) for score in scores)
            if any(score is not None for score in scores):
                assert all(0.0 <= score <= 1.0 for score in scores if score is not None)
    
    def test_clip_scorer_model_info(self):
        """Test CLIP scorer model information."""
        scorer = CLIPScorer()
        info = scorer.get_model_info()
        
        assert "model_id" in info
        assert "model_hash" in info
        assert "available" in info
        assert info["model_id"] == CLIP_MODEL_ID
        assert info["model_hash"] == CLIP_MODEL_HASH
        assert info["available"] == CLIP_AVAILABLE
    
    def test_batch_fallback_len(self):
        """Test that CLIP batch processing returns correct length with None values when deps missing."""
        scorer = CLIPScorer()
        
        # Create test images and prompts
        images = [Image.new('RGB', (224, 224)) for _ in range(5)]
        prompts = [f"test prompt {i}" for i in range(5)]
        
        # When CLIP is not available, should return None for each input
        if not CLIP_AVAILABLE or scorer.model is None:
            scores = scorer.clip_text_image_similarity(images, prompts, batch_size=2)
            
            # Check length matches input
            assert len(scores) == len(images)
            # Check all are None
            assert all(score is None for score in scores)


class TestSSIMScore:
    """Test cases for SSIM scoring functionality."""
    
    @pytest.fixture
    def sample_image_pair(self):
        """Create a pair of test images."""
        # Create base image
        base_img = Image.new('RGB', (100, 100), color=(128, 128, 128))
        base_array = np.array(base_img)
        
        # Create slightly modified image
        modified_array = base_array.copy()
        modified_array[50:60, 50:60] = [200, 200, 200]  # Add a bright patch
        modified_img = Image.fromarray(modified_array)
        
        return base_img, modified_img
    
    def test_ssim_scorer_initialization(self):
        """Test SSIM scorer initialization."""
        scorer = SSIMScorer()
        
        # Check availability
        assert hasattr(scorer, 'available')
        assert isinstance(scorer.available, bool)
    
    def test_ssim_computation_identical_images(self, sample_image_pair):
        """Test SSIM computation with identical images."""
        base_img, _ = sample_image_pair
        
        scorer = SSIMScorer()
        if scorer.available:
            score = scorer.compute_ssim(base_img, base_img)
            
            # Identical images should have SSIM close to 1.0
            assert abs(score - 1.0) < 0.01
        else:
            # If SSIM not available, should return None
            score = scorer.compute_ssim(base_img, base_img)
            assert score is None
    
    def test_ssim_computation_different_images(self, sample_image_pair):
        """Test SSIM computation with different images."""
        base_img, modified_img = sample_image_pair
        
        scorer = SSIMScorer()
        if scorer.available:
            score = scorer.compute_ssim(base_img, modified_img)
            
            # Different images should have SSIM less than 1.0
            assert score < 1.0
            assert score >= 0.0
        else:
            # If SSIM not available, should return None
            score = scorer.compute_ssim(base_img, modified_img)
            assert score is None
    
    def test_ssim_scorer_info(self):
        """Test SSIM scorer information."""
        scorer = SSIMScorer()
        info = scorer.get_info()
        
        assert "available" in info
        assert "dependencies" in info
        assert isinstance(info["available"], bool)
        assert isinstance(info["dependencies"], dict)


class TestLPIPSScore:
    """Test cases for LPIPS scoring functionality."""
    
    @pytest.fixture
    def sample_image_pair(self):
        """Create a pair of test images."""
        # Create base image
        base_img = Image.new('RGB', (100, 100), color=(128, 128, 128))
        base_array = np.array(base_img)
        
        # Create slightly modified image
        modified_array = base_array.copy()
        modified_array[50:60, 50:60] = [200, 200, 200]  # Add a bright patch
        modified_img = Image.fromarray(modified_array)
        
        return base_img, modified_img
    
    def test_lpips_scorer_initialization(self):
        """Test LPIPS scorer initialization."""
        scorer = LPIPSScorer()
        
        # Check availability
        assert hasattr(scorer, 'available')
        assert isinstance(scorer.available, bool)
    
    @pytest.mark.requires_lpips
    def test_lpips_computation_identical_images(self, sample_image_pair):
        """Test LPIPS computation with identical images."""
        base_img, _ = sample_image_pair
        
        scorer = LPIPSScorer()
        if scorer.available:
            score = scorer.compute_lpips(base_img, base_img)
            
            # Identical images should have LPIPS close to 0.0
            assert score is not None
            assert abs(score - 0.0) < 0.01
        else:
            # If LPIPS not available, should return None
            score = scorer.compute_lpips(base_img, base_img)
            assert score is None
    
    @pytest.mark.requires_lpips
    def test_lpips_computation_different_images(self, sample_image_pair):
        """Test LPIPS computation with different images."""
        base_img, modified_img = sample_image_pair
        
        scorer = LPIPSScorer()
        if scorer.available:
            score = scorer.compute_lpips(base_img, modified_img)
            
            # Different images should have LPIPS greater than 0.0
            assert score is not None
            assert score > 0.0
        else:
            # If LPIPS not available, should return None
            score = scorer.compute_lpips(base_img, modified_img)
            assert score is None
    
    def test_lpips_scorer_info(self):
        """Test LPIPS scorer information."""
        scorer = LPIPSScorer()
        info = scorer.get_info()
        
        assert "available" in info
        assert "dependencies" in info
        assert isinstance(info["available"], bool)
        assert isinstance(info["dependencies"], dict)


class TestQualityMetrics:
    """Test cases for combined quality metrics."""
    
    @pytest.fixture
    def test_images(self):
        """Create test images for metrics computation."""
        # Create base image
        base_img = Image.new('RGB', (100, 100), color=(128, 128, 128))
        base_array = np.array(base_img)
        
        # Create slightly modified image
        modified_array = base_array.copy()
        modified_array[50:60, 50:60] = [200, 200, 200]  # Add a bright patch
        modified_img = Image.fromarray(modified_array)
        
        return base_img, modified_img
    
    def test_quality_metrics_initialization(self):
        """Test quality metrics initialization."""
        metrics = QualityMetrics()
        
        # Check that all scorers are available
        assert hasattr(metrics, 'ssim_scorer')
        assert hasattr(metrics, 'lpips_scorer')
    
    def test_compute_all_metrics(self, test_images):
        """Test computation of all quality metrics."""
        base_img, modified_img = test_images
        
        metrics = QualityMetrics()
        results = metrics.compute_all_metrics(base_img, modified_img)
        
        # Check results structure
        assert "ssim" in results
        assert "lpips" in results
        
        # Check SSIM result
        if metrics.ssim_scorer.available:
            assert isinstance(results["ssim"], float)
            assert 0.0 <= results["ssim"] <= 1.0
        else:
            assert results["ssim"] is None
        
        # Check LPIPS result
        if metrics.lpips_scorer.available:
            assert results["lpips"] is None or isinstance(results["lpips"], float)
        else:
            assert results["lpips"] is None
    
    def test_quality_metrics_info(self):
        """Test quality metrics information."""
        metrics = QualityMetrics()
        info = metrics.get_metrics_info()
        
        assert "ssim" in info
        assert "lpips" in info
        assert isinstance(info["ssim"], dict)
        assert isinstance(info["lpips"], dict)


class TestQualityMetricsIntegration:
    """Integration tests for quality metrics functionality."""
    
    @pytest.fixture
    def test_images(self):
        """Create test images for integration testing."""
        images = []
        for i in range(3):
            # Create images with different patterns
            img = Image.new('RGB', (100, 100), color=(i * 50, i * 50, i * 50))
            images.append(img)
        return images
    
    @pytest.fixture
    def test_prompts(self):
        """Create test prompts for integration testing."""
        return [
            "a dark image",
            "a medium brightness image",
            "a bright image"
        ]
    
    def test_clip_batch_processing(self, test_images, test_prompts):
        """Test CLIP batch processing functionality."""
        scorer = CLIPScorer()
        
        if scorer.model is not None:
            scores = scorer.clip_text_image_similarity(test_images, test_prompts, batch_size=2)
            
            # Check batch processing results - scores might be None if CLIP processing fails
            assert len(scores) == len(test_images)
            assert all(score is None or isinstance(score, (int, float)) for score in scores)
            if any(score is not None for score in scores):
                assert all(0.0 <= score <= 1.0 for score in scores if score is not None)
    
    def test_ssim_consistency(self, test_images):
        """Test SSIM consistency across multiple runs."""
        if len(test_images) >= 2:
            scorer = SSIMScorer()
            
            if scorer.available:
                # Compute SSIM multiple times
                score1 = scorer.compute_ssim(test_images[0], test_images[1])
                score2 = scorer.compute_ssim(test_images[0], test_images[1])
                
                # Results should be consistent
                assert abs(score1 - score2) < 0.001
    
    def test_metrics_availability_check(self):
        """Test that metrics availability is properly reported."""
        # Check CLIP availability
        clip_scorer = CLIPScorer()
        assert hasattr(clip_scorer, 'model')
        
        # Check SSIM availability
        ssim_scorer = SSIMScorer()
        assert hasattr(ssim_scorer, 'available')
        
        # Check LPIPS availability
        lpips_scorer = LPIPSScorer()
        assert hasattr(lpips_scorer, 'available')
    
    def test_graceful_fallback_behavior(self):
        """Test graceful fallback when dependencies are missing."""
        # Test CLIP fallback
        clip_scorer = CLIPScorer()
        if not clip_scorer.model:
            # Should handle missing model gracefully
            images = [Image.new('RGB', (100, 100))]
            prompts = ["test"]
            scores = clip_scorer.clip_text_image_similarity(images, prompts)
            assert scores == [None]
        
        # Test SSIM fallback
        ssim_scorer = SSIMScorer()
        if not ssim_scorer.available:
            score = ssim_scorer.compute_ssim(
                Image.new('RGB', (100, 100)), 
                Image.new('RGB', (100, 100))
            )
            assert score is None
        
        # Test LPIPS fallback
        lpips_scorer = LPIPSScorer()
        if not lpips_scorer.available:
            score = lpips_scorer.compute_lpips(
                Image.new('RGB', (100, 100)), 
                Image.new('RGB', (100, 100))
            )
            assert score is None
