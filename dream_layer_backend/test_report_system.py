#!/usr/bin/env python3
"""
Comprehensive test suite for the DreamLayer Report Generation System
Tests both backend functionality and API endpoints
"""

import os
import json
import tempfile
import shutil
import zipfile
import csv
import time
import requests
import threading
from pathlib import Path
from typing import Dict, Any
import unittest
from unittest.mock import patch, MagicMock

# Import the components we're testing
from report_generator import ReportGenerator, ImageRecord


class TestImageRecord(unittest.TestCase):
    """Test cases for ImageRecord schema validation"""
    
    def test_required_columns(self):
        """Test that required columns are correctly defined"""
        required = ImageRecord.get_required_columns()
        expected = [
            'id', 'filename', 'relative_path', 'prompt', 'negative_prompt',
            'model_name', 'sampler_name', 'steps', 'cfg_scale', 'width', 
            'height', 'seed', 'timestamp', 'generation_type', 'batch_index'
        ]
        self.assertEqual(required, expected)
    
    def test_csv_schema_validation_valid(self):
        """Test CSV validation with valid schema"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write valid CSV with all required columns
            writer = csv.DictWriter(f, fieldnames=ImageRecord.get_required_columns())
            writer.writeheader()
            writer.writerow({
                'id': 'test1',
                'filename': 'test.png',
                'relative_path': 'grids/txt2img/test.png',
                'prompt': 'test prompt',
                'negative_prompt': 'test negative',
                'model_name': 'sd15.safetensors',
                'sampler_name': 'euler',
                'steps': 20,
                'cfg_scale': 7.0,
                'width': 512,
                'height': 512,
                'seed': 12345,
                'timestamp': '2024-01-01T00:00:00',
                'generation_type': 'txt2img',
                'batch_index': 0
            })
            
        try:
            result = ImageRecord.validate_csv_schema(f.name)
            self.assertTrue(result['valid'])
            self.assertEqual(result['row_count'], 1)
            self.assertEqual(len(result['missing_columns']), 0)
        finally:
            os.unlink(f.name)
    
    def test_csv_schema_validation_missing_columns(self):
        """Test CSV validation with missing required columns"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write CSV missing some required columns
            writer = csv.DictWriter(f, fieldnames=['id', 'filename', 'prompt'])
            writer.writeheader()
            writer.writerow({
                'id': 'test1',
                'filename': 'test.png',
                'prompt': 'test prompt'
            })
            
        try:
            result = ImageRecord.validate_csv_schema(f.name)
            self.assertFalse(result['valid'])
            self.assertGreater(len(result['missing_columns']), 0)
            self.assertIn('negative_prompt', result['missing_columns'])
            self.assertIn('model_name', result['missing_columns'])
        finally:
            os.unlink(f.name)
    
    def test_csv_schema_validation_nonexistent_file(self):
        """Test CSV validation with non-existent file"""
        result = ImageRecord.validate_csv_schema('/nonexistent/file.csv')
        self.assertFalse(result['valid'])
        self.assertIn('error', result)


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="dreamlayer_test_")
        self.served_images_dir = os.path.join(self.test_dir, "served_images")
        self.reports_dir = os.path.join(self.test_dir, "reports")
        os.makedirs(self.served_images_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Create sample image files
        self.sample_images = [
            "txt2img_sample_1.png",
            "txt2img_sample_2.png",
            "img2img_sample_1.png"
        ]
        
        for img_name in self.sample_images:
            img_path = os.path.join(self.served_images_dir, img_name)
            with open(img_path, 'wb') as f:
                f.write(b"FAKE_PNG_DATA" * 100)
        
        # Create sample gallery data
        self.gallery_data = {
            "txt2img": [
                {
                    "id": "txt2img_1",
                    "filename": "txt2img_sample_1.png",
                    "url": "http://localhost:5001/api/images/txt2img_sample_1.png",
                    "prompt": "A beautiful landscape",
                    "negativePrompt": "ugly, blurry",
                    "timestamp": "2024-01-15T10:30:00.000Z",
                    "settings": {
                        "model_name": "sd15.safetensors",
                        "sampler_name": "euler",
                        "steps": 20,
                        "cfg_scale": 7.0,
                        "width": 512,
                        "height": 512,
                        "seed": 12345
                    }
                },
                {
                    "id": "txt2img_2",
                    "filename": "txt2img_sample_2.png",
                    "url": "http://localhost:5001/api/images/txt2img_sample_2.png",
                    "prompt": "A cyberpunk city",
                    "negativePrompt": "low quality",
                    "timestamp": "2024-01-15T11:00:00.000Z",
                    "settings": {
                        "model_name": "sd15.safetensors",
                        "sampler_name": "dpm++",
                        "steps": 25,
                        "cfg_scale": 8.0,
                        "width": 768,
                        "height": 768,
                        "seed": 67890
                    }
                }
            ],
            "img2img": [
                {
                    "id": "img2img_1",
                    "filename": "img2img_sample_1.png",
                    "url": "http://localhost:5001/api/images/img2img_sample_1.png",
                    "prompt": "Enhanced version of input",
                    "negativePrompt": "distorted",
                    "timestamp": "2024-01-15T12:00:00.000Z",
                    "settings": {
                        "model_name": "sd15.safetensors",
                        "sampler_name": "euler",
                        "steps": 30,
                        "cfg_scale": 7.5,
                        "width": 512,
                        "height": 512,
                        "seed": 54321,
                        "denoising_strength": 0.7,
                        "input_image": "data:image/png;base64,..."
                    }
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_generator(self) -> ReportGenerator:
        """Create a ReportGenerator configured for testing"""
        # Store instance variables for the inner class to access
        served_images_dir = self.served_images_dir
        reports_dir = self.reports_dir
        test_dir = self.test_dir
        gallery_data = self.gallery_data
        
        class TestReportGenerator(ReportGenerator):
            def __init__(self):
                self.served_images_dir = served_images_dir
                self.reports_dir = reports_dir
                self.output_dir = os.path.join(test_dir, 'output')
                os.makedirs(self.output_dir, exist_ok=True)
            
            def fetch_gallery_data(self):
                return gallery_data
            
            def _get_models_info(self):
                return {
                    'checkpoints': ['sd15.safetensors', 'flux1-dev.safetensors'],
                    'loras': ['style_lora.safetensors'],
                    'controlnet': ['canny_controlnet.safetensors']
                }
        
        return TestReportGenerator()
    
    def test_scan_served_images(self):
        """Test scanning served images directory"""
        generator = self.create_test_generator()
        result = generator._scan_served_images()
        
        # Should find images and classify them
        self.assertIn('txt2img', result)
        self.assertIn('img2img', result)
        self.assertGreater(len(result['txt2img']), 0)
        self.assertGreater(len(result['img2img']), 0)
    
    def test_create_csv_records(self):
        """Test creation of CSV records from gallery data"""
        generator = self.create_test_generator()
        records = generator.create_csv_records(self.gallery_data)
        
        self.assertEqual(len(records), 3)  # 2 txt2img + 1 img2img
        
        # Check first record structure
        record = records[0]
        self.assertIsInstance(record, ImageRecord)
        self.assertIn(record.generation_type, ['txt2img', 'img2img'])
        self.assertIsNotNone(record.prompt)
        self.assertIsNotNone(record.model_name)
    
    def test_write_csv(self):
        """Test CSV writing functionality"""
        generator = self.create_test_generator()
        records = generator.create_csv_records(self.gallery_data)
        
        csv_path = os.path.join(self.test_dir, 'test_results.csv')
        generator.write_csv(records, csv_path)
        
        # Verify CSV was created and has correct structure
        self.assertTrue(os.path.exists(csv_path))
        
        validation = ImageRecord.validate_csv_schema(csv_path)
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['row_count'], 3)
    
    def test_generate_config_json(self):
        """Test configuration JSON generation"""
        generator = self.create_test_generator()
        config = generator.generate_config_json()
        
        # Check required sections
        self.assertIn('report_metadata', config)
        self.assertIn('system_settings', config)
        self.assertIn('available_models', config)
        self.assertIn('directory_structure', config)
        
        # Check metadata
        self.assertIn('generated_at', config['report_metadata'])
        self.assertIn('dreamlayer_version', config['report_metadata'])
        
        # Check models
        self.assertIn('checkpoints', config['available_models'])
    
    def test_copy_images_to_bundle(self):
        """Test copying images to bundle structure"""
        generator = self.create_test_generator()
        records = generator.create_csv_records(self.gallery_data)
        
        bundle_dir = os.path.join(self.test_dir, 'bundle')
        os.makedirs(bundle_dir, exist_ok=True)
        
        result = generator.copy_images_to_bundle(records, bundle_dir)
        
        # Check that images were copied
        self.assertGreater(len(result['copied_files']), 0)
        self.assertIn('txt2img', result['generation_types'])
        self.assertIn('img2img', result['generation_types'])
        
        # Verify grids directory structure
        grids_dir = os.path.join(bundle_dir, 'grids')
        self.assertTrue(os.path.exists(grids_dir))
        self.assertTrue(os.path.exists(os.path.join(grids_dir, 'txt2img')))
        self.assertTrue(os.path.exists(os.path.join(grids_dir, 'img2img')))
    
    def test_create_report_bundle(self):
        """Test complete report bundle creation"""
        generator = self.create_test_generator()
        result = generator.create_report_bundle("test_report.zip")
        
        # Check result status
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['total_images'], 3)
        self.assertTrue(result['csv_validation']['valid'])
        self.assertTrue(result['path_validation']['valid'])
        
        # Check that ZIP file was created
        self.assertTrue(os.path.exists(result['report_path']))
        self.assertGreater(result['bundle_size_bytes'], 0)
        
        # Verify ZIP contents
        with zipfile.ZipFile(result['report_path'], 'r') as zipf:
            zip_contents = zipf.namelist()
            
            # Check required files
            self.assertIn('results.csv', zip_contents)
            self.assertIn('config.json', zip_contents)
            self.assertIn('README.md', zip_contents)
            
            # Check grids structure
            self.assertTrue(any(path.startswith('grids/txt2img/') for path in zip_contents))
            self.assertTrue(any(path.startswith('grids/img2img/') for path in zip_contents))
    
    def test_validate_csv_paths_in_zip(self):
        """Test CSV path validation against ZIP contents"""
        generator = self.create_test_generator()
        result = generator.create_report_bundle("test_validation.zip")
        
        self.assertEqual(result['status'], 'success')
        
        # Extract and validate the generated CSV and ZIP
        csv_path = os.path.join(self.test_dir, 'extracted_results.csv')
        with zipfile.ZipFile(result['report_path'], 'r') as zipf:
            with zipf.open('results.csv') as csv_file:
                with open(csv_path, 'wb') as f:
                    f.write(csv_file.read())
        
        validation = generator._validate_csv_paths_in_zip(csv_path, result['report_path'])
        self.assertTrue(validation['valid'])
        self.assertEqual(len(validation['missing_paths']), 0)


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints (requires running server)"""
    
    BASE_URL = "http://localhost:5000"
    
    @classmethod
    def setUpClass(cls):
        """Check if server is running"""
        try:
            response = requests.get(f"{cls.BASE_URL}/", timeout=5)
            cls.server_available = response.status_code == 200
        except:
            cls.server_available = False
    
    def setUp(self):
        """Skip tests if server not available"""
        if not self.server_available:
            self.skipTest("Server not available")
    
    def test_gallery_data_endpoint(self):
        """Test updating gallery data via API"""
        test_data = {
            "txt2img": [
                {
                    "id": "api_test_1",
                    "filename": "api_test.png",
                    "prompt": "API test image",
                    "negativePrompt": "test negative",
                    "timestamp": "2024-01-01T00:00:00.000Z",
                    "settings": {
                        "model_name": "test_model.safetensors",
                        "sampler_name": "euler",
                        "steps": 20,
                        "cfg_scale": 7.0,
                        "width": 512,
                        "height": 512,
                        "seed": 12345
                    }
                }
            ],
            "img2img": []
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/gallery-data",
            json=test_data,
            timeout=10
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    def test_report_generation_endpoint(self):
        """Test report generation via API"""
        # First update gallery data
        self.test_gallery_data_endpoint()
        
        # Then generate report
        response = requests.post(
            f"{self.BASE_URL}/api/reports/generate",
            json={"filename": "api_test_report.zip"},
            timeout=30
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('report_filename', data)
        self.assertIn('total_images', data)
        self.assertIn('csv_validation', data)
        self.assertIn('path_validation', data)
    
    def test_csv_validation_endpoint(self):
        """Test CSV validation endpoint"""
        # Create a test CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=ImageRecord.get_required_columns())
            writer.writeheader()
            writer.writerow({
                'id': 'test1',
                'filename': 'test.png',
                'relative_path': 'grids/txt2img/test.png',
                'prompt': 'test prompt',
                'negative_prompt': 'test negative',
                'model_name': 'sd15.safetensors',
                'sampler_name': 'euler',
                'steps': 20,
                'cfg_scale': 7.0,
                'width': 512,
                'height': 512,
                'seed': 12345,
                'timestamp': '2024-01-01T00:00:00',
                'generation_type': 'txt2img',
                'batch_index': 0
            })
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/reports/validate-csv",
                json={"csv_path": f.name},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['validation']['valid'])
        finally:
            os.unlink(f.name)


def run_integration_tests():
    """Run comprehensive integration tests"""
    print("🧪 Running DreamLayer Report System Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestImageRecord))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All tests passed successfully!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1


def test_manual_report_generation():
    """Manual test for report generation with sample data"""
    print("\n🔧 Manual Report Generation Test")
    print("-" * 40)
    
    try:
        # Create sample environment
        test_dir = tempfile.mkdtemp(prefix="manual_test_")
        served_images_dir = os.path.join(test_dir, "served_images")
        os.makedirs(served_images_dir, exist_ok=True)
        
        # Create sample images
        for i in range(5):
            img_path = os.path.join(served_images_dir, f"sample_{i}.png")
            with open(img_path, 'wb') as f:
                f.write(b"SAMPLE_IMAGE_DATA" * 50)
        
        # Create generator
        class ManualTestGenerator(ReportGenerator):
            def __init__(self):
                self.served_images_dir = served_images_dir
                self.reports_dir = os.path.join(test_dir, "reports")
                self.output_dir = os.path.join(test_dir, "output")
                os.makedirs(self.reports_dir, exist_ok=True)
                os.makedirs(self.output_dir, exist_ok=True)
        
        generator = ManualTestGenerator()
        result = generator.create_report_bundle()
        
        print(f"✅ Manual test completed successfully!")
        print(f"   Report: {result['report_filename']}")
        print(f"   Size: {result['bundle_size_bytes']} bytes")
        print(f"   Images: {result['total_images']}")
        
        return result['report_path']
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")
        return None
    finally:
        # Cleanup
        if 'test_dir' in locals():
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    import sys
    
    # Run integration tests
    exit_code = run_integration_tests()
    
    # Run manual test
    manual_result = test_manual_report_generation()
    
    sys.exit(exit_code)
