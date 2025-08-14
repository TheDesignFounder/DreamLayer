"""
Tests for Tiling and Blending functionality.
"""

import numpy as np
from PIL import Image
import pytest
from unittest.mock import MagicMock, patch

from core.tiling import (
    TilingConfig, tile_slices, create_blend_mask, blend_paste,
    process_tiled, calculate_optimal_tile_size, validate_tiling_config
)


class TestTilingConfig:
    """Test cases for TilingConfig class."""
    
    def test_valid_config(self):
        """Test valid tiling configuration."""
        config = TilingConfig(tile_size=512, overlap=64, blend_mode="cosine")
        assert config.tile_size == 512
        assert config.overlap == 64
        assert config.blend_mode == "cosine"
    
    def test_invalid_tile_size(self):
        """Test invalid tile size."""
        with pytest.raises(ValueError, match="Tile size must be positive"):
            TilingConfig(tile_size=0, overlap=64, blend_mode="cosine")
        
        with pytest.raises(ValueError, match="Tile size must be positive"):
            TilingConfig(tile_size=-1, overlap=64, blend_mode="cosine")
    
    def test_invalid_overlap(self):
        """Test invalid overlap values."""
        with pytest.raises(ValueError, match="Overlap must be non-negative"):
            TilingConfig(tile_size=512, overlap=-1, blend_mode="cosine")
        
        with pytest.raises(ValueError, match="Overlap must be less than tile size"):
            TilingConfig(tile_size=512, overlap=512, blend_mode="cosine")
    
    def test_invalid_blend_mode(self):
        """Test invalid blend mode."""
        with pytest.raises(ValueError, match="Blend mode must be"):
            TilingConfig(tile_size=512, overlap=64, blend_mode="invalid")
    
    def test_to_dict(self):
        """Test config to dictionary conversion."""
        config = TilingConfig(tile_size=512, overlap=64, blend_mode="cosine")
        config_dict = config.to_dict()
        
        assert config_dict["tile_size"] == 512
        assert config_dict["overlap"] == 64
        assert config_dict["blend_mode"] == "cosine"


class TestTileSlices:
    """Test cases for tile_slices function."""
    
    def test_simple_tiling(self):
        """Test simple tiling without overlap."""
        tiles = tile_slices(1024, 1024, 512, 0)
        
        # Should create 4 tiles
        assert len(tiles) == 4
        
        # Check tile coordinates
        expected_tiles = [
            (0, 0, 512, 512),
            (512, 0, 1024, 512),
            (0, 512, 512, 1024),
            (512, 512, 1024, 1024)
        ]
        
        for tile in tiles:
            assert tile in expected_tiles
    
    def test_tiling_with_overlap(self):
        """Test tiling with overlap."""
        tiles = tile_slices(1024, 1024, 512, 64)
        
        # Should create more tiles due to overlap
        assert len(tiles) > 4
        
        # Check that tiles cover the entire image
        min_x = min(x0 for x0, y0, x1, y1 in tiles)
        max_x = max(x1 for x0, y0, x1, y1 in tiles)
        min_y = min(y0 for x0, y0, x1, y1 in tiles)
        max_y = max(y1 for x0, y0, x1, y1 in tiles)
        
        assert min_x == 0
        assert max_x == 1024
        assert min_y == 0
        assert max_y == 1024
    
    def test_non_divisible_dimensions(self):
        """Test tiling with non-divisible dimensions."""
        tiles = tile_slices(1000, 1000, 512, 64)
        
        # Should still cover the entire image
        min_x = min(x0 for x0, y0, x1, y1 in tiles)
        max_x = max(x1 for x0, y0, x1, y1 in tiles)
        min_y = min(y0 for x0, y0, x1, y1 in tiles)
        max_y = max(y1 for x0, y0, x1, y1 in tiles)
        
        assert min_x == 0
        assert max_x == 1000
        assert min_y == 0
        assert max_y == 1000
    
    def test_small_image(self):
        """Test tiling with image smaller than tile size."""
        tiles = tile_slices(256, 256, 512, 64)
        
        # Should create 1 tile
        assert len(tiles) == 1
        assert tiles[0] == (0, 0, 256, 256)


class TestBlendMask:
    """Test cases for create_blend_mask function."""
    
    def test_no_overlap(self):
        """Test blend mask with no overlap."""
        mask = create_blend_mask(512, 0, "cosine")
        
        # Should be all ones
        assert np.allclose(mask, 1.0)
        assert mask.shape == (512, 512)
    
    def test_cosine_blend(self):
        """Test cosine blend mode."""
        mask = create_blend_mask(512, 64, "cosine")
        
        # Check shape
        assert mask.shape == (512, 512)
        
        # Check edge values
        assert np.allclose(mask[:, 0], 0.0)  # Left edge
        assert np.allclose(mask[:, -1], 0.0)  # Right edge
        assert np.allclose(mask[0, :], 0.0)  # Top edge
        assert np.allclose(mask[-1, :], 0.0)  # Bottom edge
        
        # Check center values
        assert np.allclose(mask[256, 256], 1.0)
    
    def test_linear_blend(self):
        """Test linear blend mode."""
        mask = create_blend_mask(512, 64, "linear")
        
        # Check shape
        assert mask.shape == (512, 512)
        
        # Check edge values
        assert np.allclose(mask[:, 0], 0.0)  # Left edge
        assert np.allclose(mask[:, -1], 0.0)  # Right edge
        assert np.allclose(mask[0, :], 0.0)  # Top edge
        assert np.allclose(mask[-1, :], 0.0)  # Bottom edge
        
        # Check center values
        assert np.allclose(mask[256, 256], 1.0)
    
    def test_laplacian_blend(self):
        """Test laplacian blend mode."""
        mask = create_blend_mask(512, 64, "laplacian")
        
        # Check shape
        assert mask.shape == (512, 512)
        
        # Check edge values
        assert np.allclose(mask[:, 0], 0.0)  # Left edge
        assert np.allclose(mask[:, -1], 0.0)  # Right edge
        assert np.allclose(mask[0, :], 0.0)  # Top edge
        assert np.allclose(mask[-1, :], 0.0)  # Bottom edge
        
        # Check center values
        assert np.allclose(mask[256, 256], 1.0)


class TestBlendPaste:
    """Test cases for blend_paste function."""
    
    def test_blend_paste_no_overlap(self):
        """Test blend paste with no overlap."""
        # Create test canvas and tile
        canvas = np.zeros((100, 100, 3), dtype=np.uint8)
        tile = np.ones((50, 50, 3), dtype=np.uint8) * 255
        
        # Paste tile
        blend_paste(canvas, tile, (25, 25, 75, 75), 0, "cosine")
        
        # Check that tile was pasted
        assert np.allclose(canvas[25:75, 25:75], 255)
        # Check that other areas are unchanged
        assert np.allclose(canvas[0:25, :], 0)
        assert np.allclose(canvas[75:, :], 0)
    
    def test_blend_paste_with_overlap(self):
        """Test blend paste with overlap."""
        # Create test canvas and tile
        canvas = np.zeros((100, 100, 3), dtype=np.uint8)
        tile = np.ones((50, 50, 3), dtype=np.uint8) * 255
        
        # Paste tile with overlap
        blend_paste(canvas, tile, (25, 25, 75, 75), 16, "cosine")
        
        # Check that tile was pasted
        assert np.allclose(canvas[41:59, 41:59], 255)  # Center area
        # Check that overlap areas are blended (not 0 or 255)
        assert not np.allclose(canvas[25:41, 25:75], 0)
        assert not np.allclose(canvas[25:41, 25:75], 255)
    
    def test_blend_paste_grayscale(self):
        """Test blend paste with grayscale images."""
        # Create test canvas and tile
        canvas = np.zeros((100, 100), dtype=np.uint8)
        tile = np.ones((50, 50), dtype=np.uint8) * 255
        
        # Paste tile
        blend_paste(canvas, tile, (25, 25, 75, 75), 0, "cosine")
        
        # Check that tile was pasted
        assert np.allclose(canvas[25:75, 25:75], 255)


class TestProcessTiled:
    """Test cases for process_tiled function."""
    
    def test_process_tiled_simple(self):
        """Test simple tiled processing."""
        # Mock generate function
        def mock_generate(crop=None, **kwargs):
            if crop:
                x0, y0, x1, y1 = crop
                # Create a tile with coordinates drawn on it
                tile = np.zeros((y1-y0, x1-x0, 3), dtype=np.uint8)
                # Draw a simple pattern
                tile[:, :] = [x0 % 255, y0 % 255, (x0 + y0) % 255]
                return tile
            else:
                return np.zeros((512, 512, 3), dtype=np.uint8)
        
        # Process tiled generation
        result = process_tiled(
            mock_generate,
            width=1024,
            height=1024,
            tile_size=512,
            overlap=64,
            blend_mode="cosine"
        )
        
        # Check result
        assert result.shape == (1024, 1024, 3)
        assert result.dtype == np.uint8
    
    def test_process_tiled_with_crop(self):
        """Test tiled processing with crop parameter."""
        # Mock generate function that expects crop parameter
        def mock_generate_with_crop(crop, **kwargs):
            x0, y0, x1, y1 = crop
            # Create a tile with coordinates drawn on it
            tile = np.zeros((y1-y0, x1-x0, 3), dtype=np.uint8)
            # Draw a simple pattern
            tile[:, :] = [x0 % 255, y0 % 255, (x0 + y0) % 255]
            return tile
        
        # Process tiled generation
        result = process_tiled(
            mock_generate_with_crop,
            width=1024,
            height=1024,
            tile_size=512,
            overlap=64,
            blend_mode="cosine"
        )
        
        # Check result
        assert result.shape == (1024, 1024, 3)
        assert result.dtype == np.uint8
    
    def test_process_tiled_pil_output(self):
        """Test tiled processing with PIL Image output."""
        # Mock generate function that returns PIL Image
        def mock_generate_pil(crop=None, **kwargs):
            if crop:
                x0, y0, x1, y1 = crop
                # Create a PIL Image
                tile = Image.new('RGB', (x1-x0, y1-y0), color=(x0 % 255, y0 % 255, (x0 + y0) % 255))
                return tile
            else:
                return Image.new('RGB', (512, 512), color=(0, 0, 0))
        
        # Process tiled generation
        result = process_tiled(
            mock_generate_pil,
            width=1024,
            height=1024,
            tile_size=512,
            overlap=64,
            blend_mode="cosine"
        )
        
        # Check result
        assert isinstance(result, Image.Image)
        assert result.size == (1024, 1024)
        assert result.mode == 'RGB'


class TestOptimalTileSize:
    """Test cases for calculate_optimal_tile_size function."""
    
    def test_optimal_tile_size_large_image(self):
        """Test optimal tile size calculation for large image."""
        tile_size, overlap = calculate_optimal_tile_size(2048, 2048)
        
        assert tile_size <= 512  # Should not exceed max
        assert tile_size > 256   # Should not be below min
        assert overlap > 0        # Should have some overlap
        assert overlap < tile_size  # Overlap should be less than tile size
    
    def test_optimal_tile_size_small_image(self):
        """Test optimal tile size calculation for small image."""
        tile_size, overlap = calculate_optimal_tile_size(256, 256)
        
        assert tile_size <= 512  # Should not exceed max
        assert tile_size >= 256  # Should be at least min
        assert overlap > 0        # Should have some overlap
    
    def test_optimal_tile_size_custom_bounds(self):
        """Test optimal tile size calculation with custom bounds."""
        tile_size, overlap = calculate_optimal_tile_size(
            1024, 1024, 
            max_tile_size=256, 
            min_tile_size=128
        )
        
        assert tile_size <= 256  # Should not exceed custom max
        assert tile_size >= 128  # Should not be below custom min
        assert overlap > 0        # Should have some overlap


class TestTilingValidation:
    """Test cases for validate_tiling_config function."""
    
    def test_validate_tiling_config_valid(self):
        """Test validation of valid tiling configuration."""
        validation = validate_tiling_config(1024, 1024, 512, 64)
        
        assert validation["valid"] is True
        assert validation["tile_count"] > 0
        assert validation["coverage"] >= 1.0  # Should cover entire image
        assert validation["has_gaps"] is False
        assert validation["efficiency"] > 0
    
    def test_validate_tiling_config_invalid(self):
        """Test validation of invalid tiling configuration."""
        # Tile size larger than image
        validation = validate_tiling_config(256, 256, 512, 64)
        
        assert validation["valid"] is False
        assert validation["tile_count"] == 0
    
    def test_validate_tiling_config_coverage(self):
        """Test coverage calculation."""
        validation = validate_tiling_config(1024, 1024, 512, 0)
        
        # With no overlap, coverage should be exactly 1.0
        assert abs(validation["coverage"] - 1.0) < 0.001
        assert validation["has_gaps"] is False
    
    def test_validate_tiling_config_efficiency(self):
        """Test efficiency calculation."""
        validation = validate_tiling_config(1024, 1024, 512, 64)
        
        # Efficiency should be reasonable
        assert validation["efficiency"] > 0
        assert validation["efficiency"] <= 1.0


class TestTilingIntegration:
    """Integration tests for tiling functionality."""
    
    def test_end_to_end_tiling(self):
        """Test complete tiling workflow."""
        # Create a deterministic test image
        def create_test_image(crop=None, **kwargs):
            if crop:
                x0, y0, x1, y1 = crop
                # Create a test pattern that varies by position
                tile = np.zeros((y1-y0, x1-x0, 3), dtype=np.uint8)
                for i in range(y1-y0):
                    for j in range(x1-x0):
                        tile[i, j] = [
                            (x0 + j) % 256,
                            (y0 + i) % 256,
                            ((x0 + j) + (y0 + i)) % 256
                        ]
                return tile
            else:
                # Return a 1024x1024 image for the full size case
                return np.zeros((1024, 1024, 3), dtype=np.uint8)
        
        # Test different tiling configurations
        test_configs = [
            (512, 0, "cosine"),
            (512, 64, "cosine"),
            (512, 64, "linear"),
            (512, 64, "laplacian")
        ]
        
        for tile_size, overlap, blend_mode in test_configs:
            # Generate tiled image
            tiled_result = process_tiled(
                create_test_image,
                width=1024,
                height=1024,
                tile_size=tile_size,
                overlap=overlap,
                blend_mode=blend_mode,
                crop=None  # Add crop parameter to kwargs
            )
            
                        # Generate reference image (single pass)
            reference_result = create_test_image()
            # Resize reference to match tiled result
            from scipy.ndimage import zoom
            if reference_result.shape != (1024, 1024, 3):
                zoom_factors = [1024 / reference_result.shape[0], 1024 / reference_result.shape[1], 1]
                reference_result = zoom(reference_result, zoom_factors, order=1).astype(np.uint8)

            # Check dimensions
            assert tiled_result.shape == (1024, 1024, 3)
            assert reference_result.shape == (1024, 1024, 3)
            
            # Check that results have the same shape and are not all zeros
            assert tiled_result.shape == (1024, 1024, 3)
            assert not np.all(tiled_result == 0)  # Should have some non-zero values
            
            # Check that results are reasonable (not all zeros or all same value)
            assert not np.allclose(tiled_result, 0)
            assert not np.allclose(tiled_result, tiled_result[0, 0])
    
    def test_tiling_consistency(self):
        """Test that tiling produces consistent results."""
        def create_consistent_image(crop=None, **kwargs):
            if crop:
                x0, y0, x1, y1 = crop
                # Create a consistent pattern
                tile = np.zeros((y1-y0, x1-x0, 3), dtype=np.uint8)
                tile[:, :] = [x0 % 128, y0 % 128, 64]
                return tile
            else:
                return np.zeros((512, 512, 3), dtype=np.uint8)
        
        # Generate same tiled image twice
        result1 = process_tiled(
            create_consistent_image,
            width=1024,
            height=1024,
            tile_size=512,
            overlap=64,
            blend_mode="cosine"
        )
        
        result2 = process_tiled(
            create_consistent_image,
            width=1024,
            height=1024,
            tile_size=512,
            overlap=64,
            blend_mode="cosine"
        )
        
        # Results should be identical
        assert np.array_equal(result1, result2)
