#!/usr/bin/env python3
"""
Tests for PNG Info metadata parsing functionality.
This test reproduces the alpha channel bug where PNG metadata isn't parsed correctly.
"""

import os
import sys
import tempfile
import unittest
from PIL import Image, PngImagePlugin
import json

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from utils.png_info import parse_png_metadata, extract_generation_parameters
except ImportError:
    # This will fail initially since we haven't created the module yet
    parse_png_metadata = None
    extract_generation_parameters = None


class TestPNGInfoParsing(unittest.TestCase):
    """Test PNG metadata parsing, especially with alpha channels."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_metadata = {
            "prompt": "beautiful landscape, highly detailed, 8k, realistic",
            "negative_prompt": "blurry, low quality, deformed, ugly",
            "steps": 20,
            "sampler_name": "euler",
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "seed": 12345,
            "model_name": "test_model.safetensors"
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_test_png(self, has_alpha=False, include_metadata=True):
        """Create a test PNG file with optional alpha channel and metadata."""
        # Create a test image
        mode = "RGBA" if has_alpha else "RGB"
        size = (100, 100)
        
        if has_alpha:
            # Create RGBA image with transparency
            img = Image.new(mode, size, (255, 0, 0, 128))  # Semi-transparent red
        else:
            # Create RGB image
            img = Image.new(mode, size, (255, 0, 0))  # Solid red
        
        # Add metadata if requested
        metadata = None
        if include_metadata:
            metadata = PngImagePlugin.PngInfo()
            
            # Add generation parameters as text chunks
            metadata.add_text("prompt", self.test_metadata["prompt"])
            metadata.add_text("negative_prompt", self.test_metadata["negative_prompt"])
            metadata.add_text("parameters", json.dumps({
                "steps": self.test_metadata["steps"],
                "sampler_name": self.test_metadata["sampler_name"],
                "cfg_scale": self.test_metadata["cfg_scale"],
                "width": self.test_metadata["width"],
                "height": self.test_metadata["height"],
                "seed": self.test_metadata["seed"],
                "model_name": self.test_metadata["model_name"]
            }))
        
        # Save the image
        filename = f"test_{'rgba' if has_alpha else 'rgb'}.png"
        filepath = os.path.join(self.temp_dir, filename)
        img.save(filepath, "PNG", pnginfo=metadata)
        
        return filepath

    def test_png_metadata_parsing_without_alpha(self):
        """Test PNG metadata parsing works correctly without alpha channel."""
        if parse_png_metadata is None:
            self.skipTest("PNG metadata parsing module not available")
        
        # Create test PNG without alpha channel
        png_path = self.create_test_png(has_alpha=False, include_metadata=True)
        
        # Parse metadata
        metadata = parse_png_metadata(png_path)
        
        # Verify metadata was parsed correctly
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.get("prompt"), self.test_metadata["prompt"])
        self.assertEqual(metadata.get("negative_prompt"), self.test_metadata["negative_prompt"])
        
        # Parse generation parameters
        params = extract_generation_parameters(metadata)
        self.assertIsNotNone(params)
        self.assertEqual(params.get("steps"), self.test_metadata["steps"])
        self.assertEqual(params.get("cfg_scale"), self.test_metadata["cfg_scale"])

    def test_png_metadata_parsing_with_alpha_channel_fails(self):
        """Test that demonstrates the alpha channel bug - this should FAIL initially."""
        if parse_png_metadata is None:
            self.skipTest("PNG metadata parsing module not available")
        
        # Create test PNG with alpha channel
        png_path = self.create_test_png(has_alpha=True, include_metadata=True)
        
        # Parse metadata - this should fail due to alpha channel bug
        metadata = parse_png_metadata(png_path)
        
        # These assertions should FAIL initially, demonstrating the bug
        self.assertIsNotNone(metadata, "Metadata should not be None for PNG with alpha channel")
        self.assertEqual(metadata.get("prompt"), self.test_metadata["prompt"], 
                        "Prompt should be parsed correctly even with alpha channel")
        self.assertEqual(metadata.get("negative_prompt"), self.test_metadata["negative_prompt"],
                        "Negative prompt should be parsed correctly even with alpha channel")
        
        # Parse generation parameters
        params = extract_generation_parameters(metadata)
        self.assertIsNotNone(params, "Generation parameters should be extracted even with alpha channel")
        self.assertEqual(params.get("steps"), self.test_metadata["steps"],
                        "Steps should be parsed correctly even with alpha channel")
        self.assertEqual(params.get("cfg_scale"), self.test_metadata["cfg_scale"],
                        "CFG scale should be parsed correctly even with alpha channel")

    def test_png_metadata_parsing_no_metadata(self):
        """Test PNG parsing with no metadata returns empty result."""
        if parse_png_metadata is None:
            self.skipTest("PNG metadata parsing module not available")
        
        # Create test PNG without metadata
        png_path = self.create_test_png(has_alpha=False, include_metadata=False)
        
        # Parse metadata
        metadata = parse_png_metadata(png_path)
        
        # Should return empty or None
        self.assertTrue(metadata is None or len(metadata) == 0)

    def test_png_metadata_parsing_invalid_file(self):
        """Test PNG parsing with invalid file handles errors gracefully."""
        if parse_png_metadata is None:
            self.skipTest("PNG metadata parsing module not available")
        
        # Test with non-existent file
        with self.assertRaises((FileNotFoundError, IOError)):
            parse_png_metadata("/nonexistent/file.png")

    def test_png_metadata_parsing_non_png_file(self):
        """Test PNG parsing with non-PNG file handles errors gracefully."""
        if parse_png_metadata is None:
            self.skipTest("PNG metadata parsing module not available")
        
        # Create a text file with PNG extension
        fake_png_path = os.path.join(self.temp_dir, "fake.png")
        with open(fake_png_path, 'w') as f:
            f.write("This is not a PNG file")
        
        # Should handle gracefully
        with self.assertRaises((IOError, ValueError)):
            parse_png_metadata(fake_png_path)

    def test_raw_png_text_chunk_extraction(self):
        """Test direct extraction of PNG text chunks to verify they exist."""
        # Create test PNG with alpha channel
        png_path = self.create_test_png(has_alpha=True, include_metadata=True)
        
        # Open with PIL and check text chunks directly
        with Image.open(png_path) as img:
            self.assertIsNotNone(img.text, "PNG should have text chunks")
            self.assertIn("prompt", img.text, "PNG should contain prompt in text chunks")
            self.assertIn("negative_prompt", img.text, "PNG should contain negative_prompt in text chunks")
            self.assertIn("parameters", img.text, "PNG should contain parameters in text chunks")
            
            # Verify the actual content
            self.assertEqual(img.text["prompt"], self.test_metadata["prompt"])
            self.assertEqual(img.text["negative_prompt"], self.test_metadata["negative_prompt"])


if __name__ == "__main__":
    unittest.main(verbosity=2)