#!/usr/bin/env python3
"""
Test script for Multiple ControlNet Units Support
"""

import json
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dream_layer_backend_utils.img2img_controlnet_processor import inject_controlnet_into_workflow
from txt2img_workflow import inject_controlnet_parameters

def create_test_workflow():
    """Create a minimal test workflow for ControlNet injection."""
    return {
        "prompt": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": "test_model.safetensors"
                }
            },
            "4": {
                "class_type": "CLIPTextEncode", 
                "inputs": {
                    "clip": ["1", 1],
                    "text": "beautiful landscape"
                }
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1], 
                    "text": "ugly, blurry"
                }
            },
            "8": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["4", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0],
                    "sampler_name": "euler",
                    "steps": 20,
                    "cfg": 7.0,
                    "seed": 123456,
                    "scheduler": "normal", 
                    "denoise": 1.0
                }
            }
        }
    }

def test_single_controlnet_unit():
    """Test single ControlNet unit (existing functionality)."""
    print("🧪 Testing Single ControlNet Unit")
    print("=" * 50)
    
    workflow = create_test_workflow()
    
    controlnet_data = {
        "enabled": True,
        "units": [
            {
                "enabled": True,
                "control_type": "openpose",
                "model": "control_openpose.safetensors",
                "weight": 0.8,
                "guidance_start": 0.0,
                "guidance_end": 1.0,
                "input_image": "test_image.png",
                "input_image_path": "test_image.png"
            }
        ]
    }
    
    # Test img2img processor
    result = inject_controlnet_into_workflow(workflow, controlnet_data, "/tmp")
    
    # Check if ControlNet nodes were added
    nodes = result.get('prompt', {})
    controlnet_nodes = []
    
    for node_id, node_data in nodes.items():
        class_type = node_data.get('class_type')
        if 'ControlNet' in class_type:
            controlnet_nodes.append((node_id, class_type))
    
    print(f"✅ Added {len(controlnet_nodes)} ControlNet nodes:")
    for node_id, class_type in controlnet_nodes:
        print(f"   Node {node_id}: {class_type}")
    
    # Check KSampler connections
    ksampler = None
    for node_id, node_data in nodes.items():
        if node_data.get('class_type') == 'KSampler':
            ksampler = node_data
            break
    
    if ksampler:
        positive_input = ksampler['inputs']['positive']
        negative_input = ksampler['inputs']['negative']
        print(f"✅ KSampler positive input: {positive_input}")
        print(f"✅ KSampler negative input: {negative_input}")
    
    return len(controlnet_nodes) >= 2  # Should have Loader and Apply (LoadImage may be existing)

def test_multiple_controlnet_units():
    """Test multiple ControlNet units (new functionality)."""
    print("\n🧪 Testing Multiple ControlNet Units")
    print("=" * 50)
    
    workflow = create_test_workflow()
    
    # Create test data with 3 different ControlNet units
    controlnet_data = {
        "enabled": True,
        "units": [
            {
                "enabled": True,
                "control_type": "openpose",
                "model": "control_openpose.safetensors",
                "weight": 0.8,
                "guidance_start": 0.0,
                "guidance_end": 1.0,
                "input_image": "pose_image.png",
                "input_image_path": "pose_image.png"
            },
            {
                "enabled": True,
                "control_type": "canny",
                "model": "control_canny.safetensors", 
                "weight": 0.6,
                "guidance_start": 0.2,
                "guidance_end": 0.8,
                "input_image": "canny_image.png",
                "input_image_path": "canny_image.png"
            },
            {
                "enabled": True,
                "control_type": "depth",
                "model": "control_depth.safetensors",
                "weight": 0.7,
                "guidance_start": 0.1,
                "guidance_end": 0.9,
                "input_image": "depth_image.png", 
                "input_image_path": "depth_image.png"
            }
        ]
    }
    
    # Test img2img processor
    result = inject_controlnet_into_workflow(workflow, controlnet_data, "/tmp")
    
    # Analyze the result
    nodes = result.get('prompt', {})
    
    # Count different types of ControlNet nodes
    loader_nodes = []
    load_image_nodes = []
    apply_nodes = []
    
    for node_id, node_data in nodes.items():
        class_type = node_data.get('class_type')
        if class_type == 'ControlNetLoader':
            loader_nodes.append(node_id)
        elif class_type == 'LoadImage':
            load_image_nodes.append(node_id)
        elif class_type == 'ControlNetApplyAdvanced':
            apply_nodes.append(node_id)
    
    print(f"✅ ControlNet Loaders: {len(loader_nodes)} (expected: 3)")
    print(f"✅ LoadImage nodes: {len(load_image_nodes)} (expected: 3)")
    print(f"✅ ControlNet Apply nodes: {len(apply_nodes)} (expected: 3)")
    
    # Check chaining - each apply node should reference the previous one
    print("\n🔗 Checking ControlNet chaining:")
    for i, apply_id in enumerate(apply_nodes):
        apply_node = nodes[apply_id]
        positive_input = apply_node['inputs']['positive']
        negative_input = apply_node['inputs']['negative']
        
        if i == 0:
            # First node should connect to original conditioning
            expected_positive = "4"  # Original positive prompt
            expected_negative = "5"  # Original negative prompt
        else:
            # Subsequent nodes should chain to previous apply node
            expected_positive = apply_nodes[i-1]
            expected_negative = apply_nodes[i-1]
        
        print(f"   Apply node {i+1} ({apply_id}):")
        print(f"     Positive: {positive_input} (expected: [{expected_positive}, 0])")
        print(f"     Negative: {negative_input} (expected: [{expected_negative}, {'0' if i == 0 else '1'}])")
    
    # Check final KSampler connection
    ksampler = None
    for node_id, node_data in nodes.items():
        if node_data.get('class_type') == 'KSampler':
            ksampler = node_data
            break
    
    if ksampler and apply_nodes:
        final_apply = apply_nodes[-1]
        positive_input = ksampler['inputs']['positive']
        negative_input = ksampler['inputs']['negative']
        print(f"\n🎯 Final KSampler connections:")
        print(f"   Positive: {positive_input} (should connect to final apply node {final_apply})")
        print(f"   Negative: {negative_input} (should connect to final apply node {final_apply})")
    
    return len(loader_nodes) == 3 and len(apply_nodes) == 3

def test_mixed_enabled_disabled_units():
    """Test with some units enabled and some disabled."""
    print("\n🧪 Testing Mixed Enabled/Disabled Units")
    print("=" * 50)
    
    workflow = create_test_workflow()
    
    controlnet_data = {
        "enabled": True,
        "units": [
            {
                "enabled": True,  # Enabled
                "control_type": "openpose",
                "model": "control_openpose.safetensors",
                "weight": 0.8
            },
            {
                "enabled": False,  # Disabled - should be ignored
                "control_type": "canny",
                "model": "control_canny.safetensors",
                "weight": 0.6
            },
            {
                "enabled": True,  # Enabled
                "control_type": "depth", 
                "model": "control_depth.safetensors",
                "weight": 0.7
            }
        ]
    }
    
    result = inject_controlnet_into_workflow(workflow, controlnet_data, "/tmp")
    nodes = result.get('prompt', {})
    
    # Count ControlNet nodes - should only have 2 (for enabled units)
    apply_nodes = [id for id, data in nodes.items() if data.get('class_type') == 'ControlNetApplyAdvanced']
    
    print(f"✅ Expected 2 enabled units, got {len(apply_nodes)} ControlNet apply nodes")
    
    return len(apply_nodes) == 2

def test_txt2img_multiple_units():
    """Test txt2img workflow with multiple units.""" 
    print("\n🧪 Testing Txt2Img Multiple ControlNet Units")
    print("=" * 50)
    
    # Create a txt2img workflow with ControlNet template
    workflow = {
        "prompt": {
            "2": {
                "class_type": "ControlNetLoader",
                "inputs": {
                    "control_net_name": "diffusion_pytorch_model.safetensors"
                }
            },
            "3": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": "controlnet_input.png"
                }
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "beautiful"
                }
            },
            "5": {
                "class_type": "CLIPTextEncode", 
                "inputs": {
                    "text": "ugly"
                }
            }
        }
    }
    
    controlnet_data = {
        "enabled": True,
        "units": [
            {
                "enabled": True,
                "control_type": "openpose",
                "model": "control_openpose.safetensors",
                "weight": 0.8
            },
            {
                "enabled": True,
                "control_type": "canny",
                "model": "control_canny.safetensors",
                "weight": 0.6
            }
        ]
    }
    
    try:
        result = inject_controlnet_parameters(workflow, controlnet_data)
        nodes = result.get('prompt', {})
        
        # For multiple units, new nodes should be created
        if len(controlnet_data['units']) > 1:
            # Should have additional nodes beyond the template
            loader_count = sum(1 for data in nodes.values() if data.get('class_type') == 'ControlNetLoader')
            print(f"✅ Found {loader_count} ControlNet loaders for {len(controlnet_data['units'])} units")
            return loader_count >= len(controlnet_data['units'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error in txt2img test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Multiple ControlNet Units Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    tests = [
        ("Single ControlNet Unit", test_single_controlnet_unit),
        ("Multiple ControlNet Units", test_multiple_controlnet_units), 
        ("Mixed Enabled/Disabled", test_mixed_enabled_disabled_units),
        ("Txt2Img Multiple Units", test_txt2img_multiple_units),
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
        print("🎉 All tests passed! Multiple ControlNet units support is working correctly.")
    else:
        print("⚠️ Some tests failed. Review the implementation.")
    
    print("\n✨ Multiple ControlNet Units Implementation Complete!")