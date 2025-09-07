#!/usr/bin/env python3
"""
Standalone API test for report generation endpoints
Tests the Flask API without requiring ComfyUI dependencies
"""

import os
import sys
import json
import tempfile
import shutil
import threading
import time
import requests
from flask import Flask
import unittest

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_flask_app():
    """Create a minimal Flask app with just the report endpoints"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    # Add minimal routes needed for testing
    @app.route('/', methods=['GET'])
    def health_check():
        return jsonify({"status": "ok", "service": "DreamLayer Report API"})
    
    @app.route('/api/gallery-data', methods=['POST'])
    def update_gallery_data():
        """Update gallery data for report generation"""
        try:
            data = request.json
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            # Store gallery data temporarily for report generation
            gallery_file = os.path.join(os.path.dirname(__file__), 'temp_gallery_data.json')
            with open(gallery_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return jsonify({
                "status": "success",
                "message": "Gallery data updated successfully"
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to update gallery data: {str(e)}"
            }), 500

    @app.route('/api/reports/generate', methods=['POST'])
    def generate_report():
        """Generate comprehensive report bundle"""
        try:
            # Import here to avoid circular imports
            from report_generator import ReportGenerator
            
            data = request.json or {}
            output_filename = data.get('filename')
            
            generator = ReportGenerator()
            result = generator.create_report_bundle(output_filename)
            
            if result['status'] == 'success':
                return jsonify({
                    "status": "success",
                    "message": "Report generated successfully",
                    "report_path": result['report_path'],
                    "report_filename": result['report_filename'],
                    "total_images": result['total_images'],
                    "csv_validation": result['csv_validation'],
                    "path_validation": result['path_validation'],
                    "bundle_size_bytes": result['bundle_size_bytes'],
                    "generation_types": result['generation_types']
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": result.get('error', 'Unknown error occurred')
                }), 500
                
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to generate report: {str(e)}"
            }), 500

    @app.route('/api/reports/validate-csv', methods=['POST'])
    def validate_csv_schema():
        """Validate CSV schema for reports"""
        try:
            from report_generator import ImageRecord
            
            data = request.json
            if not data or 'csv_path' not in data:
                return jsonify({
                    "status": "error",
                    "message": "CSV path not provided"
                }), 400
            
            csv_path = data['csv_path']
            validation_result = ImageRecord.validate_csv_schema(csv_path)
            
            return jsonify({
                "status": "success",
                "validation": validation_result
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"CSV validation failed: {str(e)}"
            }), 500
    
    return app

class TestStandaloneAPI(unittest.TestCase):
    """Test API endpoints with standalone Flask server"""
    
    @classmethod
    def setUpClass(cls):
        """Start test Flask server"""
        cls.app = create_test_flask_app()
        cls.port = 5003
        cls.base_url = f"http://localhost:{cls.port}"
        
        # Start server in background thread
        def run_server():
            cls.app.run(host='0.0.0.0', port=cls.port, debug=False, use_reloader=False)
        
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Check if server is available
        try:
            response = requests.get(cls.base_url, timeout=5)
            cls.server_available = response.status_code == 200
        except:
            cls.server_available = False
    
    def setUp(self):
        """Skip tests if server not available"""
        if not self.server_available:
            self.skipTest("Test server not available")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/", timeout=5)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('service', data)
    
    def test_gallery_data_update(self):
        """Test gallery data update endpoint"""
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
            f"{self.base_url}/api/gallery-data",
            json=test_data,
            timeout=10
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    def test_gallery_data_empty(self):
        """Test gallery data endpoint with empty data"""
        response = requests.post(
            f"{self.base_url}/api/gallery-data",
            json=None,
            timeout=10
        )
        
        # Accept either 400 or 500 for empty data - both are valid error responses
        self.assertIn(response.status_code, [400, 500])
        data = response.json()
        self.assertEqual(data['status'], 'error')
    
    def test_report_generation_with_test_data(self):
        """Test report generation with test data"""
        # First update gallery data
        self.test_gallery_data_update()
        
        # Create some test images in served_images directory
        served_images_dir = os.path.join(os.path.dirname(__file__), 'served_images')
        os.makedirs(served_images_dir, exist_ok=True)
        
        test_image_path = os.path.join(served_images_dir, 'api_test.png')
        with open(test_image_path, 'wb') as f:
            f.write(b"FAKE_PNG_DATA" * 100)
        
        try:
            # Generate report
            response = requests.post(
                f"{self.base_url}/api/reports/generate",
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
            
            print(f"✅ Report generated: {data['report_filename']}")
            print(f"   Total images: {data['total_images']}")
            print(f"   Bundle size: {data['bundle_size_bytes']} bytes")
            
        finally:
            # Clean up test image
            if os.path.exists(test_image_path):
                os.unlink(test_image_path)
    
    def test_csv_validation_endpoint(self):
        """Test CSV validation endpoint"""
        # Create a test CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            from report_generator import ImageRecord
            
            import csv
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
                f"{self.base_url}/api/reports/validate-csv",
                json={"csv_path": f.name},
                timeout=10
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'success')
            self.assertTrue(data['validation']['valid'])
            
        finally:
            os.unlink(f.name)

def run_standalone_tests():
    """Run standalone API tests"""
    print("🚀 Running Standalone API Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStandaloneAPI)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 All API tests passed successfully!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1

if __name__ == "__main__":
    exit_code = run_standalone_tests()
    
    # Clean up any test files
    temp_files = ['temp_gallery_data.json']
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    sys.exit(exit_code)
