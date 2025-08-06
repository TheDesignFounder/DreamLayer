"""
Test batch report generator functionality

Tests the BatchReportGenerator class including CSV schema validation,
ZIP file creation, and deterministic file naming.
"""

import os
import csv
import json
import zipfile
import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from dream_layer_backend_utils import BatchReportGenerator
from dream_layer_backend_utils.batch_report_generator import REQUIRED_CSV_COLUMNS


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_served_images_dir(monkeypatch):
    """Mock the served images directory for testing"""
    temp_dir = tempfile.mkdtemp()
    
    # Create test images
    for i in range(1, 3):
        filename = f'test_image_{i:03d}.png'
        filepath = os.path.join(temp_dir, filename)
        # Create a dummy PNG file (1x1 pixel transparent PNG)
        with open(filepath, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05W\xcd\xc1\x0b\x00\x00\x00\x00IEND\xaeB`\x82')
    
    # Monkey patch the served images directory in the BatchReportGenerator
    def mock_init(self, output_dir=None):
        if output_dir is None:
            self.output_dir = os.path.join(temp_dir, 'reports')
        else:
            self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._served_images_dir = temp_dir  # Store the temp dir
    
    monkeypatch.setattr(BatchReportGenerator, '__init__', mock_init)
    
    # Also patch the _copy_images method to use our temp dir
    original_copy_images = BatchReportGenerator._copy_images
    def mock_copy_images(self, images_data, grids_dir):
        # Use the stored temp dir instead of the default
        served_images_dir = self._served_images_dir
        copied_count = 0
        
        for idx, image_data in enumerate(images_data):
            try:
                original_filename = image_data.get('filename')
                if not original_filename:
                    continue
                    
                src_path = os.path.join(served_images_dir, original_filename)
                grid_filename = f"grid_{idx:04d}_{Path(original_filename).stem}.png"
                dest_path = os.path.join(grids_dir, grid_filename)
                
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied_count += 1
                    
            except Exception as e:
                pass
                
        return copied_count
    
    monkeypatch.setattr(BatchReportGenerator, '_copy_images', mock_copy_images)
    
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_images_data():
    """Sample image data for testing"""
    return [
        {
            'id': 'img_001',
            'filename': 'test_image_001.png',
            'url': 'http://localhost:5001/api/images/test_image_001.png',
            'prompt': 'A beautiful landscape',
            'negativePrompt': 'ugly, blurry',
            'timestamp': 1704067200000,  # 2024-01-01
            'settings': {
                'model': 'sd-v1-5.safetensors',
                'sampler': 'DPM++ 2M Karras',
                'steps': 30,
                'cfg_scale': 7.5,
                'seed': 12345,
                'width': 1024,
                'height': 768
            }
        },
        {
            'id': 'img_002',
            'filename': 'test_image_002.png',
            'url': 'http://localhost:5001/api/images/test_image_002.png',
            'prompt': 'A futuristic city',
            'negativePrompt': 'low quality',
            'timestamp': 1704067800000,
            'settings': {
                'model': 'sdxl-base-1.0.safetensors',
                'sampler': 'Euler a',
                'steps': 25,
                'cfg_scale': 8.0,
                'seed': 54321,
                'width': 1024,
                'height': 1024
            }
        }
    ]


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'session_id': 'test_session_123',
        'generation_date': '2024-01-01T00:00:00Z',
        'total_images': 2,
        'user_settings': {
            'theme': 'dark',
            'auto_save': True
        }
    }


class TestBatchReportGenerator:
    """Test the BatchReportGenerator class"""
    
    def test_initialization(self, temp_output_dir):
        """Test generator initialization"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        assert generator.output_dir == temp_output_dir
        assert os.path.exists(temp_output_dir)
    
    def test_csv_schema_validation(self, temp_output_dir):
        """Test CSV schema validation with required columns"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Create a valid CSV
        csv_path = os.path.join(temp_output_dir, 'test_valid.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=REQUIRED_CSV_COLUMNS + ['grid_path'])
            writer.writeheader()
            writer.writerow({
                'filename': 'test.png',
                'prompt': 'test prompt',
                'negative_prompt': 'test negative',
                'model': 'test_model',
                'sampler': 'test_sampler',
                'steps': 20,
                'cfg_scale': 7.0,
                'seed': 12345,
                'width': 512,
                'height': 512,
                'timestamp': '2024-01-01T00:00:00Z',
                'grid_path': 'grids/grid_0000_test.png'
            })
        
        # Test valid CSV
        assert generator.validate_csv_schema(csv_path) is True
        
        # Create an invalid CSV (missing required column)
        invalid_csv_path = os.path.join(temp_output_dir, 'test_invalid.csv')
        with open(invalid_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['filename', 'prompt'])  # Missing required columns
            writer.writeheader()
        
        # Test invalid CSV
        assert generator.validate_csv_schema(invalid_csv_path) is False
    
    def test_deterministic_file_naming(self, temp_output_dir, sample_images_data):
        """Test that file names are deterministic"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Create temporary CSV to check naming
        csv_path = os.path.join(temp_output_dir, 'test_naming.csv')
        generator._create_csv(csv_path, sample_images_data)
        
        # Read CSV and check grid paths
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert rows[0]['grid_path'] == 'grids/grid_0000_test_image_001.png'
            assert rows[1]['grid_path'] == 'grids/grid_0001_test_image_002.png'
    
    def test_generate_report_creates_zip(self, temp_output_dir, sample_images_data, sample_config):
        """Test that generate_report creates a valid ZIP file"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Generate report
        zip_path = generator.generate_report(
            images_data=sample_images_data,
            config=sample_config,
            report_name='test_report'
        )
        
        # Check ZIP file exists
        assert os.path.exists(zip_path)
        assert zip_path.endswith('test_report.zip')
        
        # Validate ZIP contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            namelist = zipf.namelist()
            
            # Check required files exist
            assert 'results.csv' in namelist
            assert 'config.json' in namelist
            assert 'README.txt' in namelist
            
            # Check CSV content
            csv_content = zipf.read('results.csv').decode('utf-8')
            assert 'test_image_001.png' in csv_content
            assert 'A beautiful landscape' in csv_content
            
            # Check config.json content
            config_content = json.loads(zipf.read('config.json').decode('utf-8'))
            assert 'generation_config' in config_content
            assert 'report_metadata' in config_content
            assert config_content['generation_config']['session_id'] == 'test_session_123'
            
            # Check README content
            readme_content = zipf.read('README.txt').decode('utf-8')
            assert 'DreamLayer Batch Report' in readme_content
            assert 'CSV Schema:' in readme_content
    
    def test_validate_zip_contents(self, temp_output_dir, sample_images_data, sample_config):
        """Test ZIP contents validation"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Create a simple test ZIP with CSV
        zip_path = os.path.join(temp_output_dir, 'test_validation.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Create CSV content
            csv_content = "filename,prompt,negative_prompt,model,sampler,steps,cfg_scale,seed,width,height,timestamp,grid_path\n"
            csv_content += "test.png,prompt,negative,model,sampler,20,7.0,123,512,512,2024-01-01,grids/grid_0000_test.png\n"
            zipf.writestr('results.csv', csv_content)
            
            # Add the referenced grid file
            zipf.writestr('grids/grid_0000_test.png', b'fake image data')
        
        # Should validate successfully
        assert generator.validate_zip_contents(zip_path) is True
        
        # Create ZIP with missing referenced file
        invalid_zip_path = os.path.join(temp_output_dir, 'test_invalid.zip')
        with zipfile.ZipFile(invalid_zip_path, 'w') as zipf:
            # CSV references a file that doesn't exist in ZIP
            csv_content = "filename,prompt,negative_prompt,model,sampler,steps,cfg_scale,seed,width,height,timestamp,grid_path\n"
            csv_content += "test.png,prompt,negative,model,sampler,20,7.0,123,512,512,2024-01-01,grids/missing_file.png\n"
            zipf.writestr('results.csv', csv_content)
        
        # Should fail validation
        assert generator.validate_zip_contents(invalid_zip_path) is False
    
    def test_report_with_empty_images(self, temp_output_dir, sample_config):
        """Test handling of empty image list"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Generate report with empty images
        zip_path = generator.generate_report(
            images_data=[],
            config=sample_config,
            report_name='empty_report'
        )
        
        # Check ZIP still created
        assert os.path.exists(zip_path)
        
        # Check CSV is empty but valid
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            csv_content = zipf.read('results.csv').decode('utf-8')
            lines = csv_content.strip().split('\n')
            assert len(lines) == 1  # Only header
    
    def test_report_name_generation(self, temp_output_dir, sample_images_data, sample_config):
        """Test automatic report name generation when not provided"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Generate without report name
        zip_path = generator.generate_report(
            images_data=sample_images_data,
            config=sample_config
        )
        
        # Check name format
        filename = os.path.basename(zip_path)
        assert filename.startswith('report_')
        assert filename.endswith('.zip')
        # Check timestamp format (YYYYMMDD_HHMMSS)
        timestamp_part = filename[7:-4]  # Remove 'report_' and '.zip'
        assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS
        assert timestamp_part[8] == '_'


class TestBatchReportIntegration:
    """Integration tests for batch report generation"""
    
    def test_full_report_generation_workflow(self, temp_output_dir, sample_images_data, sample_config, mock_served_images_dir):
        """Test the complete workflow from data to validated ZIP"""
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Generate report
        zip_path = generator.generate_report(
            images_data=sample_images_data,
            config=sample_config,
            report_name='integration_test'
        )
        
        # Validate the generated report
        assert os.path.exists(zip_path)
        assert generator.validate_zip_contents(zip_path) is True
        
        # Extract and validate CSV schema
        temp_extract = os.path.join(temp_output_dir, 'extract')
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_extract)
        
        csv_path = os.path.join(temp_extract, 'results.csv')
        assert generator.validate_csv_schema(csv_path) is True
        
        # Verify all components present
        assert os.path.exists(os.path.join(temp_extract, 'config.json'))
        assert os.path.exists(os.path.join(temp_extract, 'README.txt'))
        assert os.path.isdir(os.path.join(temp_extract, 'grids'))
    
    @pytest.mark.parametrize("num_images", [1, 10, 100])
    def test_scalability(self, temp_output_dir, sample_config, num_images):
        """Test report generation with varying numbers of images"""
        # Generate many images
        images_data = []
        for i in range(num_images):
            images_data.append({
                'id': f'img_{i:04d}',
                'filename': f'test_image_{i:04d}.png',
                'url': f'http://localhost:5001/api/images/test_image_{i:04d}.png',
                'prompt': f'Test prompt {i}',
                'negativePrompt': 'negative',
                'timestamp': 1704067200000 + i * 1000,
                'settings': {
                    'model': 'test_model.safetensors',
                    'sampler': 'Euler',
                    'steps': 20,
                    'cfg_scale': 7.0,
                    'seed': 12345 + i,
                    'width': 512,
                    'height': 512
                }
            })
        
        generator = BatchReportGenerator(output_dir=temp_output_dir)
        
        # Generate report
        zip_path = generator.generate_report(
            images_data=images_data,
            config=sample_config,
            report_name=f'scale_test_{num_images}'
        )
        
        # Verify ZIP created and contains correct number of entries
        assert os.path.exists(zip_path)
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            csv_content = zipf.read('results.csv').decode('utf-8')
            lines = csv_content.strip().split('\n')
            assert len(lines) == num_images + 1  # +1 for header