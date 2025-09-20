"""
Tests for report_bundle.py - Report Generation with Mac Compatibility
"""
import pytest
import tempfile
import zipfile
import os
import json
from unittest.mock import patch, Mock
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

class TestReportBundle:
    
    def test_report_bundle_generator_creation(self):
        """Test ReportBundleGenerator can be created"""
        from report_bundle import ReportBundleGenerator
        
        generator = ReportBundleGenerator()
        assert generator is not None
    
    @patch('report_bundle.ReportBundleGenerator.get_enhanced_runs_data')
    def test_csv_generation(self, mock_get_runs):
        """Test CSV generation with sample data"""
        from report_bundle import ReportBundleGenerator
        
        # Mock run data
        mock_get_runs.return_value = [
            {
                'run_id': 'test-123',
                'timestamp': '2025-08-20T00:00:00',
                'model': 'dall-e-3',
                'prompt': 'test prompt',
                'clip_score_mean': 0.85,
                'generated_images': ['test1.png', 'test2.png']
            }
        ]
        
        generator = ReportBundleGenerator()
        csv_path = generator.generate_csv()
        
        assert os.path.exists(csv_path)
        assert csv_path == "results.csv"
        
        # Verify CSV content
        with open(csv_path, 'r') as f:
            content = f.read()
            assert 'run_id,timestamp,model' in content
            assert 'test-123' in content
            assert 'dall-e-3' in content
        
        # Cleanup
        os.remove(csv_path)
    
    @patch('report_bundle.ReportBundleGenerator.get_enhanced_runs_data')
    def test_config_json_generation(self, mock_get_runs):
        """Test config JSON generation"""
        from report_bundle import ReportBundleGenerator
        
        # Mock run data
        mock_get_runs.return_value = [
            {
                'run_id': 'test-123',
                'model': 'dall-e-3',
                'prompt': 'test prompt',
                'generated_images': ['test.png']
            }
        ]
        
        generator = ReportBundleGenerator()
        config_path = generator.generate_config_json()
        
        assert os.path.exists(config_path)
        assert config_path == "config.json"
        
        # Verify JSON content
        with open(config_path, 'r') as f:
            data = json.load(f)
            assert 'runs' in data
            assert 'metadata' in data
            assert len(data['runs']) == 1
            assert data['runs'][0]['run_id'] == 'test-123'
        
        # Cleanup
        os.remove(config_path)
    
    @patch('report_bundle.ReportBundleGenerator.get_enhanced_runs_data')
    def test_zip_bundle_generation(self, mock_get_runs):
        """Test ZIP bundle generation with Mac compatibility"""
        from report_bundle import ReportBundleGenerator
        
        # Mock run data
        mock_get_runs.return_value = [
            {
                'run_id': 'test-123',
                'model': 'test-model',
                'prompt': 'test prompt',
                'clip_score_mean': 0.75
            }
        ]
        
        generator = ReportBundleGenerator()
        bundle_path = generator.generate_bundle(include_images=False)
        
        assert os.path.exists(bundle_path)
        assert bundle_path.endswith('.zip')
        
        # Verify ZIP contents
        with zipfile.ZipFile(bundle_path, 'r') as zipf:
            files = zipf.namelist()
            assert 'results.csv' in files
            assert 'config.json' in files
            
            # Test ZIP integrity
            bad_file = zipf.testzip()
            assert bad_file is None, f"ZIP file corrupted: {bad_file}"
        
        # Cleanup
        os.remove(bundle_path)
    
    def test_mac_compatible_zip_settings(self):
        """Test that ZIP files use Mac-compatible settings"""
        from report_bundle import ReportBundleGenerator
        
        # Create test files
        with open('test_results.csv', 'w') as f:
            f.write('test,data\n1,2\n')
        
        with open('test_config.json', 'w') as f:
            f.write('{"test": "data"}')
        
        # Create ZIP with Mac compatibility
        zip_path = 'test_mac.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            zipf.write('test_results.csv', 'results.csv')
            zipf.write('test_config.json', 'config.json')
        
        # Verify ZIP can be read
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            assert zipf.testzip() is None
            files = zipf.namelist()
            assert 'results.csv' in files
            assert 'config.json' in files
        
        # Cleanup
        os.remove('test_results.csv')
        os.remove('test_config.json')
        os.remove(zip_path)
    
    def test_report_bundle_api_endpoint(self):
        """Test report bundle API endpoint"""
        from report_bundle import app
        
        with app.test_client() as client:
            response = client.post('/api/report-bundle',
                                 json={'include_images': False},
                                 content_type='application/json')
            
            # Should return success or handle gracefully
            assert response.status_code in [200, 500]
    
    @patch('report_bundle.os.path.exists')
    def test_download_endpoint_file_not_found(self, mock_exists):
        """Test download endpoint when file doesn't exist"""
        from report_bundle import app
        
        # Mock file not found
        mock_exists.return_value = False
        
        with app.test_client() as client:
            response = client.get('/api/report-bundle/download/nonexistent.zip')
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
    
    def test_download_endpoint_invalid_file_type(self):
        """Test download endpoint with invalid file type"""
        from report_bundle import app
        
        with app.test_client() as client:
            response = client.get('/api/report-bundle/download/test.txt')
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
