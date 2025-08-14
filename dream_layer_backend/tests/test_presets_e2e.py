"""
End-to-end tests for Presets functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.presets import (
    Preset, PresetManager, get_preset_manager,
    load_presets, save_presets, compute_preset_hash
)


class TestPresetsE2E:
    """End-to-end test cases for presets functionality."""
    
    @pytest.fixture
    def temp_presets_file(self):
        """Create a temporary presets file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            presets_path = Path(temp_file.name)
        
        try:
            yield presets_path
        finally:
            presets_path.unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_config(self):
        """Sample generation configuration."""
        return {
            "model_name": "test_model.safetensors",
            "vae_name": "test_vae.safetensors",
            "steps": 20,
            "cfg_scale": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "width": 512,
            "height": 512,
            "batch_size": 1,
            "seed": 42
        }
    
    def test_preset_creation_and_application(self, temp_presets_file, sample_config):
        """Test creating a preset and applying it to a config."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Create preset from config
        preset = manager.create_preset_from_config(
            name="test_preset",
            config=sample_config,
            description="Test preset for E2E testing"
        )
        
        # Verify preset was created
        assert preset.name == "test_preset"
        assert preset.preset_hash is not None
        assert preset.params["steps"] == 20
        assert preset.params["cfg_scale"] == 7.0
        assert preset.models["model_name"] == "test_model.safetensors"
        
        # Apply preset to a new config
        new_config = {"seed": 100}  # Minimal config
        updated_config = manager.apply_preset_to_config("test_preset", new_config)
        
        # Verify preset was applied
        assert updated_config["preset_name"] == "test_preset"
        assert updated_config["preset_hash"] == preset.preset_hash
        assert updated_config["steps"] == 20
        assert updated_config["cfg_scale"] == 7.0
        assert updated_config["model_name"] == "test_model.safetensors"
        assert updated_config["seed"] == 100  # Original value preserved
        
        # Verify preset is in manager
        assert "test_preset" in manager.list_presets()
        assert manager.get_preset("test_preset") is not None
    
    def test_preset_hash_stability(self, temp_presets_file):
        """Test that preset hashes are stable across runs."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Create preset with specific configuration
        config = {
            "model_name": "stable_model.safetensors",
            "steps": 25,
            "cfg_scale": 8.0,
            "sampler_name": "dpmpp_2m",
            "width": 1024,
            "height": 1024
        }
        
        preset1 = manager.create_preset_from_config("stable_preset", config)
        hash1 = preset1.preset_hash
        
        # Create another preset with same config
        preset2 = manager.create_preset_from_config("stable_preset2", config)
        hash2 = preset2.preset_hash
        
        # Hashes should be identical for identical configs
        assert hash1 == hash2
        
        # Verify hash computation function
        computed_hash = compute_preset_hash(preset1.to_dict())
        assert computed_hash == hash1
    
    def test_preset_versioning(self, temp_presets_file):
        """Test preset version management."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
                # Create initial preset
        config = {"steps": 20, "cfg_scale": 7.0}
        preset1 = manager.create_preset_from_config("versioned_preset", config)
        assert preset1.version == 1
        original_hash = preset1.preset_hash

        # Update preset with new params
        preset1.update(params={"steps": 30, "cfg_scale": 8.0})
        manager.add_preset(preset1)

        # Verify params were updated
        updated_preset = manager.get_preset("versioned_preset")
        assert updated_preset.params["steps"] == 30
        assert updated_preset.params["cfg_scale"] == 8.0

        # Hash should have changed due to params update
        assert updated_preset.preset_hash != original_hash
    
    def test_preset_compatibility(self, temp_presets_file):
        """Test preset compatibility checking."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Create two presets
        config1 = {"steps": 20, "cfg_scale": 7.0}
        config2 = {"steps": 20, "cfg_scale": 7.0}
        
        preset1 = manager.create_preset_from_config("compat_preset1", config1)
        preset2 = manager.create_preset_from_config("compat_preset2", config2)
        
        # Presets with same config should be compatible
        assert preset1.is_compatible_with(preset2)
        
        # Update one preset with different params
        preset1.update(params={"steps": 30, "cfg_scale": 8.0})
        assert not preset1.is_compatible_with(preset2)
    
    def test_preset_validation(self, temp_presets_file):
        """Test preset validation functionality."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Create valid preset
        config = {"model_name": "valid_model.safetensors", "steps": 20}
        preset = manager.create_preset_from_config("valid_preset", config)
        
        # Validate preset
        validation = manager.validate_preset("valid_preset")
        assert validation["valid"] is True
        assert validation["hash_valid"] is True
        assert len(validation["missing_models"]) == 0
        
        # Test validation of non-existent preset
        validation = manager.validate_preset("nonexistent_preset")
        assert validation["valid"] is False
        assert "Preset not found" in validation["error"]
    
    def test_preset_persistence(self, temp_presets_file):
        """Test that presets are properly saved and loaded."""
        # Create preset manager and add presets
        manager = PresetManager(temp_presets_file)
        
        configs = [
            {"steps": 20, "cfg_scale": 7.0},
            {"steps": 50, "cfg_scale": 8.0},
            {"steps": 10, "cfg_scale": 6.0}
        ]
        
        for i, config in enumerate(configs):
            manager.create_preset_from_config(f"persistent_preset_{i}", config)
        
        # Verify presets were saved (3 new + 3 default presets)
        assert len(manager.list_presets()) == 6
        
        # Create new manager instance to test loading
        new_manager = PresetManager(temp_presets_file)
        
        # Verify presets were loaded (3 new + 3 default presets)
        assert len(new_manager.list_presets()) == 6
        for i in range(3):
            preset_name = f"persistent_preset_{i}"
            assert preset_name in new_manager.list_presets()
            
            # Verify preset content
            preset = new_manager.get_preset(preset_name)
            assert preset.params["steps"] == configs[i]["steps"]
            assert preset.params["cfg_scale"] == configs[i]["cfg_scale"]
    
    def test_preset_removal(self, temp_presets_file):
        """Test preset removal functionality."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Add preset
        config = {"steps": 20, "cfg_scale": 7.0}
        manager.create_preset_from_config("removable_preset", config)
        
        # Verify preset exists
        assert "removable_preset" in manager.list_presets()
        
        # Remove preset
        success = manager.remove_preset("removable_preset")
        assert success is True
        
        # Verify preset was removed
        assert "removable_preset" not in manager.list_presets()
        assert manager.get_preset("removable_preset") is None
        
        # Test removing non-existent preset
        success = manager.remove_preset("nonexistent_preset")
        assert success is False
    
    def test_global_preset_manager(self):
        """Test global preset manager functionality."""
        # Get global manager
        manager = get_preset_manager()
        
        # Verify it's a PresetManager instance
        assert isinstance(manager, PresetManager)
        
        # Verify it has default presets
        presets = manager.list_presets()
        assert len(presets) > 0
        assert "default" in presets
    
    def test_load_save_presets_functions(self, temp_presets_file):
        """Test load_presets and save_presets utility functions."""
        # Create some presets
        presets_data = {
            "test_preset1": Preset(
                name="test_preset1",
                params={"steps": 20, "cfg_scale": 7.0}
            ),
            "test_preset2": Preset(
                name="test_preset2",
                params={"steps": 50, "cfg_scale": 8.0}
            )
        }
        
        # Save presets
        save_presets(temp_presets_file, presets_data)
        
        # Load presets
        loaded_presets = load_presets(temp_presets_file)
        
        # Verify presets were loaded correctly
        assert len(loaded_presets) == 2
        assert "test_preset1" in loaded_presets
        assert "test_preset2" in loaded_presets
        
        # Verify preset content
        preset1 = loaded_presets["test_preset1"]
        assert preset1.params["steps"] == 20
        assert preset1.params["cfg_scale"] == 7.0
    
    def test_preset_with_advanced_config(self, temp_presets_file):
        """Test preset creation with advanced configuration options."""
        # Create preset manager
        manager = PresetManager(temp_presets_file)
        
        # Advanced config with various parameter types
        advanced_config = {
            "model_name": "advanced_model.safetensors",
            "vae_name": "advanced_vae.safetensors",
            "lora_name": "advanced_lora.safetensors",
            "controlnet_model": "advanced_controlnet.safetensors",
            "steps": 30,
            "cfg_scale": 8.5,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "width": 1024,
            "height": 1024,
            "batch_size": 2,
            "seed": 12345,
            "denoising_strength": 0.75,
            "tile_size": 512,
            "tile_overlap": 64
        }
        
        # Create preset
        preset = manager.create_preset_from_config("advanced_preset", advanced_config)
        
        # Verify all parameters were captured
        assert preset.models["model_name"] == "advanced_model.safetensors"
        assert preset.models["vae_name"] == "advanced_vae.safetensors"
        assert preset.models["lora_name"] == "advanced_lora.safetensors"
        assert preset.models["controlnet_model"] == "advanced_controlnet.safetensors"
        
        assert preset.params["steps"] == 30
        assert preset.params["cfg_scale"] == 8.5
        assert preset.params["sampler_name"] == "dpmpp_2m"
        assert preset.params["width"] == 1024
        assert preset.params["tile_size"] == 512
        assert preset.params["tile_overlap"] == 64
        
        # Apply preset to minimal config
        minimal_config = {"prompt": "test prompt"}
        updated_config = manager.apply_preset_to_config("advanced_preset", minimal_config)
        
        # Verify preset was applied
        assert updated_config["preset_name"] == "advanced_preset"
        assert updated_config["preset_hash"] == preset.preset_hash
        assert updated_config["steps"] == 30
        assert updated_config["width"] == 1024
        assert updated_config["prompt"] == "test prompt"  # Original preserved
