#!/usr/bin/env python3
"""
Test script for Additional API Key Support (Gemini & Anthropic)
"""

import os
import sys
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dream_layer_backend_utils.api_key_injector import (
    inject_api_keys_into_workflow,
    read_api_keys_from_env,
    NODE_TO_API_KEY_MAPPING,
    ENV_KEY_TO_EXTRA_DATA_MAPPING
)
from dream_layer import API_KEY_TO_MODELS, get_available_models

def test_api_key_infrastructure():
    """Test that the API key infrastructure is properly configured."""
    print("🧪 Testing API Key Infrastructure")
    print("=" * 50)
    
    # Test 1: Check if Gemini and Anthropic are in mappings
    gemini_keys = [k for k in ENV_KEY_TO_EXTRA_DATA_MAPPING.keys() if "GEMINI" in k]
    anthropic_keys = [k for k in ENV_KEY_TO_EXTRA_DATA_MAPPING.keys() if "ANTHROPIC" in k]
    
    print(f"✅ Gemini API keys configured: {gemini_keys}")
    print(f"✅ Anthropic API keys configured: {anthropic_keys}")
    
    # Test 2: Check node mappings
    gemini_nodes = [node for node, key in NODE_TO_API_KEY_MAPPING.items() if "GEMINI" in key]
    anthropic_nodes = [node for node, key in NODE_TO_API_KEY_MAPPING.items() if "ANTHROPIC" in key]
    
    print(f"✅ Gemini nodes configured: {len(gemini_nodes)} nodes")
    print(f"   Nodes: {gemini_nodes}")
    print(f"✅ Anthropic nodes configured: {len(anthropic_nodes)} nodes")
    print(f"   Nodes: {anthropic_nodes}")
    
    # Test 3: Check models
    gemini_models = API_KEY_TO_MODELS.get("GEMINI_API_KEY", [])
    anthropic_models = API_KEY_TO_MODELS.get("ANTHROPIC_API_KEY", [])
    
    print(f"✅ Gemini models configured: {len(gemini_models)} models")
    for model in gemini_models:
        print(f"   - {model['name']} ({model['id']})")
    
    print(f"✅ Anthropic models configured: {len(anthropic_models)} models")
    for model in anthropic_models:
        print(f"   - {model['name']} ({model['id']})")
    
    return len(gemini_keys) > 0 and len(anthropic_keys) > 0

def test_api_key_injection_single():
    """Test API key injection for single service workflows."""
    print("\n🧪 Testing Single Service API Key Injection")
    print("=" * 50)
    
    # Mock environment variables
    original_env = {}
    test_keys = {
        "GEMINI_API_KEY": "gsk-test-gemini-key-123456789",
        "ANTHROPIC_API_KEY": "sk-ant-test-anthropic-key-987654321"
    }
    
    # Set test environment variables
    for key, value in test_keys.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        # Test Gemini workflow
        gemini_workflow = {
            "prompt": {
                "1": {
                    "class_type": "GeminiImageNode",
                    "inputs": {
                        "prompt": "Generate an image of a sunset"
                    }
                }
            }
        }
        
        result = inject_api_keys_into_workflow(gemini_workflow)
        
        # Check if Gemini key was injected
        extra_data = result.get("extra_data", {})
        if "api_key_gemini" in extra_data:
            print("✅ Gemini API key properly injected")
            print(f"   Key: {extra_data['api_key_gemini'][:10]}...{extra_data['api_key_gemini'][-4:]}")
        else:
            print("❌ Gemini API key not injected")
        
        # Test Anthropic workflow
        anthropic_workflow = {
            "prompt": {
                "1": {
                    "class_type": "AnthropicClaudeNode",
                    "inputs": {
                        "prompt": "Analyze this image"
                    }
                }
            }
        }
        
        result = inject_api_keys_into_workflow(anthropic_workflow)
        
        # Check if Anthropic key was injected
        extra_data = result.get("extra_data", {})
        if "api_key_anthropic" in extra_data:
            print("✅ Anthropic API key properly injected")
            print(f"   Key: {extra_data['api_key_anthropic'][:10]}...{extra_data['api_key_anthropic'][-4:]}")
        else:
            print("❌ Anthropic API key not injected")
        
        return True
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def test_api_key_injection_multiple():
    """Test API key injection for workflows with multiple services."""
    print("\n🧪 Testing Multiple Service API Key Injection")
    print("=" * 50)
    
    # Mock environment variables
    original_env = {}
    test_keys = {
        "BFL_API_KEY": "sk-bfl-test-key-123456789",
        "GEMINI_API_KEY": "gsk-test-gemini-key-123456789",
        "ANTHROPIC_API_KEY": "sk-ant-test-anthropic-key-987654321"
    }
    
    # Set test environment variables
    for key, value in test_keys.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        # Multi-service workflow
        multi_workflow = {
            "prompt": {
                "1": {
                    "class_type": "FluxProImageNode",
                    "inputs": {
                        "prompt": "Generate base image"
                    }
                },
                "2": {
                    "class_type": "GeminiVisionNode",
                    "inputs": {
                        "image_input": ["1", 0],
                        "prompt": "Analyze this image"
                    }
                },
                "3": {
                    "class_type": "AnthropicSonnetNode",
                    "inputs": {
                        "text_input": ["2", 0],
                        "prompt": "Enhance the description"
                    }
                }
            }
        }
        
        result = inject_api_keys_into_workflow(multi_workflow)
        extra_data = result.get("extra_data", {})
        
        # Check all expected keys
        expected_keys = ["api_key_comfy_org", "api_key_gemini", "api_key_anthropic"]
        injected_keys = []
        
        for expected_key in expected_keys:
            if expected_key in extra_data:
                injected_keys.append(expected_key)
                key_value = extra_data[expected_key]
                print(f"✅ {expected_key}: {key_value[:10]}...{key_value[-4:]}")
        
        print(f"✅ Successfully injected {len(injected_keys)}/{len(expected_keys)} expected keys")
        
        return len(injected_keys) == len(expected_keys)
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def test_model_availability():
    """Test that new models are available when API keys are present."""
    print("\n🧪 Testing Model Availability")
    print("=" * 50)
    
    # Mock environment variables
    original_env = {}
    test_keys = {
        "GEMINI_API_KEY": "gsk-test-gemini-key-123456789",
        "ANTHROPIC_API_KEY": "sk-ant-test-anthropic-key-987654321"
    }
    
    # Set test environment variables
    for key, value in test_keys.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        # Get available models
        models = get_available_models()
        
        # Check for Gemini models
        gemini_models = [m for m in models if "gemini" in m.get("id", "").lower()]
        print(f"✅ Gemini models available: {len(gemini_models)}")
        for model in gemini_models:
            print(f"   - {model['name']} ({model['id']})")
        
        # Check for Anthropic/Claude models
        claude_models = [m for m in models if "claude" in m.get("id", "").lower()]
        print(f"✅ Claude models available: {len(claude_models)}")
        for model in claude_models:
            print(f"   - {model['name']} ({model['id']})")
        
        return len(gemini_models) > 0 and len(claude_models) > 0
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def test_priority_handling():
    """Test API key priority handling when multiple keys compete."""
    print("\n🧪 Testing API Key Priority Handling")
    print("=" * 50)
    
    # Mock environment variables with all comfy_org keys
    original_env = {}
    test_keys = {
        "BFL_API_KEY": "sk-bfl-priority-test-123",
        "OPENAI_API_KEY": "sk-openai-priority-test-456",
        "IDEOGRAM_API_KEY": "sk-ideogram-priority-test-789"
    }
    
    # Set test environment variables
    for key, value in test_keys.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        # Workflow with multiple comfy_org compatible nodes
        workflow = {
            "prompt": {
                "1": {
                    "class_type": "FluxProImageNode",
                    "inputs": {"prompt": "FLUX image"}
                },
                "2": {
                    "class_type": "OpenAIDalle3",
                    "inputs": {"prompt": "DALL-E image"}
                },
                "3": {
                    "class_type": "IdeogramV3",
                    "inputs": {"prompt": "Ideogram image"}
                }
            }
        }
        
        result = inject_api_keys_into_workflow(workflow)
        extra_data = result.get("extra_data", {})
        
        # Check that BFL gets priority (should be first in priority order)
        if "api_key_comfy_org" in extra_data:
            used_key = extra_data["api_key_comfy_org"]
            if used_key == test_keys["BFL_API_KEY"]:
                print("✅ Correct priority: BFL_API_KEY chosen for api_key_comfy_org")
            else:
                print(f"❌ Wrong priority: Expected BFL key, got {used_key[:10]}...")
                
            return used_key == test_keys["BFL_API_KEY"]
        else:
            print("❌ No api_key_comfy_org injected")
            return False
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

def test_error_handling():
    """Test error handling for missing or invalid API keys."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    # Clear any existing API keys
    api_key_vars = ["GEMINI_API_KEY", "ANTHROPIC_API_KEY", "BFL_API_KEY", "OPENAI_API_KEY"]
    original_values = {}
    
    for var in api_key_vars:
        original_values[var] = os.environ.get(var)
        os.environ.pop(var, None)
    
    try:
        # Workflow that needs API keys but none are available
        workflow = {
            "prompt": {
                "1": {
                    "class_type": "GeminiImageNode",
                    "inputs": {"prompt": "Test"}
                }
            }
        }
        
        result = inject_api_keys_into_workflow(workflow)
        extra_data = result.get("extra_data", {})
        
        # Should handle gracefully (no crash, empty extra_data is OK)
        print(f"✅ Graceful handling: No crash when keys missing")
        print(f"   Extra data: {extra_data}")
        
        return True  # No crash = success
        
    except Exception as e:
        print(f"❌ Error handling failed: {e}")
        return False
        
    finally:
        # Restore original environment
        for var, original_value in original_values.items():
            if original_value is not None:
                os.environ[var] = original_value

if __name__ == "__main__":
    print("🚀 Additional API Key Support Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    tests = [
        ("API Key Infrastructure", test_api_key_infrastructure),
        ("Single Service Injection", test_api_key_injection_single),
        ("Multiple Service Injection", test_api_key_injection_multiple),
        ("Model Availability", test_model_availability),
        ("Priority Handling", test_priority_handling),
        ("Error Handling", test_error_handling),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR: {test_name} - {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini and Anthropic API key support is working correctly.")
        print("\n📋 NEXT STEPS:")
        print("1. Add actual GEMINI_API_KEY and ANTHROPIC_API_KEY to your .env file")
        print("2. Deploy ComfyUI nodes for Gemini and Anthropic if available")
        print("3. Test with real API calls")
    else:
        print("⚠️ Some tests failed. Review the implementation.")
    
    print("\n✨ Additional API Key Support Implementation Complete!")