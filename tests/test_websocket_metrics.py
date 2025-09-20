"""
Test WebSocket metrics calculation functionality
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

def test_run_registry_immediate_response():
    """Test that run_registry returns immediate response with pending counts"""
    from run_registry import app
    
    with app.test_client() as client:
        with patch('dream_layer_backend_utils.unified_database_queries.get_all_runs_with_metrics') as mock_get_runs:
            with patch('data.scripts.queries.DreamLayerQueries') as mock_queries_class:
                
                # Mock the queries instance and its methods
                mock_queries = MagicMock()
                mock_queries_class.return_value = mock_queries
                mock_queries.get_runs_without_clip_score.return_value = [{"run_id": "test2"}]
                mock_queries.get_runs_without_fid_score.return_value = [{"run_id": "test3"}]
                mock_queries.get_runs_without_composition_metrics.return_value = [{"run_id": "test4"}]
                
                # Mock return values
                mock_get_runs.return_value = [{"run_id": "test1", "clip_score_mean": 0.8}]
                
                response = client.get('/api/runs/enhanced/v2')
                data = json.loads(response.data)
                
                # Verify immediate response structure
                assert response.status_code == 200
                assert "runs" in data
                assert "pending_metrics" in data
                assert data["pending_metrics"]["clip"] == 1
                assert data["pending_metrics"]["fid"] == 1
                assert data["pending_metrics"]["composition"] == 1

def test_background_metrics_endpoint():
    """Test background metrics calculation endpoint"""
    from run_registry import app
    
    with app.test_client() as client:
        with patch('database_integration.ensure_clip_scores_calculated_with_progress') as mock_clip:
            with patch('database_integration.ensure_fid_scores_calculated_with_progress') as mock_fid:
                with patch('database_integration.ensure_composition_metrics_calculated_with_progress') as mock_comp:
                    
                    # Mock return values
                    mock_clip.return_value = {"success": 5, "failed": 0}
                    mock_fid.return_value = {"success": 3, "failed": 0}
                    mock_comp.return_value = {"success": 2, "failed": 0}
                    
                    response = client.post('/api/runs/calculate-metrics')
                    data = json.loads(response.data)
                    
                    assert response.status_code == 200
                    assert data["status"] == "completed"
                    
                    # Verify all progress functions were called
                    mock_clip.assert_called_once()
                    mock_fid.assert_called_once()
                    mock_comp.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
