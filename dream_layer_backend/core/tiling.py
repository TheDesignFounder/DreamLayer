"""
Tiling Module for DreamLayer AI

Handles large image generation by tiling and blending for high-resolution outputs.
"""

import math
import numpy as np
from PIL import Image
from typing import List, Tuple, Callable, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


class TilingConfig:
    """Configuration for tiled generation."""
    
    def __init__(
        self,
        tile_size: int = 512,
        overlap: int = 64,
        blend_mode: str = "cosine"
    ):
        self.tile_size = tile_size
        self.overlap = overlap
        self.blend_mode = blend_mode
        
        # Validate parameters
        if tile_size <= 0:
            raise ValueError("Tile size must be positive")
        if overlap < 0:
            raise ValueError("Overlap must be non-negative")
        if overlap >= tile_size:
            raise ValueError("Overlap must be less than tile size")
        if blend_mode not in ["cosine", "linear", "laplacian"]:
            raise ValueError("Blend mode must be 'cosine', 'linear', or 'laplacian'")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "tile_size": self.tile_size,
            "overlap": self.overlap,
            "blend_mode": self.blend_mode
        }


def tile_slices(
    width: int, 
    height: int, 
    tile_size: int, 
    overlap: int
) -> List[Tuple[int, int, int, int]]:
    """
    Generate tile coordinates for an image of given dimensions.
    
    Args:
        width: Image width
        height: Image height
        tile_size: Size of each tile
        overlap: Overlap between tiles
        
    Returns:
        List of (x0, y0, x1, y1) coordinates for each tile
    """
    tiles = []
    
    # Calculate step size (tile size minus overlap)
    step = tile_size - overlap
    
    # Generate tiles
    for y in range(0, height, step):
        for x in range(0, width, step):
            # Calculate tile boundaries
            x1 = min(x + tile_size, width)
            y1 = min(y + tile_size, height)
            
            # Ensure minimum tile size
            if x1 - x >= overlap and y1 - y >= overlap:
                tiles.append((x, y, x1, y1))
    
    return tiles


def create_blend_mask(
    tile_size: int, 
    overlap: int, 
    mode: str = "cosine"
) -> np.ndarray:
    """
    Create a blend mask for seamless tile joining.
    
    Args:
        tile_size: Size of the tile
        overlap: Overlap size
        mode: Blending mode ('cosine', 'linear', 'laplacian')
        
    Returns:
        Blend mask as numpy array
    """
    if overlap == 0:
        return np.ones((tile_size, tile_size))
    
    mask = np.ones((tile_size, tile_size))
    
    # Create overlap regions
    if overlap > 0:
        # Left edge
        for i in range(overlap):
            if mode == "cosine":
                weight = 0.5 * (1 - math.cos(math.pi * i / overlap))
            elif mode == "linear":
                weight = i / overlap
            else:  # laplacian
                weight = 1 - math.exp(-i / (overlap * 0.3))
            
            mask[:, i] *= weight
        
        # Right edge
        for i in range(overlap):
            if mode == "cosine":
                weight = 0.5 * (1 - math.cos(math.pi * (overlap - i - 1) / overlap))
            elif mode == "linear":
                weight = (overlap - i - 1) / overlap
            else:  # laplacian
                weight = 1 - math.exp(-(overlap - i - 1) / (overlap * 0.3))
            
            mask[:, tile_size - overlap + i] *= weight
        
        # Top edge
        for i in range(overlap):
            if mode == "cosine":
                weight = 0.5 * (1 - math.cos(math.pi * i / overlap))
            elif mode == "linear":
                weight = i / overlap
            else:  # laplacian
                weight = 1 - math.exp(-i / (overlap * 0.3))
            
            mask[i, :] *= weight
        
        # Bottom edge
        for i in range(overlap):
            if mode == "cosine":
                weight = 0.5 * (1 - math.cos(math.pi * (overlap - i - 1) / overlap))
            elif mode == "linear":
                weight = (overlap - i - 1) / overlap
            else:  # laplacian
                weight = 1 - math.exp(-(overlap - i - 1) / (overlap * 0.3))
            
            mask[tile_size - overlap + i, :] *= weight
    
    return mask


def blend_paste(
    canvas: np.ndarray,
    tile_img: np.ndarray,
    rect: Tuple[int, int, int, int],
    overlap: int,
    mode: str = "cosine"
) -> None:
    """
    Blend and paste a tile onto the canvas with seamless joining.
    
    Args:
        canvas: Target canvas array
        tile_img: Tile image array
        rect: (x0, y0, x1, y1) coordinates for placement
        overlap: Overlap size for blending
        mode: Blending mode
    """
    x0, y0, x1, y1 = rect
    tile_height, tile_width = tile_img.shape[:2]
    
    # Create blend mask for this tile
    blend_mask = create_blend_mask(tile_width, overlap, mode)
    
    # Apply blend mask to tile
    if len(tile_img.shape) == 3:  # Color image
        blended_tile = tile_img * blend_mask[:, :, np.newaxis]
    else:  # Grayscale image
        blended_tile = tile_img * blend_mask
    
    # Extract region from canvas
    canvas_region = canvas[y0:y1, x0:x1]
    
    # Blend with existing content
    if overlap > 0:
        # Create overlap mask for existing content
        overlap_mask = 1.0 - blend_mask[:y1-y0, :x1-x0]
        
        if len(canvas_region.shape) == 3:
            overlap_mask = overlap_mask[:, :, np.newaxis]
        
        # Blend existing content with new tile
        canvas_region = canvas_region * overlap_mask + blended_tile[:y1-y0, :x1-x0]
    else:
        canvas_region = blended_tile[:y1-y0, :x1-x0]
    
    # Update canvas
    canvas[y0:y1, x0:x1] = canvas_region


def process_tiled(
    generate_fn: Callable,
    width: int,
    height: int,
    tile_size: int = 512,
    overlap: int = 64,
    blend_mode: str = "cosine",
    **gen_kwargs
) -> Union[np.ndarray, Image.Image]:
    """
    Process large image generation using tiling and blending.
    
    Args:
        generate_fn: Function that generates a single tile
        width: Target image width
        height: Target image height
        tile_size: Size of each tile
        overlap: Overlap between tiles
        blend_mode: Blending mode for seamless joins
        **gen_kwargs: Additional arguments passed to generate_fn
        
    Returns:
        Generated image as numpy array or PIL Image
    """
    config = TilingConfig(tile_size, overlap, blend_mode)
    
    # Generate tile coordinates
    tiles = tile_slices(width, height, tile_size, overlap)
    logger.info(f"Processing {len(tiles)} tiles for {width}x{height} image")
    
    # Create output canvas
    if 'crop' in gen_kwargs:
        # Check if generate_fn expects crop parameter
        sample_kwargs = gen_kwargs.copy()
        sample_kwargs['crop'] = (0, 0, min(tile_size, width), min(tile_size, height))
        sample_result = generate_fn(**sample_kwargs)
        
        if isinstance(sample_result, Image.Image):
            sample_array = np.array(sample_result)
            output_dtype = sample_array.dtype
            output_channels = sample_array.shape[2] if len(sample_array.shape) > 2 else 1
        else:
            output_dtype = sample_result.dtype
            output_channels = sample_result.shape[2] if len(sample_result.shape) > 2 else 1
        
        if output_channels == 1:
            canvas = np.zeros((height, width), dtype=output_dtype)
        else:
            canvas = np.zeros((height, width, output_channels), dtype=output_dtype)
    else:
        # Default to RGB
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Process each tile
    for i, (x0, y0, x1, y1) in enumerate(tiles):
        logger.info(f"Processing tile {i+1}/{len(tiles)}: ({x0},{y0}) to ({x1},{y1})")
        
        try:
            # Generate tile
            if 'crop' in gen_kwargs:
                # Pass crop coordinates to generate function
                tile_kwargs = gen_kwargs.copy()
                tile_kwargs['crop'] = (x0, y0, x1, y1)
                tile_result = generate_fn(**tile_kwargs)
            else:
                # Generate full tile and crop
                tile_result = generate_fn(**gen_kwargs)
                if isinstance(tile_result, Image.Image):
                    tile_result = tile_result.crop((0, 0, x1-x0, y1-y0))
                else:
                    tile_result = tile_result[:y1-y0, :x1-x0]
            
            # Convert to numpy array if needed
            if isinstance(tile_result, Image.Image):
                tile_array = np.array(tile_result)
            else:
                tile_array = tile_result
            
            # Ensure tile dimensions match expected size
            expected_height, expected_width = y1-y0, x1-x0
            if tile_array.shape[:2] != (expected_height, expected_width):
                logger.warning(f"Tile size mismatch: expected {expected_height}x{expected_width}, got {tile_array.shape[:2]}")
                # Resize tile if needed
                if isinstance(tile_result, Image.Image):
                    tile_result = tile_result.resize((expected_width, expected_height), Image.Resampling.LANCZOS)
                    tile_array = np.array(tile_result)
                else:
                    # Simple resize for numpy arrays
                    from scipy.ndimage import zoom
                    zoom_factors = [expected_height / tile_array.shape[0], expected_width / tile_array.shape[1]]
                    if len(tile_array.shape) == 3:
                        zoom_factors.append(1)
                    tile_array = zoom(tile_array, zoom_factors, order=1)
            
            # Blend and paste tile
            blend_paste(canvas, tile_array, (x0, y0, x1, y1), overlap, blend_mode)
            
        except Exception as e:
            logger.error(f"Error processing tile {i+1}: {e}")
            # Fill with error pattern
            error_pattern = np.full((y1-y0, x1-x0, 3) if len(canvas.shape) == 3 else (y1-y0, x1-x0), 
                                  128, dtype=canvas.dtype)
            canvas[y0:y1, x0:x1] = error_pattern
    
    # Convert back to PIL Image if the generate function returns PIL Images
    try:
        # Test if generate function returns PIL Image
        test_result = generate_fn(**{**gen_kwargs, 'crop': (0, 0, 1, 1)})
        if isinstance(test_result, Image.Image):
            return Image.fromarray(canvas)
    except:
        pass
    
    return canvas


def calculate_optimal_tile_size(
    width: int, 
    height: int, 
    max_tile_size: int = 512,
    min_tile_size: int = 256
) -> Tuple[int, int]:
    """
    Calculate optimal tile size and overlap for given dimensions.
    
    Args:
        width: Image width
        height: Image height
        max_tile_size: Maximum tile size
        min_tile_size: Minimum tile size
        
    Returns:
        Tuple of (tile_size, overlap)
    """
    # Start with maximum tile size
    tile_size = max_tile_size
    
    # Calculate overlap as 1/8 of tile size
    overlap = tile_size // 8
    
    # Ensure minimum tile size
    if tile_size - overlap < min_tile_size:
        tile_size = min_tile_size + overlap
        overlap = tile_size // 8
    
    return tile_size, overlap


def validate_tiling_config(
    width: int, 
    height: int, 
    tile_size: int, 
    overlap: int
) -> Dict[str, Any]:
    """
    Validate tiling configuration for given image dimensions.
    
    Args:
        width: Image width
        height: Image height
        tile_size: Tile size
        overlap: Overlap size
        
    Returns:
        Dictionary with validation results
    """
    # Check if tile size is larger than image dimensions
    if tile_size > width or tile_size > height:
        return {
            "valid": False,
            "tile_count": 0,
            "coverage": 0.0,
            "has_gaps": True,
            "tiles": [],
            "efficiency": 0.0,
            "error": "Tile size larger than image dimensions"
        }
    
    tiles = tile_slices(width, height, tile_size, overlap)
    
    # Calculate coverage
    total_tile_area = sum((x1-x0) * (y1-y0) for x0, y0, x1, y1 in tiles)
    image_area = width * height
    coverage = total_tile_area / image_area
    
    # Check for gaps
    has_gaps = False
    if tiles:
        # Simple gap detection - check if tiles cover the entire image
        min_x = min(x0 for x0, y0, x1, y1 in tiles)
        max_x = max(x1 for x0, y0, x1, y1 in tiles)
        min_y = min(y0 for x0, y0, x1, y1 in tiles)
        max_y = max(y1 for x0, y0, x1, y1 in tiles)
        
        has_gaps = min_x > 0 or max_x < width or min_y > 0 or max_y < height
    
    return {
        "valid": len(tiles) > 0 and not has_gaps,
        "tile_count": len(tiles),
        "coverage": coverage,
        "has_gaps": has_gaps,
        "tiles": tiles,
        "efficiency": image_area / (len(tiles) * tile_size * tile_size) if tiles else 0
    }
