import pytest
import json
import tempfile
import os
from datetime import datetime
from run_registry import RunConfig, RunRegistry, create_run_config_from_generation_data

class TestRunRegistry:
    """Test cases for the Run Registry functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.registry = RunRegistry(self.temp_file.name)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_required_keys_exist(self):
        """Test that RunConfig has all required keys"""
        # Create a minimal run config with all required fields
        config = RunConfig(
            run_id="test-run-123",
            timestamp=datetime.now().isoformat(),
            model="test-model.safetensors",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="test prompt",
            negative_prompt="test negative",
            seed=12345,
            sampler="euler",
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            batch_size=1,
            batch_count=1,
            workflow={},
            version="1.0.0",
            generated_images=[],
            generation_type="txt2img"
        )
        
        # Assert all required keys exist
        required_keys = [
            'run_id', 'timestamp', 'model', 'vae', 'loras', 'controlnets',
            'prompt', 'negative_prompt', 'seed', 'sampler', 'steps', 'cfg_scale',
            'width', 'height', 'batch_size', 'batch_count', 'workflow', 'version',
            'generated_images', 'generation_type'
        ]
        
        for key in required_keys:
            assert hasattr(config, key), f"Missing required key: {key}"
    
    def test_empty_values_handled(self):
        """Test that empty values are handled without crashes"""
        # Test with empty strings and None values
        config = RunConfig(
            run_id="",
            timestamp="",
            model="",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="",
            negative_prompt="",
            seed=0,
            sampler="",
            steps=0,
            cfg_scale=0.0,
            width=0,
            height=0,
            batch_size=0,
            batch_count=0,
            workflow={},
            version="",
            generated_images=[],
            generation_type=""
        )
        
        # Should not crash when accessing any field
        assert config.run_id == ""
        assert config.prompt == ""
        assert config.negative_prompt == ""
        assert config.model == ""
        assert config.vae is None
        assert config.loras == []
        assert config.controlnets == []
        assert config.seed == 0
        assert config.sampler == ""
        assert config.steps == 0
        assert config.cfg_scale == 0.0
        assert config.width == 0
        assert config.height == 0
        assert config.batch_size == 0
        assert config.batch_count == 0
        assert config.workflow == {}
        assert config.version == ""
        assert config.generated_images == []
        assert config.generation_type == ""
    
    def test_create_run_config_from_generation_data(self):
        """Test creating run config from generation data"""
        # Test with minimal data
        generation_data = {
            'prompt': 'test prompt',
            'negative_prompt': 'test negative',
            'model_name': 'test-model.safetensors',
            'seed': 12345,
            'sampler_name': 'euler',
            'steps': 20,
            'cfg_scale': 7.0,
            'width': 512,
            'height': 512,
            'batch_size': 1,
            'batch_count': 1
        }
        
        generated_images = ['test-image-1.png', 'test-image-2.png']
        
        config = create_run_config_from_generation_data(
            generation_data, generated_images, "txt2img"
        )
        
        # Assert required keys exist
        assert hasattr(config, 'run_id')
        assert hasattr(config, 'timestamp')
        assert hasattr(config, 'model')
        assert hasattr(config, 'prompt')
        assert hasattr(config, 'negative_prompt')
        assert hasattr(config, 'seed')
        assert hasattr(config, 'sampler')
        assert hasattr(config, 'steps')
        assert hasattr(config, 'cfg_scale')
        assert hasattr(config, 'width')
        assert hasattr(config, 'height')
        assert hasattr(config, 'batch_size')
        assert hasattr(config, 'batch_count')
        assert hasattr(config, 'workflow')
        assert hasattr(config, 'version')
        assert hasattr(config, 'generated_images')
        assert hasattr(config, 'generation_type')
        
        # Assert values are set correctly
        assert config.prompt == 'test prompt'
        assert config.negative_prompt == 'test negative'
        assert config.model == 'test-model.safetensors'
        assert config.seed == 12345
        assert config.sampler == 'euler'
        assert config.steps == 20
        assert config.cfg_scale == 7.0
        assert config.width == 512
        assert config.height == 512
        assert config.batch_size == 1
        assert config.batch_count == 1
        assert config.generated_images == generated_images
        assert config.generation_type == 'txt2img'
    
    def test_create_run_config_with_empty_data(self):
        """Test creating run config with empty/missing data"""
        # Test with minimal/empty data
        generation_data = {}
        generated_images = []
        
        config = create_run_config_from_generation_data(
            generation_data, generated_images, "img2img"
        )
        
        # Should not crash and should have default values
        assert config.prompt == ''
        assert config.negative_prompt == ''
        assert config.model == 'unknown'
        assert config.seed == 0
        assert config.sampler == 'euler'
        assert config.steps == 20
        assert config.cfg_scale == 7.0
        assert config.width == 512
        assert config.height == 512
        assert config.batch_size == 1
        assert config.batch_count == 1
        assert config.generated_images == []
        assert config.generation_type == 'img2img'
    
    def test_registry_save_and_load(self):
        """Test that registry can save and load runs"""
        # Create a test run
        config = RunConfig(
            run_id="test-run-123",
            timestamp=datetime.now().isoformat(),
            model="test-model.safetensors",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="test prompt",
            negative_prompt="test negative",
            seed=12345,
            sampler="euler",
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            batch_size=1,
            batch_count=1,
            workflow={},
            version="1.0.0",
            generated_images=[],
            generation_type="txt2img"
        )
        
        # Add to registry
        self.registry.add_run(config)
        
        # Create new registry instance to test loading
        new_registry = RunRegistry(self.temp_file.name)
        
        # Should load the saved run
        loaded_run = new_registry.get_run("test-run-123")
        assert loaded_run is not None
        assert loaded_run.run_id == "test-run-123"
        assert loaded_run.prompt == "test prompt"
        assert loaded_run.model == "test-model.safetensors"
    
    def test_registry_get_all_runs(self):
        """Test getting all runs"""
        # Add multiple runs
        config1 = RunConfig(
            run_id="test-run-1",
            timestamp="2023-01-01T00:00:00",
            model="model1.safetensors",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="prompt 1",
            negative_prompt="",
            seed=1,
            sampler="euler",
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            batch_size=1,
            batch_count=1,
            workflow={},
            version="1.0.0",
            generated_images=[],
            generation_type="txt2img"
        )
        
        config2 = RunConfig(
            run_id="test-run-2",
            timestamp="2023-01-02T00:00:00",
            model="model2.safetensors",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="prompt 2",
            negative_prompt="",
            seed=2,
            sampler="euler",
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            batch_size=1,
            batch_count=1,
            workflow={},
            version="1.0.0",
            generated_images=[],
            generation_type="img2img"
        )
        
        self.registry.add_run(config1)
        self.registry.add_run(config2)
        
        # Get all runs (should be sorted by timestamp, newest first)
        all_runs = self.registry.get_all_runs()
        assert len(all_runs) == 2
        assert all_runs[0].run_id == "test-run-2"  # Newer timestamp
        assert all_runs[1].run_id == "test-run-1"  # Older timestamp
    
    def test_registry_delete_run(self):
        """Test deleting a run"""
        config = RunConfig(
            run_id="test-run-to-delete",
            timestamp=datetime.now().isoformat(),
            model="test-model.safetensors",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="test prompt",
            negative_prompt="",
            seed=12345,
            sampler="euler",
            steps=20,
            cfg_scale=7.0,
            width=512,
            height=512,
            batch_size=1,
            batch_count=1,
            workflow={},
            version="1.0.0",
            generated_images=[],
            generation_type="txt2img"
        )
        
        self.registry.add_run(config)
        
        # Verify run exists
        assert self.registry.get_run("test-run-to-delete") is not None
        
        # Delete run
        success = self.registry.delete_run("test-run-to-delete")
        assert success is True
        
        # Verify run is deleted
        assert self.registry.get_run("test-run-to-delete") is None
        
        # Try to delete non-existent run
        success = self.registry.delete_run("non-existent-run")
        assert success is False 