"""
Pytest configuration and shared fixtures for DreamLayer tests
"""
import pytest
import tempfile
import os
import sys
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Setup test database
    os.environ['TEST_DB_PATH'] = db_path
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def mock_comfyui():
    """Mock ComfyUI responses"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            'status': 'success',
            'all_images': [
                {'filename': 'test_image_001.png'},
                {'filename': 'test_image_002.png'}
            ]
        }
        yield mock_post

@pytest.fixture
def test_generation_data():
    """Sample generation data for testing"""
    return {
        'model_name': 'test-model-v1',
        'prompt': 'beautiful sunset over mountains',
        'negative_prompt': 'blurry, low quality',
        'seed': 12345,
        'steps': 20,
        'cfg_scale': 7.0,
        'width': 512,
        'height': 512,
        'batch_size': 1,
        'batch_count': 1
    }

@pytest.fixture
def mock_clip_calculator():
    """Mock CLIP calculator for testing"""
    mock_calc = Mock()
    mock_calc.compute_clip_score.return_value = 0.85
    return mock_calc
