"""
DreamLayer Labeled Grid Exporter
Creates labeled image grids from most recent images with generation parameters

Author: Brandon Lum
Task: Labeled Grid Exporter (Task #3)
Date: August 2025

This module implements a grid exporter that takes the most recent generated images
from DreamLayer and creates labeled grids showing generation parameters for each image.
"""

import os
import time
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handler if it doesn't exist
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class MetadataExtractor:
    """
    Handles extraction of generation metadata from DreamLayer log files.
    
    This component is responsible for finding and parsing generation parameters
    like sampler, steps, CFG scale, preset, and seed from log files.
    """
    
    def __init__(self, logs_dir: str):
        """
        Initialize the metadata extractor.
        
        Args:
            logs_dir: Directory containing DreamLayer log files
        """
        self.logs_dir = logs_dir
        self.use_mock_metadata = True  # TODO: Set to False when real log parsing is implemented
        
        logger.debug(f"MetadataExtractor initialized with logs_dir: {logs_dir}")
    
    def extract_metadata(self, image_filename: str, image_timestamp: float) -> Dict[str, str]:
        """
        Extract generation metadata for the given image.
        
        Args:
            image_filename: Name of the image file
            image_timestamp: File modification timestamp for matching
            
        Returns:
            Dictionary containing sampler, steps, cfg, preset, seed values
        """
        if self.use_mock_metadata:
            logger.debug(f"Using mock metadata for {image_filename} (timestamp: {image_timestamp})")
            return self._generate_mock_metadata(image_filename)
        else:
            return self._parse_actual_logs(image_filename, image_timestamp)
    
    def _generate_mock_metadata(self, image_filename: str) -> Dict[str, str]:
        """
        Generate mock metadata for testing and demonstration purposes.
        
        Args:
            image_filename: Name of the image file
            
        Returns:
            Dictionary with mock generation parameters
        """
        # Extract index from filename for variation (e.g., DreamLayer_00001_.png -> 1)
        match = re.search(r'(\d+)', image_filename)
        index = int(match.group(1)) if match else 0
        
        # Create varied but realistic metadata for demonstration
        samplers = ["Euler", "Euler a", "DPM++ 2M", "DDIM", "LMS"]
        steps = ["20", "25", "30", "35", "40"]
        cfg_scales = ["7.0", "7.5", "8.0", "8.5", "9.0"]
        presets = ["Default", "Creative", "Precise", "Artistic", "Photographic"]
        seeds = ["42", "123456", "789012", "345678", "901234", "567890", "234567", "678901"]
        
        return {
            'sampler': samplers[index % len(samplers)],
            'steps': steps[index % len(steps)],
            'cfg': cfg_scales[index % len(cfg_scales)],
            'preset': presets[index % len(presets)],
            'seed': seeds[index % len(seeds)]
        }
    
    def _parse_actual_logs(self, image_filename: str, image_timestamp: float) -> Dict[str, str]:
        """
        Parse actual DreamLayer log files to extract generation metadata.
        
        Args:
            image_filename: Name of the image file
            image_timestamp: File modification timestamp for matching
            
        Returns:
            Dictionary containing actual generation parameters from logs
            
        Raises:
            NotImplementedError: This method needs to be implemented for production use
        """
        # TODO: Implement actual log parsing logic
        # 1. Read log files from self.logs_dir
        # 2. Parse log entries around image_timestamp
        # 3. Extract sampler, steps, cfg, preset, seed from log entries
        # 4. Return actual metadata dictionary
        
        logger.warning(f"Actual log parsing not implemented for {image_filename}")
        raise NotImplementedError(
            "Actual log parsing not implemented. "
            "Set use_mock_metadata = True or implement this method."
        )


class GridLayoutManager:
    """
    Handles grid layout calculations and positioning.
    
    This component calculates optimal grid dimensions, cell sizes,
    and positioning for images and labels.
    """
    
    def __init__(self, cell_padding: int = 15, label_height: int = 120):
        """
        Initialize the grid layout manager.
        
        Args:
            cell_padding: Padding around each cell in pixels
            label_height: Height reserved for labels in pixels
        """
        self.cell_padding = cell_padding
        self.label_height = label_height
        
        logger.debug(f"GridLayoutManager initialized with padding: {cell_padding}, label_height: {label_height}")
    
    def calculate_grid_size(self, num_images: int, grid_size: Optional[Tuple[int, int]] = None) -> Tuple[int, int]:
        """
        Calculate optimal grid dimensions.
        
        Args:
            num_images: Number of images to arrange
            grid_size: Optional explicit grid size (columns, rows)
            
        Returns:
            Tuple of (columns, rows)
        """
        if grid_size is not None:
            return grid_size
        
        # Auto-calculate grid size to be roughly square
        cols = int(np.ceil(np.sqrt(num_images)))
        rows = int(np.ceil(num_images / cols))
        
        logger.debug(f"Calculated grid size: {cols}x{rows} for {num_images} images")
        return (cols, rows)
    
    def calculate_dimensions(self, images: List[Tuple[Image.Image, Dict]], grid_size: Tuple[int, int]) -> Dict[str, int]:
        """
        Calculate canvas and cell dimensions.
        
        Args:
            images: List of (PIL Image, metadata) tuples
            grid_size: Grid dimensions (columns, rows)
            
        Returns:
            Dictionary containing dimension information
        """
        if not images:
            raise ValueError("No images provided for dimension calculation")
        
        cols, rows = grid_size
        
        # Find maximum image dimensions
        max_width = max(img.width for img, _ in images)
        max_height = max(img.height for img, _ in images)
        
        # Calculate cell and grid dimensions
        cell_width = max_width + self.cell_padding * 2
        cell_height = max_height + self.label_height + self.cell_padding * 3
        
        grid_width = cols * cell_width
        grid_height = rows * cell_height
        
        dimensions = {
            'max_image_width': max_width,
            'max_image_height': max_height,
            'cell_width': cell_width,
            'cell_height': cell_height,
            'grid_width': grid_width,
            'grid_height': grid_height,
            'cols': cols,
            'rows': rows
        }
        
        logger.debug(f"Calculated dimensions: grid={grid_width}x{grid_height}, cell={cell_width}x{cell_height}")
        return dimensions
    
    def get_cell_position(self, index: int, dimensions: Dict[str, int]) -> Tuple[int, int]:
        """
        Calculate the position of a cell in the grid.
        
        Args:
            index: Image index (0-based)
            dimensions: Dimension information from calculate_dimensions
            
        Returns:
            Tuple of (x, y) coordinates for the cell
        """
        cols = dimensions['cols']
        cell_width = dimensions['cell_width']
        cell_height = dimensions['cell_height']
        
        row = index // cols
        col = index % cols
        
        x = col * cell_width + self.cell_padding
        y = row * cell_height + self.cell_padding
        
        return (x, y)


class GridRenderer:
    """
    Handles the actual rendering of images and labels onto the grid canvas.
    
    This component is responsible for creating the final grid image with
    proper positioning, backgrounds, and text labels.
    """
    
    def __init__(self, font: ImageFont.ImageFont, background_color: str = "#f8f8f8", cell_background_color: str = "#ffffff"):
        """
        Initialize the grid renderer.
        
        Args:
            font: Font to use for label text
            background_color: Background color for the entire grid
            cell_background_color: Background color for individual cells
        """
        self.font = font
        self.background_color = background_color
        self.cell_background_color = cell_background_color
        
        logger.debug(f"GridRenderer initialized with font: {type(font).__name__}")
    
    def create_canvas(self, dimensions: Dict[str, int]) -> Tuple[Image.Image, ImageDraw.Draw]:
        """
        Create a blank canvas with background color.
        
        Args:
            dimensions: Dimension information
            
        Returns:
            Tuple of (PIL Image, ImageDraw object)
        """
        canvas = Image.new("RGB", (dimensions['grid_width'], dimensions['grid_height']), color=self.background_color)
        draw = ImageDraw.Draw(canvas)
        
        logger.debug(f"Created canvas: {dimensions['grid_width']}x{dimensions['grid_height']}")
        return canvas, draw
    
    def render_cell(self, canvas: Image.Image, draw: ImageDraw.Draw, 
                   image: Image.Image, metadata: Dict[str, str], 
                   position: Tuple[int, int], dimensions: Dict[str, int]) -> None:
        """
        Render a single cell (image + labels) onto the canvas.
        
        Args:
            canvas: Main canvas to draw on
            draw: ImageDraw object for the canvas
            image: PIL Image to place
            metadata: Metadata dictionary for labels
            position: (x, y) position for the cell
            dimensions: Dimension information
        """
        x, y = position
        cell_width = dimensions['cell_width']
        cell_height = dimensions['cell_height']
        cell_padding = 15  # TODO: Get from layout manager
        
        # Add white background for this cell
        cell_bg = Image.new("RGB", (cell_width - cell_padding, cell_height - cell_padding), 
                           color=self.cell_background_color)
        canvas.paste(cell_bg, (x - cell_padding//2, y - cell_padding//2))
        
        # Paste the actual image
        canvas.paste(image, (x, y))
        
        # Draw labels below image
        self._draw_labels(draw, metadata, x, y + image.height + 8)
    
    def _draw_labels(self, draw: ImageDraw.Draw, metadata: Dict[str, str], x: int, y: int) -> None:
        """
        Draw metadata labels at the specified position.
        
        Args:
            draw: ImageDraw object
            metadata: Metadata dictionary
            x: X coordinate for labels
            y: Y coordinate for labels
        """
        labels = [
            f"Sampler: {metadata.get('sampler', 'Unknown')}",
            f"Steps: {metadata.get('steps', 'Unknown')}",
            f"CFG: {metadata.get('cfg', 'Unknown')}",
            f"Preset: {metadata.get('preset', 'Unknown')}",
            f"Seed: {metadata.get('seed', 'Unknown')}"
        ]
        
        line_height = 22
        for i, label_text in enumerate(labels):
            text_y = y + i * line_height
            draw.text((x, text_y), label_text, font=self.font, fill="#333333")


class LabeledGridExporter:
    """
    Creates labeled grids from most recent DreamLayer images.
    
    This class handles the complete workflow of:
    1. Finding recent generated images
    2. Extracting generation metadata (sampler, steps, CFG, preset, seed)
    3. Assembling images into a grid layout
    4. Burning parameter labels onto each grid cell
    5. Exporting the final grid as PNG with stable ordering
    
    The implementation is inspired by ComfyUI's grid systems but customized
    for DreamLayer's specific requirements and file structure.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the grid exporter with DreamLayer directory paths.
        
        Args:
            output_dir: Custom output directory for grid exports.
                       If None, uses DreamLayer's default output directory.
        """
        # Get the current file's directory (dream_layer_backend)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Set up main output directory
        if output_dir is None:
            self.output_dir = os.path.join(project_root, "Dream_Layer_Resources", "output")
        else:
            self.output_dir = output_dir
        
        # Set up served images directory (where DreamLayer API stores images)
        self.served_images_dir = os.path.join(current_dir, "served_images")
        
        # Set up logs directory (for metadata extraction)
        self.logs_dir = os.path.join(project_root, "logs")
        
        # Initialize font for labels
        self.font = self._setup_font()
        
        # Initialize components
        self.metadata_extractor = MetadataExtractor(self.logs_dir)
        self.layout_manager = GridLayoutManager()
        self.renderer = GridRenderer(self.font)
        
        logger.info(f"Main output directory: {self.output_dir}")
        logger.info(f"Served images directory: {self.served_images_dir}")
        logger.info(f"Logs directory: {self.logs_dir}")
        logger.info(f"Font initialized: {type(self.font).__name__}")
    
    def _setup_font(self) -> ImageFont.ImageFont:
        """
        Setup font for label text with fallbacks.
        
        Attempts to load fonts in order of preference:
        1. Roboto from comfy-easy-grids (if available)
        2. System fonts (Windows/Linux/macOS)
        3. PIL default font as fallback
        
        Returns:
            ImageFont object for text rendering
        """
        font_paths = [
            # Try comfy-easy-grids font first
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "comfy-easy-grids", "fonts", "Roboto-Regular.ttf"),
            # Windows system fonts
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            # Linux system fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            # macOS system fonts
            "/System/Library/Fonts/Arial.ttf",
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size=20)
            except Exception:
                continue
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def get_recent_images(self, count: int = 8) -> List[Dict[str, Any]]:
        """
        Get the most recent generated images from DreamLayer output directories.
        
        Scans both the main output directory and served images directory,
        sorts by modification time, and returns the most recent images.
        
        Args:
            count: Maximum number of recent images to retrieve
            
        Returns:
            List of image dictionaries containing filepath, filename, and metadata
        """
        images = []
        
        # Check both output directories
        directories_to_check = [
            self.output_dir,
            self.served_images_dir
        ]
        
        for directory in directories_to_check:
            if not os.path.exists(directory):
                logger.warning(f"Directory not found: {directory}")
                continue
                
            logger.debug(f"Scanning directory: {directory}")
            
            # Get all PNG files with timestamps
            try:
                for filename in os.listdir(directory):
                    if filename.lower().endswith('.png'):
                        filepath = os.path.join(directory, filename)
                        try:
                            stat = os.stat(filepath)
                            images.append({
                                'filename': filename,
                                'filepath': filepath,
                                'mtime': stat.st_mtime,
                                'size': stat.st_size
                            })
                        except Exception as e:
                            logger.warning(f"Could not stat {filepath}: {e}")
            except Exception as e:
                logger.warning(f"Could not list directory {directory}: {e}")
        
        # Sort by modification time (newest first) and take the requested count
        images.sort(key=lambda x: x['mtime'], reverse=True)
        recent_images = images[:count]
        
        logger.info(f"Found {len(recent_images)} recent images")
        return recent_images
    
    def extract_metadata_from_logs(self, image_filename: str, image_timestamp: float) -> Dict[str, str]:
        """
        Extract generation metadata from DreamLayer log files.
        
        Currently returns mock metadata. To implement actual log parsing:
        1. Implement _parse_actual_logs() method
        2. Set USE_MOCK_METADATA = False
        3. Ensure log files exist in self.logs_dir
        
        Args:
            image_filename: Name of the image file
            image_timestamp: File modification timestamp for matching
            
        Returns:
            Dictionary containing sampler, steps, cfg, preset, seed values
        """
        USE_MOCK_METADATA = True  # TODO: Set to False when real log parsing is implemented
        
        if USE_MOCK_METADATA:
            logger.debug(f"Using mock metadata for {image_filename} (timestamp: {image_timestamp})")
            return self._generate_mock_metadata(image_filename)
        else:
            return self._parse_actual_logs(image_filename, image_timestamp)
    
    def _generate_mock_metadata(self, image_filename: str) -> Dict[str, str]:
        """
        Generate mock metadata for testing and demonstration purposes.
        
        This is a placeholder implementation that should be replaced with
        actual log parsing when the log file format is known.
        
        Args:
            image_filename: Name of the image file
            
        Returns:
            Dictionary with mock generation parameters
        """
        # Extract index from filename for variation (e.g., DreamLayer_00001_.png -> 1)
        match = re.search(r'(\d+)', image_filename)
        index = int(match.group(1)) if match else 0
        
        # Create varied but realistic metadata for demonstration
        samplers = ["Euler", "Euler a", "DPM++ 2M", "DDIM", "LMS"]
        steps = ["20", "25", "30", "35", "40"]
        cfg_scales = ["7.0", "7.5", "8.0", "8.5", "9.0"]
        presets = ["Default", "Creative", "Precise", "Artistic", "Photographic"]
        seeds = ["42", "123456", "789012", "345678", "901234", "567890", "234567", "678901"]
        
        return {
            'sampler': samplers[index % len(samplers)],
            'steps': steps[index % len(steps)],
            'cfg': cfg_scales[index % len(cfg_scales)],
            'preset': presets[index % len(presets)],
            'seed': seeds[index % len(seeds)]
        }
    
    def _parse_actual_logs(self, image_filename: str, image_timestamp: float) -> Dict[str, str]:
        """
        Parse actual DreamLayer log files to extract generation metadata.
        
        This method should be implemented to parse txt2img_server.log and
        img2img_server.log files to find generation parameters that match
        the given image by timestamp.
        
        Args:
            image_filename: Name of the image file
            image_timestamp: File modification timestamp for matching
            
        Returns:
            Dictionary containing actual generation parameters from logs
            
        Raises:
            NotImplementedError: This method needs to be implemented for production use
        """
        # TODO: Implement actual log parsing logic
        # 1. Read log files from self.logs_dir
        # 2. Parse log entries around image_timestamp
        # 3. Extract sampler, steps, cfg, preset, seed from log entries
        # 4. Return actual metadata dictionary
        
        logger.warning(f"Actual log parsing not implemented for {image_filename}")
        raise NotImplementedError(
            "Actual log parsing not implemented. "
            "Set USE_MOCK_METADATA = True or implement this method."
        )
    
    def create_labeled_grid(self, 
                           images: List[Dict[str, Any]], 
                           grid_size: Optional[Tuple[int, int]] = None) -> Image.Image:
        """
        Create a labeled grid from image data.
        
        This is the core function that assembles individual images into a grid
        layout and burns generation parameter labels onto each cell.
        
        Algorithm:
        1. Calculate optimal grid dimensions if not specified
        2. Load and validate all images
        3. Calculate canvas size including space for labels
        4. Create blank canvas
        5. Place each image and draw parameter labels
        
        Args:
            images: List of image dictionaries with filepath and metadata
            grid_size: Optional (columns, rows) tuple. Auto-calculated if None.
            
        Returns:
            PIL Image containing the assembled labeled grid
            
        Raises:
            ValueError: If no images provided or images cannot be loaded
        """
        if not images:
            raise ValueError("No images provided")
        
        # Auto-calculate grid size if not provided (make it roughly square)
        if grid_size is None:
            num_images = len(images)
            cols = int(np.ceil(np.sqrt(num_images)))
            rows = int(np.ceil(num_images / cols))
            grid_size = (cols, rows)
        
        cols, rows = grid_size
        logger.info(f"Creating {cols}x{rows} grid for {len(images)} images")
        
        # Load all images and get dimensions
        loaded_images = []
        max_width = max_height = 0
        
        for img_info in images:
            try:
                pil_img = Image.open(img_info['filepath'])
                # Convert to RGB if necessary
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                loaded_images.append((pil_img, img_info))
                max_width = max(max_width, pil_img.width)
                max_height = max(max_height, pil_img.height)
                logger.debug(f"Loaded: {img_info['filename']} ({pil_img.width}x{pil_img.height})")
            except Exception as e:
                logger.error(f"Could not load image {img_info['filepath']}: {e}")
        
        if not loaded_images:
            raise ValueError("No images could be loaded")
        
        # Calculate label space needed
        label_height = 120  # Space for 5 lines of labels (24px each)
        cell_padding = 15
        
        # Calculate grid dimensions
        cell_width = max_width + cell_padding * 2
        cell_height = max_height + label_height + cell_padding * 3
        
        grid_width = cols * cell_width
        grid_height = rows * cell_height
        
        logger.debug(f"Grid canvas size: {grid_width}x{grid_height}")
        logger.debug(f"Cell size: {cell_width}x{cell_height}")
        
        # Create grid canvas with light gray background
        grid_canvas = Image.new("RGB", (grid_width, grid_height), color="#f8f8f8")
        draw = ImageDraw.Draw(grid_canvas)
        
        # Place images in grid with labels
        for idx, (img, img_info) in enumerate(loaded_images):
            if idx >= cols * rows:
                break
                
            row = idx // cols
            col = idx % cols
            
            # Calculate position
            x = col * cell_width + cell_padding
            y = row * cell_height + cell_padding
            
            logger.debug(f"Placing image {idx} at grid position ({col}, {row}) -> canvas ({x}, {y})")
            
            # Add white background for this cell
            cell_bg = Image.new("RGB", (cell_width - cell_padding, cell_height - cell_padding), color="#ffffff")
            grid_canvas.paste(cell_bg, (x - cell_padding//2, y - cell_padding//2))
            
            # Paste image
            grid_canvas.paste(img, (x, y))
            
            # Extract metadata for this image
            metadata = self.extract_metadata_from_logs(img_info['filename'], img_info['mtime'])
            
            # Draw labels below image
            label_y = y + img.height + 8
            labels = [
                f"Sampler: {metadata.get('sampler', 'Unknown')}",
                f"Steps: {metadata.get('steps', 'Unknown')}",
                f"CFG: {metadata.get('cfg', 'Unknown')}",
                f"Preset: {metadata.get('preset', 'Unknown')}",
                f"Seed: {metadata.get('seed', 'Unknown')}"
            ]
            
            # Draw each label line
            line_height = 22
            for i, label_text in enumerate(labels):
                text_y = label_y + i * line_height
                if text_y < grid_canvas.height - 25:  # Ensure we don't draw outside canvas
                    draw.text((x, text_y), label_text, font=self.font, fill="#333333")
        
        logger.info("Grid assembly completed")
        return grid_canvas
    
    def export_grid(self, 
                   images: List[Dict[str, Any]], 
                   filename: Optional[str] = None,
                   grid_size: Optional[Tuple[int, int]] = None) -> str:
        """
        Export a labeled grid to PNG file with metadata.
        
        Creates the grid and saves it to the output directory with
        proper PNG metadata for tracking grid information.
        
        Args:
            images: List of image dictionaries
            filename: Output filename. Auto-generated with timestamp if None.
            grid_size: Grid dimensions. Auto-calculated if None.
            
        Returns:
            Full path to the exported grid file
        """
        if filename is None:
            timestamp = int(time.time())
            filename = f"labeled_grid_{timestamp}.png"
        
        # Ensure filename ends with .png
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        logger.info("Creating labeled grid...")
        
        # Create the grid
        grid_image = self.create_labeled_grid(images, grid_size)
        
        # Save to output directory
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        
        # Save with metadata
        grid_image.save(output_path, format='PNG', optimize=True)
        
        file_size = os.path.getsize(output_path)
        logger.info(f"Grid exported successfully to: {output_path}")
        logger.info(f"File size: {file_size:,} bytes, dimensions: {grid_image.width}x{grid_image.height}")
        
        return output_path
    
    def create_grid_from_recent(self, 
                               count: int = 8, 
                               grid_size: Optional[Tuple[int, int]] = None,
                               filename: Optional[str] = None) -> str:
        """
        Convenience method to create grid from most recent images.
        
        Combines get_recent_images(), metadata extraction, and export_grid()
        into a single operation for easy use.
        
        Args:
            count: Number of recent images to include in grid
            grid_size: Grid dimensions (columns, rows). Auto-calculated if None.
            filename: Output filename. Auto-generated if None.
            
        Returns:
            Path to the exported grid file
            
        Example:
            exporter = LabeledGridExporter()
            grid_path = exporter.create_grid_from_recent(count=6, grid_size=(3, 2))
        """
        logger.info(f"Creating labeled grid from {count} most recent images...")
        
        # Get recent images
        recent_images = self.get_recent_images(count)
        
        if not recent_images:
            raise ValueError("No recent images found to create grid")
        
        logger.info(f"Selected {len(recent_images)} images:")
        for i, img in enumerate(recent_images):
            logger.debug(f"  {i+1}. {img['filename']}")
        
        # Export the grid
        return self.export_grid(recent_images, filename, grid_size)


def main():
    """
    Command-line interface for testing and demonstration.
    
    Provides a simple CLI to test the grid exporter functionality
    with various parameters.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="DreamLayer Labeled Grid Exporter")
    parser.add_argument("--count", type=int, default=8, 
                       help="Number of recent images to include (default: 8)")
    parser.add_argument("--output", type=str, 
                       help="Output filename (auto-generated if not specified)")
    parser.add_argument("--cols", type=int, 
                       help="Number of columns in grid")
    parser.add_argument("--rows", type=int, 
                       help="Number of rows in grid")
    
    args = parser.parse_args()
    
    grid_size = None
    if args.cols and args.rows:
        grid_size = (args.cols, args.rows)
    
    try:
        logger.info("DreamLayer Labeled Grid Exporter")
        logger.info("=" * 50)
        
        exporter = LabeledGridExporter()
        output_path = exporter.create_grid_from_recent(
            count=args.count,
            grid_size=grid_size,
            filename=args.output
        )
        
        logger.info("=" * 50)
        logger.info(f"Grid created successfully: {output_path}")
        
    except Exception as e:
        logger.error(f"Error creating grid: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())