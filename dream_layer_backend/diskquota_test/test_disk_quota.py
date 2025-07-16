import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from shared_utils import check_disk_quota

def test_disk_quota_allows_enough_space(tmp_path, mocker):
    # Simulate 100GB total, 95GB used, 5GB free, quota 2GB (should allow)
    mocker.patch('shutil.disk_usage', return_value=(100*1024**3, 95*1024**3, 5*1024**3))
    assert check_disk_quota(str(tmp_path), 2) is True

def test_disk_quota_blocks_low_space(tmp_path, mocker):
    # Simulate 100GB total, 99GB used, 1GB free, quota 2GB (should block)
    mocker.patch('shutil.disk_usage', return_value=(100*1024**3, 99*1024**3, 1*1024**3))
    assert check_disk_quota(str(tmp_path), 2) is False