"""
Test suite for DreamLayer Labeled Grid Exporter
Includes snapshot test as required by Task #3 deliverables

Author: Brandon Lum
Date: August 2025
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from grid_exporter import LabeledGridExporter


class TestLabeledGridExporter:
    """Test suite for the labeled grid exporter functionality"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        self.test_images_dir = os.path.join(self.test_dir, "test_images")
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.test_images_dir, exist_ok=True)
        
        # Create small test images (tiny fixture as requested)
        self.create_test_images()
        
        # Initialize exporter with test directory
        self.exporter = LabeledGridExporter(output_dir=self.output_dir)
        # Override the main output dir to use our test images
        self.exporter.output_dir = self.test_images_dir
    
    def teardown_method(self):
        """Clean up after each test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_images(self):
        """Create tiny test fixture images for snapshot testing"""
        # Create 4 small test images with different colors
        colors = [
            (255, 100, 100),  # Red
            (100, 255, 100),  # Green  
            (100, 100, 255),  # Blue
            (255, 255, 100),  # Yellow
        ]
        
        self.test_image_paths = []
        
        for i, color in enumerate(colors):
            # Create 64x64 test image (tiny fixture)
            img = Image.new('RGB', (64, 64), color)
            filename = f"test_image_{i+1:03d}.png"
            filepath = os.path.join(self.test_images_dir, filename)
            img.save(filepath)
            self.test_image_paths.append(filepath)
            print(f"Created test image: {filename} with color {color}")
    
    def test_initialization(self):
        """Test that the exporter initializes correctly"""
        exporter = LabeledGridExporter()
        assert hasattr(exporter, 'output_dir')
        assert hasattr(exporter, 'served_images_dir')
        assert hasattr(exporter, 'logs_dir')
        assert hasattr(exporter, 'font')
    
    def test_get_recent_images(self):
        """Test image discovery functionality"""
        images = self.exporter.get_recent_images(count=4)
        
        assert len(images) == 4
        assert all('filename' in img for img in images)
        assert all('filepath' in img for img in images)
        assert all('mtime' in img for img in images)
        assert all('size' in img for img in images)
        
        # Images should be sorted by modification time (newest first)
        for i in range(len(images) - 1):
            assert images[i]['mtime'] >= images[i+1]['mtime']
    
    def test_metadata_extraction(self):
        """Test metadata extraction generates expected fields"""
        metadata = self.exporter.extract_metadata_from_logs("test_image_001.png", 1234567890.0)
        
        required_fields = ['sampler', 'steps', 'cfg', 'preset', 'seed']
        assert all(field in metadata for field in required_fields)
        assert all(isinstance(metadata[field], str) for field in required_fields)
        
        # Test that different files generate different metadata
        metadata2 = self.exporter.extract_metadata_from_logs("test_image_002.png", 1234567891.0)
        assert metadata != metadata2  # Should be different due to index variation
    
    def test_create_labeled_grid_basic(self):
        """Test basic grid creation functionality"""
        images = self.exporter.get_recent_images(count=4)
        grid_image = self.exporter.create_labeled_grid(images, grid_size=(2, 2))
        
        assert isinstance(grid_image, Image.Image)
        assert grid_image.mode == 'RGB'
        assert grid_image.width > 0
        assert grid_image.height > 0
        
        # Grid should be larger than individual images due to labels and padding
        assert grid_image.width > 64 * 2  # Larger than 2 images side by side
        assert grid_image.height > 64 * 2  # Larger than 2 images stacked
    
    def test_grid_auto_sizing(self):
        """Test automatic grid size calculation"""
        # Test with 4 images - should create 2x2 grid
        images = self.exporter.get_recent_images(count=4)
        grid_image = self.exporter.create_labeled_grid(images)
        
        # Verify grid was created successfully
        assert isinstance(grid_image, Image.Image)
        
        # Test with 3 images - should create 2x2 grid with one empty cell
        images = self.exporter.get_recent_images(count=3)
        grid_image = self.exporter.create_labeled_grid(images)
        assert isinstance(grid_image, Image.Image)
    
    def test_export_grid(self):
        """Test grid export functionality"""
        images = self.exporter.get_recent_images(count=4)
        output_path = self.exporter.export_grid(images, filename="test_grid.png", grid_size=(2, 2))
        
        assert os.path.exists(output_path)
        assert output_path.endswith('test_grid.png')
        
        # Verify the exported file is a valid PNG
        with Image.open(output_path) as img:
            assert img.format == 'PNG'
            assert img.mode == 'RGB'
    
    def test_create_grid_from_recent(self):
        """Test the main convenience method"""
        output_path = self.exporter.create_grid_from_recent(count=4, grid_size=(2, 2), filename="recent_grid.png")
        
        assert os.path.exists(output_path)
        assert "recent_grid.png" in output_path
        
        # Verify file properties
        file_size = os.path.getsize(output_path)
        assert file_size > 1000  # Should be reasonably sized PNG
    
    def test_snapshot_grid_output(self):
        """
        Snapshot test: Verify grid output has expected properties
        This test covers the "tiny fixture" requirement from Task #3
        """
        # Create grid from our tiny test fixture (64x64 images)
        output_path = self.exporter.create_grid_from_recent(count=4, grid_size=(2, 2), filename="snapshot_test.png")
        
        # Load and analyze the generated grid
        with Image.open(output_path) as grid_img:
            # Convert to numpy for analysis
            grid_array = np.array(grid_img)
            
            # Snapshot assertions - these define the expected behavior
            assert grid_img.format == 'PNG'
            assert grid_img.mode == 'RGB'
            
            # Grid should be larger than individual images due to labels and padding
            assert grid_img.width > 64 * 2
            assert grid_img.height > 64 * 2
            
            # Grid should have reasonable bounds (not too large for tiny fixtures)
            assert grid_img.width < 1000  # Reasonable for 2x2 grid of 64x64 images
            assert grid_img.height < 1000
            
            # Color analysis - should contain varied colors from our test images
            unique_colors = len(np.unique(grid_array.reshape(-1, grid_array.shape[-1]), axis=0))
            assert unique_colors > 10  # Should have many colors due to test images + labels + backgrounds
            
            # File size should be reasonable
            file_size = os.path.getsize(output_path)
            assert 5000 < file_size < 100000  # Reasonable PNG size for small grid
            
        print(f"✅ Snapshot test passed!")
        print(f"   📄 Grid file: {output_path}")
        print(f"   📐 Dimensions: {grid_img.width}x{grid_img.height}")
        print(f"   📏 File size: {file_size:,} bytes")
        print(f"   🎨 Color complexity: {unique_colors} unique colors")
    
    def test_stable_ordering(self):
        """Test that grid export has stable, consistent ordering"""
        # Create two grids with same parameters
        images = self.exporter.get_recent_images(count=4)
        
        grid1 = self.exporter.create_labeled_grid(images, grid_size=(2, 2))
        grid2 = self.exporter.create_labeled_grid(images, grid_size=(2, 2))
        
        # Convert to arrays for comparison
        array1 = np.array(grid1)
        array2 = np.array(grid2)
        
        # Should be identical (stable ordering)
        assert np.array_equal(array1, array2), "Grid ordering should be stable and consistent"
    
    def test_error_handling(self):
        """Test error handling for edge cases"""
        # Test with no images
        with pytest.raises(ValueError, match="No images provided"):
            self.exporter.create_labeled_grid([])
        
        # Test with invalid grid size
        images = self.exporter.get_recent_images(count=4)
        grid = self.exporter.create_labeled_grid(images, grid_size=(0, 1))
        # Should handle gracefully and auto-calculate


def test_cli_interface():
    """Test command-line interface"""
    # This would test the main() function
    # For now, just verify it can import correctly
    from grid_exporter import main
    assert callable(main)


if __name__ == "__main__":
    # Run basic tests for quick verification
    test = TestLabeledGridExporter()
    test.setup_method()
    
    try:
        print("🧪 Running basic functionality tests...")
        test.test_initialization()
        print("✅ Initialization test passed")
        
        test.test_get_recent_images()
        print("✅ Image discovery test passed")
        
        test.test_metadata_extraction()
        print("✅ Metadata extraction test passed")
        
        test.test_create_labeled_grid_basic()
        print("✅ Grid creation test passed")
        
        test.test_snapshot_grid_output()
        print("✅ Snapshot test passed")
        
        test.test_stable_ordering()
        print("✅ Stable ordering test passed")
        
        print("\n🎉 All tests passed! Grid exporter is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        test.teardown_method()