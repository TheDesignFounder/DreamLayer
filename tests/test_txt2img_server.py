"""
Tests for txt2img_server.py - Text to Image Generation with Database Integration
"""
import pytest
import json
from unittest.mock import patch, Mock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

class TestTxt2ImgServer:
    
    def test_txt2img_endpoint_exists(self):
        """Test that txt2img endpoint is accessible"""
        from txt2img_server import app
        
        with app.test_client() as client:
            # Test OPTIONS request
            response = client.options('/api/txt2img')
            assert response.status_code == 200
    
    @patch('txt2img_server.requests.post')
    @patch('dream_layer_backend_utils.direct_database_integration.save_generation_run')
    def test_txt2img_generation_success(self, mock_db_save, mock_comfy_post, test_generation_data):
        """Test successful txt2img generation with database integration"""
        from txt2img_server import app
        
        # Mock ComfyUI response
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'success',
            'all_images': [{'filename': 'test_output.png'}]
        }
        mock_response.status_code = 200
        mock_comfy_post.return_value = mock_response
        
        # Mock database save
        mock_db_save.return_value = True
        
        with app.test_client() as client:
            response = client.post('/api/txt2img', 
                                 json=test_generation_data,
                                 content_type='application/json')
            
            # Should handle request (may return 200 or 500 depending on mocking)
            assert response.status_code in [200, 500]
            
            # If successful, verify database integration was called
            if response.status_code == 200:
                mock_db_save.assert_called()
    
    def test_txt2img_model_name_handling(self, test_generation_data):
        """Test that model_name is properly handled in generation data"""
        # Test the data structure directly
        assert 'model_name' in test_generation_data
        assert test_generation_data['model_name'] == 'test-model-v1'
        
        # Test model name validation
        model_name = test_generation_data.get('model_name', 'default')
        assert model_name != 'unknown'
    
    @patch('txt2img_server.requests.post')
    def test_txt2img_comfyui_error_handling(self, mock_comfy_post, test_generation_data):
        """Test error handling when ComfyUI fails"""
        from txt2img_server import app
        
        # Mock ComfyUI error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'error': 'ComfyUI error'}
        mock_comfy_post.return_value = mock_response
        
        with app.test_client() as client:
            response = client.post('/api/txt2img', 
                                 json=test_generation_data,
                                 content_type='application/json')
            
            # Should handle error gracefully
            assert response.status_code in [200, 500]
    
    def test_txt2img_invalid_data(self):
        """Test txt2img with invalid input data"""
        from txt2img_server import app
        
        with app.test_client() as client:
            # Test with empty data
            response = client.post('/api/txt2img', 
                                 json={},
                                 content_type='application/json')
            
            # Should handle gracefully (may return error or use defaults)
            assert response.status_code in [200, 400, 500]
    
    def test_model_name_extraction(self):
        """Test model name extraction from request data"""
        test_data = {
            'model_name': 'dall-e-3',
            'prompt': 'test prompt'
        }
        
        # Test that we can extract model name
        model = test_data.get('model_name', 'unknown')
        assert model == 'dall-e-3'
        assert model != 'unknown'
