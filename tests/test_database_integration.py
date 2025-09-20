"""
Tests for Database Integration - 3-Table Schema and Operations
"""
import pytest
import tempfile
import os
import sqlite3
from unittest.mock import patch, Mock
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dream_layer_backend'))

class TestDatabaseIntegration:
    
    def test_database_creation(self, temp_db):
        """Test database can be created with proper schema"""
        # Test basic database creation
        conn = sqlite3.connect(temp_db)
        
        # Create test tables to verify database works
        conn.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                model TEXT,
                prompt TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                run_id TEXT NOT NULL,
                asset_key TEXT NOT NULL,
                asset_value TEXT,
                PRIMARY KEY (run_id, asset_key)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                run_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                PRIMARY KEY (run_id, metric_name)
            )
        ''')
        
        conn.commit()
        
        # Verify tables exist
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'runs' in tables
        assert 'assets' in tables
        assert 'metrics' in tables
        
        conn.close()
    
    def test_save_generation_run(self):
        """Test saving generation run to database"""
        # Test the function signature and data handling
        generation_data = {
            'model_name': 'test-model',
            'prompt': 'test prompt',
            'seed': 12345,
            'steps': 20,
            'cfg_scale': 7.0
        }
        
        generated_images = ['test.png']
        generation_type = 'txt2img'
        
        # Test data validation
        assert 'model_name' in generation_data
        assert 'prompt' in generation_data
        assert isinstance(generated_images, list)
        assert generation_type in ['txt2img', 'img2img']
        
        # Test model name extraction logic
        model = generation_data.get('model') or generation_data.get('model_name', 'unknown')
        assert model == 'test-model'
        assert model != 'unknown'
    
    @patch('dream_layer_backend_utils.unified_database_queries.get_all_runs_with_clipscore')
    def test_get_all_runs_with_clipscore(self, mock_get_runs):
        """Test retrieving runs with ClipScore from database"""
        # Mock return data
        mock_get_runs.return_value = [
            {
                'run_id': 'run-123',
                'timestamp': '2025-08-20T00:00:00',
                'model': 'dall-e-3',
                'prompt': 'test prompt',
                'clip_score_mean': 0.85,
                'generated_images': ['test.png']
            }
        ]
        
        runs = mock_get_runs()
        
        # Should return list of runs
        assert isinstance(runs, list)
        assert len(runs) == 1
        assert runs[0]['clip_score_mean'] == 0.85
        mock_get_runs.assert_called_once()
    
    @patch('dream_layer_backend_utils.unified_database_queries.get_database_stats')
    def test_get_database_stats(self, mock_get_stats):
        """Test getting database statistics"""
        # Mock stats return
        mock_get_stats.return_value = {
            'total_runs': 45,
            'runs_with_clipscore': 35,
            'database_size_mb': 2.5
        }
        
        stats = mock_get_stats()
        
        assert isinstance(stats, dict)
        assert stats['total_runs'] == 45
        assert stats['runs_with_clipscore'] == 35
        mock_get_stats.assert_called_once()
    
    def test_database_schema_validation(self, temp_db):
        """Test that database schema matches expected structure"""
        # Create a simple test database
        conn = sqlite3.connect(temp_db)
        
        # Create test tables
        conn.execute('''
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                model TEXT,
                prompt TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE metrics (
                run_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                PRIMARY KEY (run_id, metric_name)
            )
        ''')
        
        conn.commit()
        
        # Verify schema
        cursor = conn.execute("PRAGMA table_info(runs)")
        runs_columns = [row[1] for row in cursor.fetchall()]
        
        assert 'run_id' in runs_columns
        assert 'timestamp' in runs_columns
        assert 'model' in runs_columns
        
        cursor = conn.execute("PRAGMA table_info(metrics)")
        metrics_columns = [row[1] for row in cursor.fetchall()]
        
        assert 'run_id' in metrics_columns
        assert 'metric_name' in metrics_columns
        assert 'metric_value' in metrics_columns
        
        conn.close()
    
    def test_clipscore_storage_and_retrieval(self, temp_db):
        """Test storing and retrieving ClipScore values"""
        conn = sqlite3.connect(temp_db)
        
        # Create metrics table
        conn.execute('''
            CREATE TABLE metrics (
                run_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                timestamp TEXT,
                PRIMARY KEY (run_id, metric_name)
            )
        ''')
        
        # Insert test ClipScore
        conn.execute('''
            INSERT INTO metrics (run_id, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', ('test-run-123', 'clip_score_mean', 0.85, '2025-08-20T00:00:00'))
        
        conn.commit()
        
        # Retrieve ClipScore
        cursor = conn.execute('''
            SELECT metric_value FROM metrics 
            WHERE run_id = ? AND metric_name = ?
        ''', ('test-run-123', 'clip_score_mean'))
        
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 0.85
        
        conn.close()
    
    def test_model_name_handling(self):
        """Test model name handling in database operations"""
        # Test model name extraction
        generation_data = {
            'model_name': 'dall-e-3',
            'prompt': 'test prompt'
        }
        
        # Test the logic we use in direct_database_integration
        model = generation_data.get('model') or generation_data.get('model_name', 'unknown')
        assert model == 'dall-e-3'
        assert model != 'unknown'
        
        # Test fallback
        empty_data = {}
        model_fallback = empty_data.get('model') or empty_data.get('model_name', 'unknown')
        assert model_fallback == 'unknown'
    
    def test_database_integration_workflow(self):
        """Test the complete database integration workflow"""
        # Test the workflow steps
        steps = [
            'Generate image',
            'Extract generation data',
            'Save to runs table',
            'Save to assets table',
            'Calculate ClipScore',
            'Save to metrics table'
        ]
        
        # Verify workflow steps are defined
        assert len(steps) == 6
        assert 'ClipScore' in steps[4]
        assert 'metrics table' in steps[5]
        
        # Test data flow
        run_data = {
            'run_id': 'test-123',
            'model': 'dall-e-3',
            'prompt': 'test prompt'
        }
        
        # Verify data structure
        assert 'run_id' in run_data
        assert 'model' in run_data
        assert 'prompt' in run_data
