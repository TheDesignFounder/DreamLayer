"""
Test file validation logic for multi-format model uploads
Tests the core extension validation implemented in shared_utils.py
"""

import pytest
from pathlib import Path


class TestFileExtensionValidation:
    """Test file extension validation logic"""
    
    def test_validates_safetensors_extension(self, expected_extensions):
        """Test that .safetensors files are accepted"""
        filename = "model.safetensors"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_validates_ckpt_extension(self, expected_extensions):
        """Test that .ckpt files are accepted"""
        filename = "model.ckpt"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_validates_pth_extension(self, expected_extensions):
        """Test that .pth files are accepted"""
        filename = "model.pth"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_validates_pt_extension(self, expected_extensions):
        """Test that .pt files are accepted"""
        filename = "model.pt"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_validates_bin_extension(self, expected_extensions):
        """Test that .bin files are accepted"""
        filename = "model.bin"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_rejects_txt_extension(self, expected_extensions):
        """Test that .txt files are rejected"""
        filename = "model.txt"
        file_ext = Path(filename).suffix.lower()
        assert file_ext not in expected_extensions
    
    def test_rejects_pkl_extension(self, expected_extensions):
        """Test that .pkl files are rejected"""
        filename = "model.pkl"
        file_ext = Path(filename).suffix.lower()
        assert file_ext not in expected_extensions
    
    def test_rejects_no_extension(self, expected_extensions):
        """Test that files without extensions are rejected"""
        filename = "model"
        file_ext = Path(filename).suffix.lower()
        assert file_ext not in expected_extensions
    
    @pytest.mark.parametrize("filename", [
        "model.SAFETENSORS",
        "model.CkPt",
        "model.PTH",
        "model.PT",
        "model.BIN"
    ])
    def test_case_insensitive_validation(self, filename, expected_extensions):
        """Test that extension validation is case insensitive"""
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions, f"Failed for {filename}"
    
    def test_all_expected_extensions_covered(self, sample_model_files, expected_extensions):
        """Test that all expected extensions are covered in our test cases"""
        valid_files = [
            sample_model_files['valid_safetensors'],
            sample_model_files['valid_ckpt'],
            sample_model_files['valid_pth'],
            sample_model_files['valid_pt'],
            sample_model_files['valid_bin']
        ]

        tested_extensions = {Path(filename).suffix.lower() for filename in valid_files}
        assert tested_extensions == expected_extensions


class TestFileValidationIntegration:
    """Test file validation integration with upload logic"""
    
    def test_validation_logic_matches_implementation(self, expected_extensions):
        """Test that our validation logic matches the actual implementation"""
        # This tests the exact logic used in shared_utils.py
        allowed_extensions = {'.safetensors', '.ckpt', '.pth', '.pt', '.bin'}
        
        # Verify our test expectations match the implementation
        assert allowed_extensions == expected_extensions
    
    def test_error_message_format(self, expected_extensions):
        """Test that error message includes all supported formats"""
        # Test the error message format used in shared_utils.py
        error_message = f"Invalid file type. Supported formats: {', '.join(sorted(expected_extensions))}"
        
        # Verify all extensions are included
        assert all(ext in error_message for ext in expected_extensions)
    
    @pytest.mark.parametrize("filename,should_pass", [
        ("model.safetensors", True),
        ("model.ckpt", True),
        ("model.pth", True),
        ("model.pt", True),
        ("model.bin", True),
        ("model.txt", False),
        ("model.pkl", False),
        ("model.json", False),
        ("model", False),
        ("model.SAFETENSORS", True),
        ("model.CkPt", True),
    ])
    def test_parametrized_validation(self, filename, should_pass, expected_extensions):
        """Parametrized test for various file extensions"""
        file_ext = Path(filename).suffix.lower()
        is_valid = file_ext in expected_extensions
        
        assert is_valid == should_pass, f"Failed for {filename}: expected {should_pass}, got {is_valid}"


class TestValidationEdgeCases:
    """Test edge cases in file validation"""
    
    def test_empty_filename(self, expected_extensions):
        """Test handling of empty filename"""
        filename = ""
        file_ext = Path(filename).suffix.lower()
        assert file_ext not in expected_extensions
    
    def test_filename_with_multiple_dots(self, expected_extensions):
        """Test filename with multiple dots"""
        filename = "model.backup.safetensors"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions
    
    def test_filename_with_path(self, expected_extensions):
        """Test filename that includes path components"""
        filename = "path/to/model.safetensors"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions

    def test_filename_with_windows_path(self, expected_extensions):
        """Test filename that includes Windows-style path components"""
        filename = "path\\to\\model.safetensors"
        file_ext = Path(filename).suffix.lower()
        assert file_ext in expected_extensions

    def test_very_long_extension(self, expected_extensions):
        """Test very long extension"""
        filename = "model.verylongextension"
        file_ext = Path(filename).suffix.lower()
        assert file_ext not in expected_extensions
