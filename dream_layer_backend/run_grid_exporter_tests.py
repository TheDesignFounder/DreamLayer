#!/usr/bin/env python3
"""
Test runner for the labeled grid exporter.

This script runs the comprehensive test suite for the labeled grid exporter
and provides a summary of the results.
"""

import sys
import subprocess
import os

def main():
    """Run the labeled grid exporter tests."""
    print("🧪 Running Labeled Grid Exporter Tests")
    print("=" * 50)
    
    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Run the tests
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_labeled_grid_exporter.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            print("\nTest Summary:")
            print("- ✅ Input validation (success and failure cases)")
            print("- ✅ CSV metadata reading")
            print("- ✅ Image collection (with and without metadata)")
            print("- ✅ Grid dimension calculation")
            print("- ✅ Grid assembly (basic, with metadata, auto-layout)")
            print("- ✅ Custom font and margin settings")
            print("- ✅ Error handling (empty input)")
            print("- ✅ End-to-end workflow")
            print("\n🎉 The labeled grid exporter is working correctly!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out after 60 seconds")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 