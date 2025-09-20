"""
Shared test fixtures for DreamLayer backend tests
Following ComfyUI testing patterns
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def mock_file():
    """Mock file object for upload testing"""
    mock = Mock()
    mock.filename = "test_model.safetensors"
    mock.content_type = "application/octet-stream"
    return mock


@pytest.fixture
def mock_file_with_extension():
    """Factory fixture for creating mock files with specific extensions"""
    def _create_mock_file(filename: str):
        mock = Mock()
        mock.filename = filename
        mock.content_type = "application/octet-stream"
        return mock
    return _create_mock_file


@pytest.fixture
def temp_model_dir():
    """Temporary directory for model testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create model subdirectories
        for model_type in ['checkpoints', 'loras', 'controlnet', 'upscale_models']:
            os.makedirs(os.path.join(temp_dir, model_type), exist_ok=True)
        yield temp_dir


@pytest.fixture
def sample_model_files():
    """Sample model files for testing"""
    return {
        'valid_safetensors': 'model.safetensors',
        'valid_ckpt': 'model.ckpt',
        'valid_pth': 'model.pth',
        'valid_pt': 'model.pt',
        'valid_bin': 'model.bin',
        'invalid_txt': 'model.txt',
        'invalid_pkl': 'model.pkl',
        'no_extension': 'model',
        'uppercase': 'MODEL.SAFETENSORS',
        'mixed_case': 'Model.CkPt'
    }


@pytest.fixture
def expected_extensions():
    """Expected supported extensions"""
    return {'.safetensors', '.ckpt', '.pth', '.pt', '.bin'}


@pytest.fixture
def mock_comfyui_models_dir(temp_model_dir):
    """Mock ComfyUI models directory structure"""
    models_dir = os.path.join(temp_model_dir, 'ComfyUI', 'models')
    
    # Create model type directories
    model_types = ['checkpoints', 'loras', 'controlnet', 'upscale_models', 'vae', 'embeddings', 'hypernetworks']
    for model_type in model_types:
        os.makedirs(os.path.join(models_dir, model_type), exist_ok=True)
    
    return models_dir
