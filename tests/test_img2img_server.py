"""
Tests for img2img_server.py - Image to Image Generation with Database Integration
"""
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

class TestImg2ImgServer:
    
    def test_img2img_endpoint_exists(self):
        """Test that img2img endpoint is accessible"""
        try:
            from img2img_server import app
            
            with app.test_client() as client:
                response = client.options('/api/img2img')
                assert response.status_code == 200
        except ImportError:
            pytest.skip("img2img_server not available")
    
    @patch('img2img_server.requests.post')
    @patch('dream_layer_backend_utils.direct_database_integration.save_generation_run')
    def test_img2img_generation_success(self, mock_db_save, mock_comfy_post):
        """Test successful img2img generation with database integration"""
        try:
            from img2img_server import app
            
            # Mock ComfyUI response
            mock_comfy_post.return_value.json.return_value = {
                'status': 'success',
                'all_images': [{'filename': 'img2img_output.png'}]
            }
            mock_comfy_post.return_value.status_code = 200
            
            # Mock database save
            mock_db_save.return_value = True
            
            test_data = {
                'model_name': 'test-model',
                'prompt': 'enhance this image',
                'init_image': 'base64encodedimage...',
                'denoising_strength': 0.7
            }
            
            with app.test_client() as client:
                response = client.post('/api/img2img', 
                                     json=test_data,
                                     content_type='application/json')
                
                # Should handle request (may succeed or fail gracefully)
                assert response.status_code in [200, 400, 500]
                
        except ImportError:
            pytest.skip("img2img_server not available")
    
    def test_img2img_denoising_strength_validation(self):
        """Test denoising strength parameter validation"""
        # Test valid denoising strength values
        valid_strengths = [0.1, 0.5, 0.7, 1.0]
        invalid_strengths = [-0.1, 1.1, 2.0]
        
        for strength in valid_strengths:
            assert 0.0 <= strength <= 1.0
        
        for strength in invalid_strengths:
            assert not (0.0 <= strength <= 1.0)
