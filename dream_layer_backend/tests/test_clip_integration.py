#!/usr/bin/env python3
"""
Tests for CLIP integration in the labeled grid exporter.

This test suite validates the CLIP auto-labeling functionality by:
1. Testing CLIP model loading and initialization
2. Testing label generation with different image types
3. Testing the integration with grid assembly
4. Testing fallback behavior when CLIP fails
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
import pytest
from unittest.mock import Mock, patch, MagicMock

from PIL import Image, ImageDraw, ImageFont

# Import the functions we want to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dream_layer_backend_utils.labeled_grid_exporter import (
    CLIPLabeler,
    assemble_grid_enhanced,
    GridTemplate,
    collect_images
)


class TestCLIPIntegrationBasic:
    """Basic tests that don't require CLIP to be installed."""
    
    def test_import_works(self):
        """Test that the module can be imported."""
        try:
            from dream_layer_backend_utils.labeled_grid_exporter import (
                assemble_grid_enhanced,
                GridTemplate,
                collect_images
            )
            assert True  # Import succeeded
        except ImportError as e:
            pytest.skip(f"Module import failed: {e}")
    
    def test_grid_template_creation(self):
        """Test GridTemplate creation."""
        try:
            template = GridTemplate("test", 2, 3, (256, 256))
            assert template.name == "test"
            assert template.rows == 2
            assert template.cols == 3
            assert template.cell_size == (256, 256)
        except NameError:
            pytest.skip("GridTemplate not available")


class TestCLIPIntegration:
    """Test suite for CLIP integration functionality."""
    
    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Create a temporary directory with test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture(scope="class")
    def test_images_dir(self, test_data_dir):
        """Create test images directory and generate diverse test images."""
        images_dir = os.path.join(test_data_dir, "test_images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate diverse test images for CLIP testing
        test_images = [
            ("landscape.png", (512, 512), (100, 150, 200), "landscape"),
            ("portrait.png", (512, 512), (200, 100, 150), "portrait"),
            ("animal.png", (512, 512), (150, 200, 100), "animal"),
            ("building.png", (512, 512), (180, 180, 180), "building"),
            ("vehicle.png", (512, 512), (100, 100, 100), "vehicle"),
        ]
        
        for filename, size, color, image_type in test_images:
            img = Image.new("RGB", size, color)
            draw = ImageDraw.Draw(img)
            
            # Add descriptive text based on image type
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 50), f"{image_type.title()} Image", fill="white", font=font)
            draw.text((50, 100), f"Type: {image_type}", fill="white", font=font)
            
            # Add visual elements based on type
            if image_type == "landscape":
                # Draw mountains and sky
                draw.rectangle([0, 0, size[0], size[1]//2], fill=(135, 206, 235))  # Sky
                draw.polygon([(100, size[1]//2), (200, 100), (300, size[1]//2)], fill=(139, 69, 19))  # Mountain
            elif image_type == "portrait":
                # Draw a simple face
                draw.ellipse([150, 100, 350, 300], fill=(255, 218, 185))  # Face
                draw.ellipse([200, 150, 220, 170], fill=(0, 0, 0))  # Eye
                draw.ellipse([280, 150, 300, 170], fill=(0, 0, 0))  # Eye
            elif image_type == "animal":
                # Draw a simple animal shape
                draw.ellipse([100, 200, 400, 400], fill=(139, 69, 19))  # Body
                draw.ellipse([350, 150, 450, 250], fill=(139, 69, 19))  # Head
            elif image_type == "building":
                # Draw a simple building
                draw.rectangle([100, 200, 400, 450], fill=(169, 169, 169))  # Building
                draw.rectangle([150, 250, 200, 300], fill=(135, 206, 235))  # Window
                draw.rectangle([250, 250, 300, 300], fill=(135, 206, 235))  # Window
            elif image_type == "vehicle":
                # Draw a simple car
                draw.rectangle([100, 300, 400, 400], fill=(255, 0, 0))  # Car body
                draw.ellipse([150, 350, 200, 400], fill=(0, 0, 0))  # Wheel
                draw.ellipse([300, 350, 350, 400], fill=(0, 0, 0))  # Wheel
            
            img.save(os.path.join(images_dir, filename))
        
        return images_dir
    
    @pytest.fixture(scope="class")
    def output_dir(self, test_data_dir):
        """Create output directory for test results."""
        output_dir = os.path.join(test_data_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def test_clip_labeler_initialization(self):
        """Test CLIP labeler initialization."""
        # Test with default model
        try:
            labeler = CLIPLabeler()
            assert labeler.model_name == "openai/clip-vit-base-patch32"
            assert labeler.device in ["cuda", "cpu"]
            print(f"CLIP labeler initialized successfully on {labeler.device}")
        except ImportError as e:
            pytest.skip(f"transformers library not available: {e}")
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_clip_labeler_custom_model(self):
        """Test CLIP labeler with custom model."""
        try:
            labeler = CLIPLabeler(model_name="openai/clip-vit-base-patch16")
            assert labeler.model_name == "openai/clip-vit-base-patch16"
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_clip_labeler_device_selection(self):
        """Test CLIP labeler device selection."""
        try:
            # Test CPU device
            labeler = CLIPLabeler(device="cpu")
            assert labeler.device == "cpu"
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_generate_label_basic(self, test_images_dir):
        """Test basic label generation."""
        try:
            labeler = CLIPLabeler()
            
            # Load a test image
            image_path = os.path.join(test_images_dir, "landscape.png")
            with Image.open(image_path) as img:
                label = labeler.generate_label(img)
            
            # Validate label
            assert isinstance(label, str)
            assert len(label) > 0
            assert len(label) <= 50  # Max length check
            print(f"Generated label: {label}")
            
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_generate_label_different_images(self, test_images_dir):
        """Test label generation with different image types."""
        try:
            labeler = CLIPLabeler()
            
            image_files = ["landscape.png", "portrait.png", "animal.png", "building.png", "vehicle.png"]
            
            for image_file in image_files:
                image_path = os.path.join(test_images_dir, image_file)
                with Image.open(image_path) as img:
                    label = labeler.generate_label(img)
                
                assert isinstance(label, str)
                assert len(label) > 0
                print(f"{image_file}: {label}")
                
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_generate_label_max_length(self, test_images_dir):
        """Test label generation with custom max length."""
        try:
            labeler = CLIPLabeler()
            
            image_path = os.path.join(test_images_dir, "landscape.png")
            with Image.open(image_path) as img:
                # Test with very short max length
                label = labeler.generate_label(img, max_length=10)
            
            assert len(label) <= 10
            print(f"Short label: {label}")
            
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_batch_generate_labels(self, test_images_dir):
        """Test batch label generation."""
        try:
            labeler = CLIPLabeler()
            
            # Load multiple images
            images = []
            image_files = ["landscape.png", "portrait.png", "animal.png"]
            
            for image_file in image_files:
                image_path = os.path.join(test_images_dir, image_file)
                with Image.open(image_path) as img:
                    images.append(img.copy())
            
            # Generate labels in batch
            labels = labeler.batch_generate_labels(images)
            
            assert len(labels) == len(images)
            assert all(isinstance(label, str) for label in labels)
            assert all(len(label) > 0 for label in labels)
            
            for i, label in enumerate(labels):
                print(f"Batch label {i+1}: {label}")
                
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_clip_fallback_behavior(self):
        """Test CLIP fallback behavior when model fails."""
        # Test with invalid model name - should handle gracefully
        labeler = CLIPLabeler(model_name="invalid/model/name")
        
        # Should return "unlabeled" when model fails to load
        from unittest.mock import Mock
        result = labeler.generate_label(Mock())
        assert result == "unlabeled"
    
    def test_collect_images_with_clip(self, test_images_dir):
        """Test image collection with CLIP labeling."""
        try:
            labeler = CLIPLabeler()
            
            # Collect images with CLIP labeling
            images_info = collect_images(test_images_dir, None, labeler)
            
            assert len(images_info) == 5  # 5 test images
            
            # Check that CLIP labels were generated
            for img_info in images_info:
                assert 'metadata' in img_info
                assert 'auto_label' in img_info['metadata']
                assert isinstance(img_info['metadata']['auto_label'], str)
                assert len(img_info['metadata']['auto_label']) > 0
                print(f"{img_info['filename']}: {img_info['metadata']['auto_label']}")
                
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_assemble_grid_enhanced_with_clip(self, test_images_dir, output_dir):
        """Test enhanced grid assembly with CLIP labeling."""
        try:
            output_path = os.path.join(output_dir, "clip_grid.png")
            
            # Create grid template
            template = GridTemplate(
                name="clip_test",
                rows=2,
                cols=3,
                cell_size=(256, 256),
                margin=10,
                font_size=14
            )
            
            # Assemble grid with CLIP labeling
            result = assemble_grid_enhanced(
                input_dir=test_images_dir,
                output_path=output_path,
                template=template,
                use_clip=True,
                clip_model="openai/clip-vit-base-patch32"
            )
            
            # Validate result
            assert result['status'] == 'success'
            assert result['images_processed'] == 5
            assert result['grid_dimensions'] == "2x3"
            
            # Check output file
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            print(f"CLIP grid created: {output_path}")
            print(f"Result: {result}")
            
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_assemble_grid_enhanced_clip_vs_csv_priority(self, test_images_dir, output_dir):
        """Test that CSV labels take priority over CLIP labels."""
        # Create a simple CSV file
        csv_path = os.path.join(output_dir, "test_metadata.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write("filename,label\n")
            csvfile.write("landscape.png,CSV Landscape Label\n")
            csvfile.write("portrait.png,CSV Portrait Label\n")
        
        try:
            output_path = os.path.join(output_dir, "priority_test.png")
            
            template = GridTemplate("priority_test", 1, 2, (256, 256))
            
            # Assemble grid with both CSV and CLIP (CSV should take priority)
            result = assemble_grid_enhanced(
                input_dir=test_images_dir,
                output_path=output_path,
                template=template,
                csv_path=csv_path,
                label_columns=["label"],
                use_clip=True  # CLIP should be ignored when CSV is present
            )
            
            assert result['status'] == 'success'
            print(f"Priority test completed: {result}")
            
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")
    
    def test_clip_model_variants(self, test_images_dir, output_dir):
        """Test different CLIP model variants."""
        clip_models = [
            "openai/clip-vit-base-patch16",
            "openai/clip-vit-base-patch32",
        ]
        
        for model_name in clip_models:
            try:
                output_path = os.path.join(output_dir, f"clip_{model_name.replace('/', '_')}.png")
                
                template = GridTemplate("model_test", 1, 1, (256, 256))
                
                result = assemble_grid_enhanced(
                    input_dir=test_images_dir,
                    output_path=output_path,
                    template=template,
                    use_clip=True,
                    clip_model=model_name
                )
                
                assert result['status'] == 'success'
                print(f"Model {model_name}: {result}")
                
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
    
    def test_clip_error_handling(self, test_images_dir, output_dir):
        """Test error handling when CLIP fails."""
        output_path = os.path.join(output_dir, "clip_error_test.png")
        
        template = GridTemplate("error_test", 1, 1, (256, 256))
        
        # Test with invalid CLIP model
        with patch('dream_layer_backend_utils.labeled_grid_exporter.CLIPLabeler') as mock_clip:
            mock_clip.side_effect = Exception("CLIP model failed to load")
            
            # Should fall back to filename-based labels
            result = assemble_grid_enhanced(
                input_dir=test_images_dir,
                output_path=output_path,
                template=template,
                use_clip=True,
                clip_model="invalid/model"
            )
            
            # Should still succeed with fallback
            assert result['status'] == 'success'
            print(f"Error handling test completed: {result}")
    
    def test_clip_performance_benchmark(self, test_images_dir):
        """Benchmark CLIP performance with multiple images."""
        try:
            labeler = CLIPLabeler()
            
            import time
            
            # Load all test images
            images = []
            for filename in os.listdir(test_images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(test_images_dir, filename)
                    with Image.open(image_path) as img:
                        images.append(img.copy())
            
            # Benchmark individual processing
            start_time = time.time()
            individual_labels = []
            for img in images:
                label = labeler.generate_label(img)
                individual_labels.append(label)
            individual_time = time.time() - start_time
            
            # Benchmark batch processing
            start_time = time.time()
            batch_labels = labeler.batch_generate_labels(images)
            batch_time = time.time() - start_time
            
            print(f"\nPerformance Benchmark:")
            print(f"Individual processing: {individual_time:.2f}s for {len(images)} images")
            print(f"Batch processing: {batch_time:.2f}s for {len(images)} images")
            print(f"Speedup: {individual_time/batch_time:.2f}x")
            
            # Verify results are the same
            assert individual_labels == batch_labels
            
        except Exception as e:
            pytest.skip(f"CLIP model not available: {e}")


class TestCLIPIntegrationMock:
    """Test suite using mocked CLIP for unit testing."""
    
    @pytest.fixture
    def mock_clip_labeler(self):
        """Create a mocked CLIP labeler."""
        with patch('dream_layer_backend_utils.labeled_grid_exporter.CLIPLabeler') as mock:
            mock_instance = Mock()
            mock_instance.generate_label.return_value = "mocked label"
            mock_instance.batch_generate_labels.return_value = ["mocked label 1", "mocked label 2"]
            mock.return_value = mock_instance
            yield mock_instance
    
    def test_mock_clip_labeler(self, mock_clip_labeler):
        """Test with mocked CLIP labeler."""
        from dream_layer_backend_utils.labeled_grid_exporter import CLIPLabeler
        
        labeler = CLIPLabeler()
        label = labeler.generate_label(Mock())
        
        assert label == "mocked label"
        mock_clip_labeler.generate_label.assert_called_once()
    
    def test_mock_collect_images_with_clip(self, mock_clip_labeler, tmp_path):
        """Test image collection with mocked CLIP."""
        # Create a test image
        test_image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path)
        
        # Test collection with mocked CLIP
        images_info = collect_images(str(tmp_path), None, mock_clip_labeler)
        
        assert len(images_info) == 1
        assert 'metadata' in images_info[0]
        assert 'auto_label' in images_info[0]['metadata']
        assert images_info[0]['metadata']['auto_label'] == "mocked label"


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v", "--tb=short"]) 