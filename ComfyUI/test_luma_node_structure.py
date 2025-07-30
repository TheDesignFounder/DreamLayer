#!/usr/bin/env python3
"""
Simple validation script for Luma Text2Img node structure.
This script tests the basic structure without requiring the full ComfyUI environment.
"""

import sys
import os

def test_luma_node_structure():
    """Test the basic structure of the Luma node implementation."""
    
    print("🔍 Testing Luma Text2Img Node Structure...")
    
    # Test 1: Check if the node file exists
    node_file = "comfy_api_nodes/nodes_luma.py"
    if os.path.exists(node_file):
        print("✅ Luma node file exists:", node_file)
    else:
        print("❌ Luma node file not found:", node_file)
        return False
    
    # Test 2: Check if test file exists
    test_file = "tests-unit/comfy_api_nodes_test/test_luma_text2img.py"
    if os.path.exists(test_file):
        print("✅ Test file exists:", test_file)
    else:
        print("❌ Test file not found:", test_file)
        return False
    
    # Test 3: Check if documentation exists
    doc_file = "comfy_api_nodes/README_LUMA_TEXT2IMG.md"
    if os.path.exists(doc_file):
        print("✅ Documentation exists:", doc_file)
    else:
        print("❌ Documentation not found:", doc_file)
        return False
    
    # Test 4: Check node file content structure
    try:
        with open(node_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key components
        checks = [
            ("LumaImageGenerationNode class", "class LumaImageGenerationNode" in content),
            ("RETURN_TYPES", "RETURN_TYPES" in content),
            ("INPUT_TYPES", "INPUT_TYPES" in content),
            ("api_call method", "def api_call" in content),
            ("NODE_CLASS_MAPPINGS", "NODE_CLASS_MAPPINGS" in content),
            ("NODE_DISPLAY_NAME_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS" in content),
        ]
        
        for check_name, result in checks:
            if result:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} not found")
                return False
                
    except Exception as e:
        print(f"❌ Error reading node file: {e}")
        return False
    
    # Test 5: Check test file content structure
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key test components
        test_checks = [
            ("TestLumaImageGenerationNode class", "class TestLumaImageGenerationNode" in content),
            ("test_node_input_types", "test_node_input_types" in content),
            ("test_api_call_success", "test_api_call_success" in content),
            ("pytest import", "import pytest" in content),
        ]
        
        for check_name, result in test_checks:
            if result:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} not found")
                return False
                
    except Exception as e:
        print(f"❌ Error reading test file: {e}")
        return False
    
    # Test 6: Check documentation content
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key documentation components
        doc_checks = [
            ("Overview section", "## Overview" in content),
            ("Features section", "## Features" in content),
            ("Setup section", "## Setup" in content),
            ("Node Parameters", "## Node Parameters" in content),
            ("Usage Examples", "## Usage Examples" in content),
            ("API Endpoints", "## API Endpoints" in content),
        ]
        
        for check_name, result in doc_checks:
            if result:
                print(f"✅ {check_name} found")
            else:
                print(f"❌ {check_name} not found")
                return False
                
    except Exception as e:
        print(f"❌ Error reading documentation: {e}")
        return False
    
    print("\n🎉 All structure tests passed!")
    return True

def test_environment_setup():
    """Test environment setup requirements."""
    
    print("\n🔍 Testing Environment Setup...")
    
    # Check for .env.example
    env_example = "../.env.example"
    if os.path.exists(env_example):
        print("✅ .env.example exists")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            if "LUMA_API_KEY" in content:
                print("✅ LUMA_API_KEY placeholder found in .env.example")
            else:
                print("❌ LUMA_API_KEY placeholder not found in .env.example")
        except Exception as e:
            print(f"❌ Error reading .env.example: {e}")
    else:
        print("❌ .env.example not found")
    
    # Check git branch
    try:
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            branch = result.stdout.strip()
            print(f"✅ Current git branch: {branch}")
            if "luma-text2img-node" in branch:
                print("✅ Working on correct feature branch")
            else:
                print("⚠️  Not on luma-text2img-node branch")
        else:
            print("❌ Could not determine git branch")
    except Exception as e:
        print(f"❌ Error checking git branch: {e}")

def main():
    """Main validation function."""
    
    print("🚀 Luma Text2Img Node Validation")
    print("=" * 50)
    
    # Test structure
    structure_ok = test_luma_node_structure()
    
    # Test environment
    test_environment_setup()
    
    print("\n" + "=" * 50)
    if structure_ok:
        print("✅ Validation completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Set up LUMA_API_KEY in .env file")
        print("2. Run integration tests with real API key")
        print("3. Push changes to your fork")
        print("4. Create Pull Request to DreamLayer main repo")
        print("5. Email DreamLayer confirming PR submission")
    else:
        print("❌ Validation failed - please check the issues above")
    
    return 0 if structure_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 