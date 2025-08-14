"""
Tests for Report Bundle functionality.
"""

import csv
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image

from tools.report_bundle import build_report_bundle, validate_bundle
from tools.report_schema import validate_results_csv, CORE_COLUMNS, METRIC_COLUMNS


class TestReportBundle:
    """Test cases for report bundle functionality."""
    
    @pytest.fixture
    def temp_run_dir(self):
        """Create a temporary run directory with test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "test_run"
            run_dir.mkdir()
            
            # Create test config.json
            config_data = {
                "run_id": "test_run_123",
                "model_name": "test_model.safetensors",
                "preset_name": "test_preset",
                "width": 512,
                "height": 512,
                "steps": 20,
                "cfg": 7.0
            }
            
            with open(run_dir / "config.json", 'w') as f:
                json.dump(config_data, f)
            
            # Create test results.csv
            results_data = [
                {
                    "run_id": "test_run_123",
                    "image_path": "output/image1.png",
                    "seed": 42,
                    "sampler": "euler",
                    "steps": 20,
                    "cfg": 7.0,
                    "preset_name": "test_preset",
                    "preset_hash": "abc123",
                    "ssim": 0.95,
                    "clip_score": 0.8,
                    "lpips": 0.1
                },
                {
                    "run_id": "test_run_123",
                    "image_path": "output/image2.png",
                    "seed": 43,
                    "sampler": "euler",
                    "steps": 20,
                    "cfg": 7.0,
                    "preset_name": "test_preset",
                    "preset_hash": "abc123",
                    "ssim": 0.92,
                    "clip_score": 0.75,
                    "lpips": 0.15
                }
            ]
            
            with open(run_dir / "results.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CORE_COLUMNS + METRIC_COLUMNS)
                writer.writeheader()
                writer.writerows(results_data)
            
            # Create test images
            (run_dir / "output").mkdir()
            (run_dir / "grids").mkdir()
            
            # Create dummy image files
            for img_path in ["output/image1.png", "output/image2.png", "grids/grid.png"]:
                (run_dir / img_path).touch()
            
            yield run_dir
    
    def test_build_report_bundle_success(self, temp_run_dir):
        """Test successful report bundle creation."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        try:
            # Build bundle
            result = build_report_bundle(temp_run_dir, zip_path)
            
            # Verify result
            assert result["files"] is not None
            assert result["sha256"] is not None
            assert result["bundle_size"] > 0
            
            # Verify ZIP contents
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                
                # Check required files
                assert "config.json" in file_list
                assert "results.csv" in file_list
                assert "README.txt" in file_list
                assert any(f.startswith("images/") for f in file_list)
                
                # Verify deterministic order
                expected_files = sorted(file_list)
                assert file_list == expected_files
                
                # Check CSV content
                with zipf.open("results.csv") as csv_file:
                    csv_content = csv_file.read().decode('utf-8')
                    assert "schema_version" in csv_content
                    assert "test_run_123" in csv_content
                
                # Check README content
                with zipf.open("README.txt") as readme_file:
                    readme_content = readme_file.read().decode('utf-8')
                    assert "DreamLayer AI" in readme_content
                    assert "test_run_123" in readme_content
                    
        finally:
            zip_path.unlink(missing_ok=True)
    
    def test_build_report_bundle_missing_files(self, temp_run_dir):
        """Test bundle creation with missing required files."""
        # Remove required files
        (temp_run_dir / "results.csv").unlink()
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        try:
            with pytest.raises(ValueError, match="Required file not found"):
                build_report_bundle(temp_run_dir, zip_path)
        finally:
            zip_path.unlink(missing_ok=True)
    
    def test_build_report_bundle_custom_globs(self, temp_run_dir):
        """Test bundle creation with custom glob patterns."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        try:
            # Use custom globs
            custom_globs = ["output/*.png", "grids/*.png"]
            result = build_report_bundle(temp_run_dir, zip_path, custom_globs)
            
            # Verify custom files included
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                assert "images/image1.png" in file_list
                assert "images/image2.png" in file_list
                assert "images/grid.png" in file_list
                
        finally:
            zip_path.unlink(missing_ok=True)
    
    def test_validate_bundle_success(self, temp_run_dir):
        """Test successful bundle validation."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        try:
            # Build bundle first
            build_report_bundle(temp_run_dir, zip_path)
            
            # Validate bundle
            validation = validate_bundle(zip_path)
            
            assert validation["valid"] is True
            assert validation["total_files"] > 0
            assert validation["csv_valid"] is True
            assert "config.json" in validation["file_list"]
            assert "results.csv" in validation["file_list"]
            assert "README.txt" in validation["file_list"]
            
        finally:
            zip_path.unlink(missing_ok=True)
    
    def test_validate_bundle_invalid(self):
        """Test bundle validation with invalid ZIP."""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            zip_path = Path(temp_zip.name)
        
        try:
            # Create invalid ZIP
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.writestr("test.txt", "invalid content")
            
            # Validate bundle
            validation = validate_bundle(zip_path)
            
            assert validation["valid"] is False
            assert "Missing required files" in validation["error"]
            
        finally:
            zip_path.unlink(missing_ok=True)


class TestReportSchema:
    """Test cases for report schema validation."""
    
    @pytest.fixture
    def temp_run_dir(self):
        """Create a temporary run directory with test files"""
        run_dir = Path(tempfile.mkdtemp())
        
        # Create config.json
        config = {
            "run_id": "test_run_123",
            "timestamp": "2024-01-01T00:00:00Z",
            "preset_name": "test_preset",
            "preset_hash": "abc123"
        }
        config_file = run_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        # Create results.csv
        results_data = [
            ["run_id", "image_path", "seed", "sampler", "steps", "cfg", "preset_name", "preset_hash", "ssim", "clip_score", "lpips"],
            ["test_run_123", "images/grid_00001.png", "42", "euler", "20", "7.5", "test_preset", "abc123", "0.95", "0.87", "0.12"],
            ["test_run_123", "images/grid_00002.png", "43", "euler", "20", "7.5", "test_preset", "abc123", "0.92", "0.89", "0.15"]
        ]
        results_file = run_dir / "results.csv"
        with open(results_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(results_data)
        
        # Create images directory with dummy images
        images_dir = run_dir / "images"
        images_dir.mkdir()
        
        # Create dummy images
        for i in range(1, 3):
            img = Image.new('RGB', (512, 512), color=(i * 50, i * 50, i * 50))
            img.save(images_dir / f"grid_{i:05d}.png")
        
        yield run_dir
        
        # Cleanup
        shutil.rmtree(run_dir)

    @pytest.fixture
    def temp_csv_file(self):
        """Create a temporary CSV file with test data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            csv_path = Path(temp_csv.name)
        
        try:
            # Create test CSV
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CORE_COLUMNS + METRIC_COLUMNS)
                writer.writeheader()
                writer.writerow({
                    "run_id": "test_123",
                    "image_path": "test.png",
                    "seed": 42,
                    "sampler": "euler",
                    "steps": 20,
                    "cfg": 7.0,
                    "preset_name": "test",
                    "preset_hash": "abc123",
                    "ssim": 0.95,
                    "clip_score": 0.8,
                    "lpips": 0.1
                })
            
            yield csv_path
            
        finally:
            csv_path.unlink(missing_ok=True)
    
    def test_validate_results_csv_success(self, temp_csv_file):
        """Test successful CSV validation."""
        # Should not raise any exception
        validate_results_csv(temp_csv_file)
    
    def test_validate_results_csv_missing_columns(self):
        """Test CSV validation with missing columns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            csv_path = Path(temp_csv.name)
        
        try:
            # Create CSV with missing columns
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["run_id", "image_path"])  # Missing required columns
                writer.writerow(["test", "test.png"])
            
            with pytest.raises(ValueError, match="Missing required columns"):
                validate_results_csv(csv_path)
                
        finally:
            csv_path.unlink(missing_ok=True)
    
    def test_validate_results_csv_with_schema_version(self):
        """Test CSV validation with schema version."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_csv:
            csv_path = Path(temp_csv.name)
        
        try:
            # Create CSV with schema version and missing metric columns
            fieldnames = ["schema_version"] + [col for col in CORE_COLUMNS if col not in ["ssim", "clip_score", "lpips"]]
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({
                    "schema_version": "1.0",
                    "run_id": "test_123",
                    "image_path": "test.png",
                    "seed": 42,
                    "sampler": "euler",
                    "steps": 20,
                    "cfg": 7.0,
                    "preset_name": "test",
                    "preset_hash": "abc123"
                })
            
            # Should not raise exception for missing metric columns with schema version
            validate_results_csv(csv_path)
                
        finally:
            csv_path.unlink(missing_ok=True)
    
    def test_validate_results_csv_image_paths(self, temp_run_dir):
        """Test CSV validation with image path resolution."""
        # Create CSV with relative paths that exist
        csv_path = temp_run_dir / "results_rel.csv"

        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CORE_COLUMNS + METRIC_COLUMNS)
            writer.writeheader()
            writer.writerow({
                "run_id": "test_123",
                "image_path": "images/grid_00001.png",  # Use relative path that exists
                "seed": 42,
                "sampler": "euler",
                "steps": 20,
                "cfg": 7.0,
                "preset_name": "test",
                "preset_hash": "abc123",
                "ssim": 0.95,
                "clip_score": 0.8,
                "lpips": 0.1
            })

        # Should not raise exception for valid image paths
        validate_results_csv(csv_path, temp_run_dir)
    
    def test_validate_results_csv_invalid_image_paths(self, temp_run_dir):
        """Test CSV validation with invalid image paths."""
        csv_path = temp_run_dir / "results_invalid.csv"
        
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=CORE_COLUMNS + METRIC_COLUMNS)
            writer.writeheader()
            writer.writerow({
                "run_id": "test_123",
                "image_path": "nonexistent.png",
                "seed": 42,
                "sampler": "euler",
                "steps": 20,
                "cfg": 7.0,
                "preset_name": "test",
                "preset_hash": "abc123",
                "ssim": 0.95,
                "clip_score": 0.8,
                "lpips": 0.1
            })
        
        with pytest.raises(ValueError, match="Image path not found"):
            validate_results_csv(csv_path, temp_run_dir)
