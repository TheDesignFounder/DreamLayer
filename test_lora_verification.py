#!/usr/bin/env python3
"""
Simple verification script for LoRA merge utility.
This script can be run independently to verify the LoRA functionality.
"""

import sys
import os

# Add the dream_layer_backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "dream_layer_backend")
sys.path.insert(0, backend_dir)

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import diffusers
        print("✅ Diffusers imported successfully")
    except ImportError as e:
        print(f"❌ Diffusers import failed: {e}")
        return False
    
    try:
        import safetensors
        print("✅ Safetensors imported successfully")
    except ImportError as e:
        print(f"❌ Safetensors import failed: {e}")
        return False
    
    try:
        from lora_merge import merge_lora_with_base, create_dummy_checkpoint, create_dummy_lora
        print("✅ LoRA merge module imported successfully")
    except ImportError as e:
        print(f"❌ LoRA merge module import failed: {e}")
        return False
    
    return True

def _validate_merge_results(success, output_path):
    """Validate LoRA merge results."""
    merge_successful = success
    output_exists = os.path.exists(output_path)
    output_has_content = output_exists and os.path.getsize(output_path) > 0
    
    if not merge_successful:
        print("❌ LoRA merge test FAILED: Merge operation failed")
        return False
        
    if not output_exists:
        print("❌ LoRA merge test FAILED: Output file not found")
        return False
        
    if not output_has_content:
        print("❌ LoRA merge test FAILED: Output file is empty")
        return False
    
    return True

def _validate_cli_script(cli_path):
    """Validate CLI script existence and permissions."""
    cli_exists = os.path.exists(cli_path)
    cli_executable = cli_exists and os.access(cli_path, os.X_OK)
    
    if not cli_exists:
        print(f"❌ CLI script not found: {cli_path}")
        return False
        
    if not cli_executable:
        print(f"❌ CLI script not executable: {cli_path}")
        return False
    
    return True

def test_lora_functionality():
    """Test the actual LoRA merge functionality."""
    print("\n🧪 Testing LoRA functionality...")
    
    try:
        from lora_merge import create_dummy_checkpoint, create_dummy_lora, merge_lora_with_base
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='lora_verification_')
        print(f"📁 Created temp directory: {temp_dir}")
        
        try:
            # Create dummy files
            base_path = os.path.join(temp_dir, 'test_base.safetensors')
            lora_path = os.path.join(temp_dir, 'test_lora.safetensors')
            output_path = os.path.join(temp_dir, 'test_merged.safetensors')
            
            print("📝 Creating dummy checkpoint...")
            create_dummy_checkpoint(base_path, size_mb=0.5)
            
            print("📝 Creating dummy LoRA...")
            create_dummy_lora(lora_path, size_mb=0.05)
            
            print("🔄 Testing merge operation...")
            success = merge_lora_with_base(base_path, lora_path, output_path, alpha=0.8, device='cpu')
            
            # Validate test results
            validation_result = _validate_merge_results(success, output_path)
            if not validation_result:
                return False
            
            # Success case
            output_size = os.path.getsize(output_path) / (1024 * 1024)
            print("✅ LoRA merge test PASSED!")
            print(f"📊 Output file: {output_path}")
            print(f"📊 Output size: {output_size:.2f} MB")
            return True
                
        finally:
            # Clean up
            try:
                shutil.rmtree(temp_dir)
                print("🧹 Cleaned up temp directory")
            except (OSError, FileNotFoundError):
                pass  # Directory already gone or doesn't exist
                
    except Exception as e:
        print(f"❌ LoRA functionality test failed: {e}")
        return False

def test_cli_command():
    """Test the CLI command."""
    print("\n💻 Testing CLI command...")
    
    try:
        cli_path = os.path.join(current_dir, "dreamlayer")
        
        # Validate CLI script existence
        validation_result = _validate_cli_script(cli_path)
        if not validation_result:
            return False
        
        print(f"✅ CLI script exists and is executable: {cli_path}")
        
        # Test version command
        import subprocess
        try:
            result = subprocess.run([cli_path, "version"], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"❌ CLI version command failed: {result.stderr}")
                return False
                
            print("✅ CLI version command works")
            print(f"📋 Output: {result.stdout.strip()}")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ CLI version command timed out")
            return False
        except Exception as e:
            print(f"❌ CLI version command error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist."""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "dreamlayer",
        "dream_layer_backend/lora_merge.py",
        "dream_layer_backend/requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        file_exists = os.path.exists(full_path)
        
        if not file_exists:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
            continue
            
        print(f"✅ {file_path}")
    
    return all_exist

def main():
    """Run all verification tests."""
    print("🚀 DreamLayer LoRA Auto-Merge Verification")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("LoRA Functionality", test_lora_functionality), 
        ("CLI Command", test_cli_command)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        try:
            test_result = test_func()
            if not test_result:
                print(f"❌ {test_name} test FAILED")
                continue
                
            print(f"✅ {test_name} test PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed != total:
        print("⚠️  Some tests failed. Please check the output above.")
        return False
        
    print("🎉 ALL TESTS PASSED! LoRA Auto-Merge utility is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)