"""
Unit tests for the Run Registry module.
Tests storage, retrieval, and API endpoints for generation runs.
"""

import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_registry import RunRegistry


class TestRunRegistry:
    """Test suite for RunRegistry class"""
    
    @pytest.fixture
    def temp_registry(self):
        """Create a temporary registry for testing"""
        temp_dir = tempfile.mkdtemp()
        registry = RunRegistry(base_dir=temp_dir)
        yield registry
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_save_run_creates_required_keys(self, temp_registry):
        """Test that saved runs contain all required keys"""
        config = {
            'prompt': 'A beautiful landscape',
            'negative_prompt': 'ugly, blurry',
            'model': 'sdxl-base-1.0',
            'vae': 'sdxl-vae',
            'loras': [{'name': 'style-lora', 'strength': 0.8}],
            'controlnet': {'enabled': True, 'model': 'canny'},
            'seed': 42,
            'sampler': 'euler_a',
            'steps': 20,
            'cfg_scale': 7.5,
            'generation_type': 'txt2img',
            'workflow': {'nodes': []},
            'workflow_version': '1.0.0'
        }
        
        run_id = temp_registry.save_run(config)
        
        # Verify run was saved
        assert run_id is not None
        assert len(run_id) == 36  # UUID format
        
        # Load the saved run
        run = temp_registry.get_run(run_id)
        
        # Check all required keys exist
        required_keys = [
            'id', 'timestamp', 'prompt', 'negative_prompt', 
            'model', 'vae', 'loras', 'controlnets',
            'seed', 'sampler', 'steps', 'cfg_scale',
            'generation_type', 'workflow', 'workflow_version'
        ]
        
        for key in required_keys:
            assert key in run, f"Required key '{key}' not found in saved run"
        
        # Verify values match
        assert run['prompt'] == config['prompt']
        assert run['model'] == config['model']
        assert run['seed'] == config['seed']
        assert run['generation_type'] == config['generation_type']
    
    def test_handle_empty_values_gracefully(self, temp_registry):
        """Test that empty or None values are handled without crashing"""
        config = {
            'prompt': '',  # Empty string
            'negative_prompt': None,  # None value
            'model': 'sdxl-base-1.0',
            'vae': None,
            'loras': [],  # Empty list
            'controlnet': {},  # Empty dict
            'seed': 42,
            'sampler': 'euler_a',
            'steps': 20,
            'cfg_scale': 7.5,
            'generation_type': 'txt2img',
            'workflow': None,
            'workflow_version': '1.0.0'
        }
        
        # Should not raise an exception
        run_id = temp_registry.save_run(config)
        assert run_id is not None
        
        # Load and verify
        run = temp_registry.get_run(run_id)
        assert run['prompt'] == ''
        assert run['negative_prompt'] is None
        assert run['loras'] == []
        assert run['controlnets'] == {}
        assert run['workflow'] is None
    
    def test_handle_missing_keys_with_defaults(self, temp_registry):
        """Test that missing keys get sensible defaults"""
        # Minimal config with many missing keys
        config = {
            'prompt': 'Test prompt',
            'generation_type': 'txt2img'
        }
        
        run_id = temp_registry.save_run(config)
        run = temp_registry.get_run(run_id)
        
        # Check that defaults were applied
        assert run['negative_prompt'] == ''  # Default empty string
        assert run['model'] == 'Unknown'  # Default model
        assert run['vae'] == 'Default'  # Default VAE
        assert run['loras'] == []  # Default empty list
        assert run['controlnets'] == {}  # Default empty dict
        assert run['seed'] == -1  # Default seed
        assert run['sampler'] == 'euler'  # Default sampler
        assert run['steps'] == 20  # Default steps
        assert run['cfg_scale'] == 7.0  # Default CFG
        assert run['workflow'] == {}  # Default empty workflow
        assert run['workflow_version'] == '1.0.0'  # Default version
    
    def test_list_runs_pagination(self, temp_registry):
        """Test listing runs with pagination"""
        # Save multiple runs
        for i in range(15):
            config = {
                'prompt': f'Test prompt {i}',
                'generation_type': 'txt2img',
                'seed': i
            }
            temp_registry.save_run(config)
        
        # Test first page
        runs = temp_registry.list_runs(limit=10, offset=0)
        assert len(runs) == 10
        
        # Test second page
        runs = temp_registry.list_runs(limit=10, offset=10)
        assert len(runs) == 5
        
        # Test offset beyond available runs
        runs = temp_registry.list_runs(limit=10, offset=20)
        assert len(runs) == 0
    
    def test_delete_run(self, temp_registry):
        """Test deleting a run"""
        config = {'prompt': 'Test', 'generation_type': 'txt2img'}
        run_id = temp_registry.save_run(config)
        
        # Verify run exists
        run = temp_registry.get_run(run_id)
        assert run is not None
        
        # Delete the run
        success = temp_registry.delete_run(run_id)
        assert success is True
        
        # Verify run no longer exists
        run = temp_registry.get_run(run_id)
        assert run is None
        
        # Verify it's not in the list
        runs = temp_registry.list_runs()
        assert not any(r['id'] == run_id for r in runs)
    
    def test_clear_all_runs(self, temp_registry):
        """Test clearing all runs"""
        # Save multiple runs
        run_ids = []
        for i in range(5):
            config = {'prompt': f'Test {i}', 'generation_type': 'txt2img'}
            run_id = temp_registry.save_run(config)
            run_ids.append(run_id)
        
        # Verify runs exist
        runs = temp_registry.list_runs()
        assert len(runs) == 5
        
        # Clear all runs
        temp_registry.clear_all_runs()
        
        # Verify all runs are gone
        runs = temp_registry.list_runs()
        assert len(runs) == 0
        
        # Verify individual runs are gone
        for run_id in run_ids:
            assert temp_registry.get_run(run_id) is None
    
    def test_thread_safety(self, temp_registry):
        """Test that operations are thread-safe"""
        import threading
        import time
        
        results = []
        errors = []
        
        def save_run(index):
            try:
                config = {
                    'prompt': f'Thread test {index}',
                    'generation_type': 'txt2img',
                    'seed': index
                }
                run_id = temp_registry.save_run(config)
                results.append(run_id)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_run, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Thread errors occurred: {errors}"
        assert len(results) == 10
        assert len(set(results)) == 10  # All IDs should be unique
        
        # Verify all runs were saved
        runs = temp_registry.list_runs()
        assert len(runs) == 10
    
    def test_large_config_handling(self, temp_registry):
        """Test handling of large configuration objects"""
        # Create a large config with many LoRAs and complex workflow
        config = {
            'prompt': 'A' * 1000,  # Long prompt
            'negative_prompt': 'B' * 1000,  # Long negative prompt
            'model': 'sdxl-base-1.0',
            'loras': [
                {'name': f'lora_{i}', 'strength': 0.5 + i * 0.01}
                for i in range(50)  # Many LoRAs
            ],
            'controlnet': {
                'enabled': True,
                'units': [
                    {
                        'enabled': True,
                        'model': f'controlnet_{i}',
                        'weight': 0.5 + i * 0.1,
                        'input_image': 'base64_' + 'x' * 10000  # Large image data
                    }
                    for i in range(5)
                ]
            },
            'workflow': {
                'nodes': [
                    {'id': i, 'type': 'node', 'data': {'value': 'x' * 100}}
                    for i in range(100)  # Large workflow
                ]
            },
            'generation_type': 'txt2img',
            'seed': 42,
            'sampler': 'euler_a',
            'steps': 50,
            'cfg_scale': 7.5,
            'workflow_version': '1.0.0'
        }
        
        # Should handle large config without issues
        run_id = temp_registry.save_run(config)
        assert run_id is not None
        
        # Verify it can be loaded
        run = temp_registry.get_run(run_id)
        assert run is not None
        assert len(run['loras']) == 50
        assert len(run['controlnets']['units']) == 5
        assert len(run['workflow']['nodes']) == 100
    
    def test_run_summary_format(self, temp_registry):
        """Test that run summaries have the correct format"""
        config = {
            'prompt': 'A beautiful sunset over mountains',
            'model': 'sdxl-base-1.0',
            'generation_type': 'txt2img',
            'seed': 12345
        }
        
        run_id = temp_registry.save_run(config)
        runs = temp_registry.list_runs(limit=1)
        
        assert len(runs) == 1
        summary = runs[0]
        
        # Check summary format
        assert 'id' in summary
        assert 'timestamp' in summary
        assert 'prompt' in summary
        assert 'model' in summary
        assert 'generation_type' in summary
        
        # Verify prompt is truncated in summary
        assert len(summary['prompt']) <= 100
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(summary['timestamp'])
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")


class TestRunRegistryAPI:
    """Test suite for Run Registry API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create Flask test client"""
        # Import the Flask app
        from dream_layer import app
        app.config['TESTING'] = True
        return app.test_client()
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry"""
        with patch('dream_layer.get_registry') as mock:
            registry = MagicMock()
            mock.return_value = registry
            yield registry
    
    def test_api_list_runs(self, app, mock_registry):
        """Test GET /api/runs endpoint"""
        mock_registry.list_runs.return_value = [
            {
                'id': 'test-id-1',
                'timestamp': '2024-01-01T00:00:00',
                'prompt': 'Test prompt 1',
                'model': 'sdxl',
                'generation_type': 'txt2img'
            }
        ]
        
        response = app.get('/api/runs?limit=10&offset=0')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['runs']) == 1
        assert data['runs'][0]['id'] == 'test-id-1'
    
    def test_api_get_run_by_id(self, app, mock_registry):
        """Test GET /api/runs/<run_id> endpoint"""
        mock_run = {
            'id': 'test-id',
            'timestamp': '2024-01-01T00:00:00',
            'prompt': 'Test prompt',
            'model': 'sdxl',
            'seed': 42,
            'generation_type': 'txt2img'
        }
        mock_registry.get_run.return_value = mock_run
        
        response = app.get('/api/runs/test-id')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['run']['id'] == 'test-id'
        assert data['run']['seed'] == 42
    
    def test_api_get_nonexistent_run(self, app, mock_registry):
        """Test getting a run that doesn't exist"""
        mock_registry.get_run.return_value = None
        
        response = app.get('/api/runs/nonexistent-id')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()
    
    def test_api_save_run(self, app, mock_registry):
        """Test POST /api/runs endpoint"""
        mock_registry.save_run.return_value = 'new-run-id'
        
        run_config = {
            'prompt': 'New test prompt',
            'model': 'sdxl',
            'generation_type': 'txt2img'
        }
        
        response = app.post('/api/runs',
                           data=json.dumps(run_config),
                           content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['run_id'] == 'new-run-id'
    
    def test_api_delete_run(self, app, mock_registry):
        """Test DELETE /api/runs/<run_id> endpoint"""
        mock_registry.delete_run.return_value = True
        
        response = app.delete('/api/runs/test-id')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'deleted successfully' in data['message'].lower()
    
    def test_api_delete_nonexistent_run(self, app, mock_registry):
        """Test deleting a run that doesn't exist"""
        mock_registry.delete_run.return_value = False
        
        response = app.delete('/api/runs/nonexistent-id')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
