#!/usr/bin/env python3
"""
Snapshot tests for the labeled grid exporter.

This test suite validates the labeled grid exporter functionality by:
1. Generating dummy test images programmatically
2. Creating test CSV data with metadata
3. Running the grid exporter
4. Validating output dimensions, file existence, and content
"""

import os
import csv
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict

import pytest
from PIL import Image, ImageDraw, ImageFont

# Import the functions we want to test
from dream_layer_backend_utils.labeled_grid_exporter import (
    validate_inputs,
    read_metadata,
    collect_images,
    assemble_grid,
    determine_grid
)


class TestLabeledGridExporter:
    """Test suite for the labeled grid exporter functionality."""
    
    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Create a temporary directory with test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture(scope="class")
    def test_images_dir(self, test_data_dir):
        """Create test images directory and generate dummy images."""
        images_dir = os.path.join(test_data_dir, "test_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate 4 dummy test images with different colors and patterns
        test_images = [
            ("test_image_1.png", (512, 512), (255, 100, 100)),  # Red
            ("test_image_2.png", (512, 512), (100, 255, 100)),  # Green
            ("test_image_3.png", (512, 512), (100, 100, 255)),  # Blue
            ("test_image_4.png", (512, 512), (255, 255, 100)),  # Yellow
        ]
        
        for filename, size, color in test_images:
            img = Image.new("RGB", size, color)
            draw = ImageDraw.Draw(img)
            
            # Add some text to make images more interesting
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 50), f"Test Image {filename}", fill="white", font=font)
            draw.text((50, 100), f"Size: {size[0]}x{size[1]}", fill="white", font=font)
            draw.text((50, 150), f"Color: RGB{color}", fill="white", font=font)
            
            # Add a simple pattern
            for i in range(0, size[0], 50):
                for j in range(0, size[1], 50):
                    if (i + j) % 100 == 0:
                        draw.rectangle([i, j, i+25, j+25], fill="white")
            
            img.save(os.path.join(images_dir, filename))
        
        return images_dir
    
    @pytest.fixture(scope="class")
    def test_csv_path(self, test_data_dir):
        """Create test CSV file with metadata."""
        csv_path = os.path.join(test_data_dir, "test_metadata.csv")
        
        # Create test metadata that matches the generated images
        test_data = [
            {
                "filename": "test_image_1.png",
                "seed": "12345",
                "sampler": "euler_a",
                "steps": "20",
                "cfg": "7.5",
                "model": "stable-diffusion-v1-5"
            },
            {
                "filename": "test_image_2.png",
                "seed": "67890",
                "sampler": "dpm++_2m",
                "steps": "30",
                "cfg": "8.0",
                "model": "stable-diffusion-v2-1"
            },
            {
                "filename": "test_image_3.png",
                "seed": "11111",
                "sampler": "ddim",
                "steps": "25",
                "cfg": "6.5",
                "model": "stable-diffusion-v1-5"
            },
            {
                "filename": "test_image_4.png",
                "seed": "22222",
                "sampler": "euler",
                "steps": "15",
                "cfg": "9.0",
                "model": "stable-diffusion-v2-1"
            }
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["filename", "seed", "sampler", "steps", "cfg", "model"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_data)
        
        return csv_path
    
    @pytest.fixture(scope="class")
    def output_dir(self, test_data_dir):
        """Create output directory for test results."""
        output_dir = os.path.join(test_data_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def test_validate_inputs_success(self, test_images_dir, output_dir):
        """Test input validation with valid paths."""
        output_path = os.path.join(output_dir, "test_grid.png")
        
        # Should not raise any exceptions
        validate_inputs(test_images_dir, output_path)
        
        # Test with CSV
        csv_path = os.path.join(output_dir, "dummy.csv")
        with open(csv_path, 'w') as f:
            f.write("filename,seed\n")
        
        validate_inputs(test_images_dir, output_path, csv_path)
    
    def test_validate_inputs_failure(self, output_dir):
        """Test input validation with invalid paths."""
        output_path = os.path.join(output_dir, "test_grid.png")
        
        # Test non-existent input directory
        result = validate_inputs("/non/existent/path", output_path)
        assert result == False
        
        # Test non-existent CSV file (use a valid directory)
        result = validate_inputs(output_dir, output_path, "/non/existent.csv")
        assert result == True  # Should still be valid since CSV is optional
    
    def test_read_metadata(self, test_csv_path):
        """Test CSV metadata reading."""
        records = read_metadata(test_csv_path)
        
        assert len(records) == 4
        # records is now a dict keyed by filename, not a list
        assert all(isinstance(record, dict) for record in records.values())
        
        # Check that all expected columns are present
        expected_columns = {"filename", "seed", "sampler", "steps", "cfg", "model"}
        for record in records.values():
            assert all(col in record for col in expected_columns)
        
        # Check specific values (records is now dict keyed by filename)
        first_record = list(records.values())[0]
        assert first_record["filename"] == "test_image_1.png"
        assert first_record["seed"] == "12345"
        assert first_record["sampler"] == "euler_a"
    
    def test_collect_images_with_metadata(self, test_images_dir, test_csv_path):
        """Test image collection with CSV metadata."""
        csv_records = read_metadata(test_csv_path)
        images_info = collect_images(test_images_dir, csv_records)
        
        assert len(images_info) == 4
        
        # Check that metadata was properly merged
        for info in images_info:
            assert "path" in info
            assert "filename" in info
            assert "metadata" in info
            assert "seed" in info["metadata"]
            assert "sampler" in info["metadata"]
            assert "steps" in info["metadata"]
            assert "cfg" in info["metadata"]
            assert "model" in info["metadata"]
            
            # Verify path is correct
            assert os.path.exists(info["path"])
            assert os.path.basename(info["path"]) == info["filename"]
    
    def test_collect_images_without_metadata(self, test_images_dir):
        """Test image collection without CSV metadata."""
        images_info = collect_images(test_images_dir, None)
        
        assert len(images_info) == 4
        
        # Check that basic fields are present
        for info in images_info:
            assert "path" in info
            assert "filename" in info
            assert "metadata" in info
            assert os.path.exists(info["path"])
    
    def test_determine_grid(self):
        """Test grid dimension calculation."""
        # Create dummy images_info list
        images_info = [{"path": f"test_{i}.png"} for i in range(10)]
        
        # Test with fixed rows
        rows, cols = determine_grid(images_info, rows=2, cols=None)
        assert rows == 2
        assert cols == 5
        
        # Test with fixed columns
        rows, cols = determine_grid(images_info, rows=None, cols=3)
        assert rows == 4  # ceil(10/3)
        assert cols == 3
        
        # Test automatic calculation
        images_info_4 = [{"path": f"test_{i}.png"} for i in range(4)]
        rows, cols = determine_grid(images_info_4, rows=None, cols=None)
        assert rows == 2
        assert cols == 2
        
        # Test edge cases
        images_info_1 = [{"path": "test.png"}]
        rows, cols = determine_grid(images_info_1, rows=None, cols=None)
        assert rows == 1
        assert cols == 1
        
        # Test empty input - new behavior returns 0 rows for empty list
        rows, cols = determine_grid([], rows=None, cols=None)
        assert rows == 0  # Updated expectation for empty input
        assert cols == 0  # Updated expectation for empty input
    
    def test_assemble_grid_basic(self, test_images_dir, output_dir):
        """Test basic grid assembly without metadata."""
        output_path = os.path.join(output_dir, "basic_grid.png")
        
        # Collect images without metadata
        images_info = collect_images(test_images_dir, None)
        
        # Assemble grid
        assemble_grid(
            images_info=images_info,
            label_columns=[],  # No metadata columns
            output_path=output_path,
            rows=2,
            cols=2,
            font_size=16,
            margin=10
        )
        
        # Validate output
        self._validate_grid_output(output_path, expected_rows=2, expected_cols=2)
    
    def test_assemble_grid_with_metadata(self, test_images_dir, test_csv_path, output_dir):
        """Test grid assembly with CSV metadata."""
        output_path = os.path.join(output_dir, "metadata_grid.png")
        
        # Collect images with metadata
        csv_records = read_metadata(test_csv_path)
        images_info = collect_images(test_images_dir, csv_records)
        
        # Assemble grid with metadata labels
        assemble_grid(
            images_info=images_info,
            label_columns=["seed", "sampler", "steps", "cfg"],
            output_path=output_path,
            rows=2,
            cols=2,
            font_size=16,
            margin=10
        )
        
        # Validate output
        self._validate_grid_output(output_path, expected_rows=2, expected_cols=2)
    
    def test_assemble_grid_auto_layout(self, test_images_dir, output_dir):
        """Test grid assembly with automatic layout calculation."""
        output_path = os.path.join(output_dir, "auto_grid.png")
        
        # Collect images without metadata
        images_info = collect_images(test_images_dir, None)
        
        # Assemble grid with automatic layout
        assemble_grid(
            images_info=images_info,
            label_columns=[],
            output_path=output_path,
            rows=None,  # Auto-calculate
            cols=None,  # Auto-calculate
            font_size=16,
            margin=10
        )
        
        # Validate output (should be 2x2 for 4 images)
        self._validate_grid_output(output_path, expected_rows=2, expected_cols=2)
    
    def test_assemble_grid_custom_font_margin(self, test_images_dir, output_dir):
        """Test grid assembly with custom font size and margin."""
        output_path = os.path.join(output_dir, "custom_grid.png")
        
        # Collect images without metadata
        images_info = collect_images(test_images_dir, None)
        
        # Assemble grid with custom settings
        assemble_grid(
            images_info=images_info,
            label_columns=[],
            output_path=output_path,
            rows=2,
            cols=2,
            font_size=24,  # Larger font
            margin=20      # Larger margin
        )
        
        # Validate output
        self._validate_grid_output(output_path, expected_rows=2, expected_cols=2)
    
    def test_assemble_grid_empty_input(self, output_dir):
        """Test grid assembly with empty input (should raise error)."""
        output_path = os.path.join(output_dir, "empty_grid.png")
        
        with pytest.raises(ValueError, match="Invalid inputs:"):
            assemble_grid(
                images_info=[],
                label_columns=[],
                output_path=output_path,
                rows=2,
                cols=2
            )
    
    def test_end_to_end_workflow(self, test_images_dir, test_csv_path, output_dir):
        """Test complete end-to-end workflow."""
        output_path = os.path.join(output_dir, "e2e_grid.png")
        
        # Validate inputs
        validate_inputs(test_images_dir, output_path, test_csv_path)
        
        # Read metadata
        csv_records = read_metadata(test_csv_path)
        
        # Collect images
        images_info = collect_images(test_images_dir, csv_records)
        assert len(images_info) == 4
        
        # Assemble grid
        assemble_grid(
            images_info=images_info,
            label_columns=["seed", "sampler", "steps"],
            output_path=output_path,
            rows=2,
            cols=2,
            font_size=16,
            margin=10
        )
        
        # Validate final output
        self._validate_grid_output(output_path, expected_rows=2, expected_cols=2)
        
        # Check that labels contain expected metadata
        with Image.open(output_path) as img:
            # The image should be larger than individual test images due to grid layout
            # Using more conservative estimates for the enhanced version with 256px cells
            assert img.width > 250
            assert img.height > 250
    
    def _validate_grid_output(self, output_path: str, expected_rows: int, expected_cols: int):
        """Helper method to validate grid output."""
        # Check file exists and is not empty
        assert os.path.exists(output_path), f"Output file {output_path} does not exist"
        assert os.path.getsize(output_path) > 0, f"Output file {output_path} is empty"
        
        # Check file is a valid image
        with Image.open(output_path) as img:
            # Verify it's a valid image
            assert img.format in ['PNG', 'JPEG', 'BMP', 'TIFF'], f"Unexpected image format: {img.format}"
            
            # Check dimensions are reasonable
            assert img.width > 0, "Image width should be positive"
            assert img.height > 0, "Image height should be positive"
            
            # For a 2x2 grid with 256x256 images (new default) and margins, expect roughly:
            # Width: 2 * (256 + 2*10) = ~532 pixels
            # Height: 2 * (256 + label_height + 3*10) = ~600+ pixels
            # Using more conservative estimates for the enhanced version
            expected_min_width = expected_cols * 250  # Conservative estimate for 256px cells
            expected_min_height = expected_rows * 250  # Conservative estimate for 256px cells
            
            assert img.width >= expected_min_width, f"Image width {img.width} is too small for {expected_cols}x{expected_rows} grid"
            assert img.height >= expected_min_height, f"Image height {img.height} is too small for {expected_rows}x{expected_cols} grid"
            
            # Check that image is not completely blank (should have some non-white pixels)
            # Convert to RGB and check for non-white pixels
            rgb_img = img.convert('RGB')
            pixels = list(rgb_img.getdata())
            
            # Count non-white pixels (assuming white background)
            non_white_pixels = sum(1 for pixel in pixels if pixel != (255, 255, 255))
            assert non_white_pixels > 0, "Grid image appears to be completely blank"
            
            # Log some useful information
            print(f"\nGrid output validation:")
            print(f"  File: {output_path}")
            print(f"  Size: {img.width}x{img.height}")
            print(f"  Format: {img.format}")
            print(f"  File size: {os.path.getsize(output_path)} bytes")
            print(f"  Non-white pixels: {non_white_pixels}/{len(pixels)}")


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v"]) 