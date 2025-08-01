import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from preset_manager import PresetManager
from dream_layer import app

class TestPresetSystem:
    @pytest.fixture
    def preset_manager(self):
        """Create a temporary preset manager for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            manager = PresetManager(temp_file)
            yield manager
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_create_preset(self, preset_manager):
        """Test creating a new preset"""
        settings = {
            "prompt": "test prompt",
            "negative_prompt": "test negative",
            "model_name": "test_model.safetensors",
            "sampler_name": "euler",
            "scheduler": "normal",
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "batch_size": 1,
            "batch_count": 1,
            "seed": -1,
            "random_seed": True
        }
        
        preset = preset_manager.create_preset(
            name="Test Preset",
            description="A test preset",
            settings=settings
        )
        
        assert preset.name == "Test Preset"
        assert preset.description == "A test preset"
        assert preset.settings == settings
        assert preset.hash is not None
        assert preset.version == "1.0.0"
        assert preset.is_default == False

    def test_select_and_apply_preset(self, preset_manager):
        """Test selecting a preset and applying its settings"""
        # Create a preset
        settings = {
            "prompt": "selected prompt",
            "negative_prompt": "selected negative",
            "model_name": "selected_model.safetensors",
            "sampler_name": "dpm++",
            "scheduler": "karras",
            "steps": 30,
            "cfg_scale": 8.0,
            "width": 1024,
            "height": 1024,
            "batch_size": 2,
            "batch_count": 3,
            "seed": 12345,
            "random_seed": False
        }
        
        preset = preset_manager.create_preset(
            name="Selected Preset",
            description="A preset to select",
            settings=settings
        )
        
        # Verify preset can be retrieved
        retrieved_preset = preset_manager.get_preset(preset.id)
        assert retrieved_preset is not None
        assert retrieved_preset.name == "Selected Preset"
        assert retrieved_preset.settings == settings

    def test_preset_hash_validation(self, preset_manager):
        """Test that preset hash validation works correctly"""
        settings = {
            "prompt": "hash test",
            "model_name": "test_model.safetensors",
            "steps": 20,
            "cfg_scale": 7.0
        }
        
        preset = preset_manager.create_preset(
            name="Hash Test Preset",
            settings=settings
        )
        
        # Test with same settings (should be valid)
        is_valid = preset_manager.validate_preset_hash(preset.id, settings)
        assert is_valid == True
        
        # Test with different settings (should be invalid)
        modified_settings = settings.copy()
        modified_settings["steps"] = 30
        is_valid = preset_manager.validate_preset_hash(preset.id, modified_settings)
        assert is_valid == False

    def test_preset_api_endpoints(self, client):
        """Test preset API endpoints"""
        # Test GET /api/presets
        response = client.get('/api/presets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'presets' in data

        # Test POST /api/presets (create)
        preset_data = {
            "name": "API Test Preset",
            "description": "Created via API",
            "settings": {
                "prompt": "api test",
                "model_name": "api_model.safetensors",
                "steps": 25,
                "cfg_scale": 7.5
            }
        }
        
        response = client.post('/api/presets', 
                             data=json.dumps(preset_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['preset']['name'] == "API Test Preset"
        
        preset_id = data['preset']['id']
        
        # Test GET /api/presets/<id>
        response = client.get(f'/api/presets/{preset_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['preset']['id'] == preset_id

        # Test PUT /api/presets/<id> (update)
        update_data = {
            "name": "Updated API Test Preset",
            "settings": {
                "prompt": "updated api test",
                "model_name": "updated_api_model.safetensors",
                "steps": 30,
                "cfg_scale": 8.0
            }
        }
        
        response = client.put(f'/api/presets/{preset_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['preset']['name'] == "Updated API Test Preset"

        # Test DELETE /api/presets/<id>
        response = client.delete(f'/api/presets/{preset_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    @patch('dream_layer.preset_manager')
    def test_generation_with_preset_info(self, mock_preset_manager, client):
        """Test that generation includes preset information in metadata"""
        # Mock preset manager to return a test preset
        mock_preset = MagicMock()
        mock_preset.id = "test-preset-123"
        mock_preset.name = "Test Generation Preset"
        mock_preset.version = "1.0.0"
        mock_preset.hash = "abc123hash"
        
        mock_preset_manager.get_preset.return_value = mock_preset
        
        # Mock the generation workflow to capture preset info
        with patch('dream_layer.txt2img_workflow.transform_to_txt2img_workflow') as mock_transform:
            mock_transform.return_value = {
                "prompt": {"1": {"class_type": "TestNode"}},
                "meta": {"preset": {"id": "test-preset-123", "name": "Test Generation Preset"}}
            }
            
            # Test generation request with preset info
            generation_data = {
                "prompt": "test generation",
                "model_name": "test_model.safetensors",
                "steps": 20,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 512,
                "preset_info": {
                    "id": "test-preset-123",
                    "name": "Test Generation Preset",
                    "version": "1.0.0",
                    "hash": "abc123hash"
                }
            }
            
            response = client.post('/api/generate',
                                data=json.dumps(generation_data),
                                content_type='application/json')
            
            # Verify that preset info was passed to workflow transformation
            mock_transform.assert_called_once()
            call_args = mock_transform.call_args[0][0]
            assert 'preset_info' in call_args
            assert call_args['preset_info']['id'] == "test-preset-123"
            assert call_args['preset_info']['name'] == "Test Generation Preset"

    def test_default_presets_initialization(self, preset_manager):
        """Test that default presets are created on initialization"""
        presets = preset_manager.get_all_presets()
        
        # Should have default presets
        assert len(presets) >= 3
        
        # Check for specific default presets
        preset_names = [p.name for p in presets]
        assert "SDXL Base" in preset_names
        assert "Base + Refiner" in preset_names
        assert "Fast Generation" in preset_names
        
        # Verify default presets are marked as default
        default_presets = [p for p in presets if p.is_default]
        assert len(default_presets) >= 3

    def test_preset_version_pinning(self, preset_manager):
        """Test that preset version pinning works correctly"""
        # Create a preset with specific settings
        original_settings = {
            "prompt": "version test",
            "model_name": "version_model.safetensors",
            "steps": 20,
            "cfg_scale": 7.0
        }
        
        preset = preset_manager.create_preset(
            name="Version Test Preset",
            settings=original_settings
        )
        
        original_hash = preset.hash
        original_version = preset.version
        
        # Update the preset with new settings
        updated_settings = original_settings.copy()
        updated_settings["steps"] = 30
        
        updated_preset = preset_manager.update_preset(
            preset.id,
            settings=updated_settings
        )
        
        # Hash should change when settings change
        assert updated_preset.hash != original_hash
        
        # Version should remain the same (version pinning)
        assert updated_preset.version == original_version

if __name__ == "__main__":
    pytest.main([__file__]) 