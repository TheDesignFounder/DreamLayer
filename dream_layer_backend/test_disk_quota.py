#!/usr/bin/env python3
"""
Test suite for disk quota functionality.
"""

import pytest
import shutil
from unittest.mock import patch, MagicMock
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shared_utils


class TestDiskQuota:
    """Test disk quota functionality."""
    
    def setup_method(self):
        """Reset disk quota to default before each test."""
        shared_utils.set_max_disk_gb(shared_utils.DEFAULT_MAX_DISK_GB)
    
    def test_set_and_get_max_disk_gb(self):
        """Test setting and getting disk quota limit."""
        # Test default value
        assert shared_utils.get_max_disk_gb() == shared_utils.DEFAULT_MAX_DISK_GB
        
        # Test setting new value
        shared_utils.set_max_disk_gb(50.0)
        assert shared_utils.get_max_disk_gb() == 50.0
        
        # Test setting fractional value
        shared_utils.set_max_disk_gb(15.5)
        assert shared_utils.get_max_disk_gb() == 15.5
    
    def test_check_disk_space_sufficient(self):
        """Test disk space check when sufficient space is available."""
        # Mock disk usage to return plenty of space (100GB free)
        mock_usage = MagicMock()
        mock_usage.free = 100 * (1024**3)  # 100GB in bytes
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)  # Require 20GB
            result = shared_utils.check_disk_space()
            
            assert result['available'] is True
            assert result['free_gb'] == 100.0
            assert result['limit_gb'] == 20.0
            assert 'error' not in result
    
    def test_check_disk_space_insufficient(self):
        """Test disk space check when insufficient space is available."""
        # Mock disk usage to return limited space (10GB free)
        mock_usage = MagicMock()
        mock_usage.free = 10 * (1024**3)  # 10GB in bytes
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)  # Require 20GB
            result = shared_utils.check_disk_space()
            
            assert result['available'] is False
            assert result['free_gb'] == 10.0
            assert result['limit_gb'] == 20.0
            assert 'error' not in result
    
    def test_check_disk_space_error_handling(self):
        """Test disk space check error handling."""
        # Mock disk usage to raise an exception
        with patch('shutil.disk_usage', side_effect=OSError("Disk not found")):
            result = shared_utils.check_disk_space()
            
            assert result['available'] is False
            assert result['free_gb'] == 0
            assert result['limit_gb'] == shared_utils.get_max_disk_gb()
            assert 'error' in result
            assert 'Disk not found' in result['error']
    
    def test_check_disk_quota_before_output_sufficient(self):
        """Test quota check before output when space is sufficient."""
        # Mock disk usage to return plenty of space
        mock_usage = MagicMock()
        mock_usage.free = 100 * (1024**3)  # 100GB
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)
            result = shared_utils.check_disk_quota_before_output()
            
            # Should return None when space is sufficient
            assert result is None
    
    def test_check_disk_quota_before_output_insufficient(self):
        """Test quota check before output when space is insufficient."""
        # Mock disk usage to return limited space
        mock_usage = MagicMock()
        mock_usage.free = 5 * (1024**3)  # 5GB
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)
            result = shared_utils.check_disk_quota_before_output()
            
            # Should return error tuple when space is insufficient
            assert result is not None
            error_dict, status_code = result
            
            assert status_code == 507  # HTTP 507 Insufficient Storage
            assert error_dict['status'] == 'error'
            assert error_dict['error_code'] == 'DISK_QUOTA_EXCEEDED'
            assert 'Insufficient disk space' in error_dict['message']
            assert error_dict['disk_info']['free_gb'] == 5.0
            assert error_dict['disk_info']['limit_gb'] == 20.0
            assert error_dict['disk_info']['available'] is False
    
    def test_send_to_comfyui_disk_quota_exceeded(self):
        """Test send_to_comfyui function when disk quota is exceeded."""
        # Mock disk usage to return insufficient space
        mock_usage = MagicMock()
        mock_usage.free = 1 * (1024**3)  # 1GB
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)
            
            # Test workflow (content doesn't matter for quota check)
            test_workflow = {"test": "workflow"}
            
            result = shared_utils.send_to_comfyui(test_workflow)
            
            # Should return disk quota error without calling ComfyUI
            assert result['status'] == 'error'
            assert result['error_code'] == 'DISK_QUOTA_EXCEEDED'
            assert 'Insufficient disk space' in result['message']
    
    def test_send_to_comfyui_disk_quota_ok(self):
        """Test send_to_comfyui function when disk quota is OK."""
        # Mock disk usage to return sufficient space
        mock_usage = MagicMock()
        mock_usage.free = 100 * (1024**3)  # 100GB
        
        # Mock the workflow analyzer to avoid import errors
        mock_workflow_info = {
            'batch_size': 1,
            'is_api': False
        }
        
        with patch('shutil.disk_usage', return_value=mock_usage), \
             patch('dream_layer_backend_utils.workflow_loader.analyze_workflow', return_value=mock_workflow_info), \
             patch('requests.post') as mock_post, \
             patch('shared_utils.find_save_node', return_value="9"), \
             patch('shared_utils.wait_for_image', return_value=[]):
            
            # Mock successful ComfyUI response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"prompt_id": "test_123"}
            mock_post.return_value = mock_response
            
            shared_utils.set_max_disk_gb(20.0)
            
            # Test workflow
            test_workflow = {"test": "workflow"}
            
            result = shared_utils.send_to_comfyui(test_workflow)
            
            # Should proceed past disk quota check
            assert 'error_code' not in result or result.get('error_code') != 'DISK_QUOTA_EXCEEDED'
    
    def test_fractional_gb_calculations(self):
        """Test fractional GB calculations in disk space checks."""
        # Mock disk usage to return specific byte amount
        # 1.5GB = 1.5 * 1024^3 bytes
        mock_usage = MagicMock()
        mock_usage.free = int(1.5 * (1024**3))  # 1.5GB in bytes
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(2.0)  # Require 2GB
            result = shared_utils.check_disk_space()
            
            assert result['available'] is False  # 1.5GB < 2GB
            assert result['free_gb'] == 1.5
            assert result['limit_gb'] == 2.0
    
    def test_edge_case_exact_limit(self):
        """Test edge case where free space exactly equals the limit."""
        # Mock disk usage to return exactly the limit
        mock_usage = MagicMock()
        mock_usage.free = 20 * (1024**3)  # Exactly 20GB
        
        with patch('shutil.disk_usage', return_value=mock_usage):
            shared_utils.set_max_disk_gb(20.0)  # Require exactly 20GB
            result = shared_utils.check_disk_space()
            
            assert result['available'] is True  # 20GB >= 20GB
            assert result['free_gb'] == 20.0
            assert result['limit_gb'] == 20.0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])