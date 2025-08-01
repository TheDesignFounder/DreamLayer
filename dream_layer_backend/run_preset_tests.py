#!/usr/bin/env python3
"""
Test runner for the preset system
Run this to verify that the preset functionality works correctly
"""

import sys
import os
import json
from preset_manager import PresetManager

def test_preset_basic_functionality():
    """Test basic preset functionality"""
    print("🧪 Testing basic preset functionality...")
    
    # Create a temporary preset manager
    manager = PresetManager("test_presets.json")
    
    # Test creating a preset
    settings = {
        "prompt": "test prompt",
        "negative_prompt": "test negative",
        "model_name": "test_model.safetensors",
        "sampler_name": "euler",
        "scheduler": "normal",
        "steps": 20,
        "cfg_scale": 7.0,
        "width": 512,
        "height": 512,
        "batch_size": 1,
        "batch_count": 1,
        "seed": -1,
        "random_seed": True
    }
    
    preset = manager.create_preset(
        name="Test Preset",
        description="A test preset",
        settings=settings
    )
    
    print(f"✅ Created preset: {preset.name}")
    print(f"   ID: {preset.id}")
    print(f"   Hash: {preset.hash}")
    print(f"   Version: {preset.version}")
    
    # Test retrieving the preset
    retrieved = manager.get_preset(preset.id)
    assert retrieved is not None
    assert retrieved.name == preset.name
    print("✅ Preset retrieval works")
    
    # Test hash validation
    is_valid = manager.validate_preset_hash(preset.id, settings)
    assert is_valid == True
    print("✅ Hash validation works")
    
    # Test updating preset
    updated_settings = settings.copy()
    updated_settings["steps"] = 30
    
    original_hash = preset.hash
    
    updated_preset = manager.update_preset(
        preset.id,
        settings=updated_settings
    )
    
    assert updated_preset.settings["steps"] == 30
    assert updated_preset.hash != original_hash  # Hash should change
    print("✅ Preset update works")
    
    # Test getting all presets
    all_presets = manager.get_all_presets()
    assert len(all_presets) > 0
    print(f"✅ Found {len(all_presets)} presets")
    
    # Clean up
    if os.path.exists("test_presets.json"):
        os.unlink("test_presets.json")
    
    print("✅ All basic functionality tests passed!")

def test_default_presets():
    """Test that default presets are created correctly"""
    print("\n🧪 Testing default presets...")
    
    manager = PresetManager("test_default_presets.json")
    
    presets = manager.get_all_presets()
    
    # Check for default presets
    preset_names = [p.name for p in presets]
    expected_defaults = ["SDXL Base", "Base + Refiner", "Fast Generation"]
    
    for expected in expected_defaults:
        assert expected in preset_names, f"Missing default preset: {expected}"
        print(f"✅ Found default preset: {expected}")
    
    # Check that default presets are marked as default
    default_presets = [p for p in presets if p.is_default]
    assert len(default_presets) >= 3
    print(f"✅ Found {len(default_presets)} default presets")
    
    # Clean up
    if os.path.exists("test_default_presets.json"):
        os.unlink("test_default_presets.json")
    
    print("✅ Default presets test passed!")

def test_preset_serialization():
    """Test that presets can be saved and loaded correctly"""
    print("\n🧪 Testing preset serialization...")
    
    filename = "test_serialization_presets.json"
    
    # Create manager and add a preset
    manager1 = PresetManager(filename)
    settings = {
        "prompt": "serialization test",
        "model_name": "test_model.safetensors",
        "steps": 25,
        "cfg_scale": 7.5
    }
    
    preset = manager1.create_preset(
        name="Serialization Test Preset",
        description="Testing save/load",
        settings=settings
    )
    
    # Create a new manager instance (simulates restart)
    manager2 = PresetManager(filename)
    
    # Verify preset was loaded correctly
    loaded_preset = manager2.get_preset(preset.id)
    assert loaded_preset is not None
    assert loaded_preset.name == preset.name
    assert loaded_preset.settings == preset.settings
    assert loaded_preset.hash == preset.hash
    
    print("✅ Preset serialization works correctly")
    
    # Clean up
    if os.path.exists(filename):
        os.unlink(filename)
    
    print("✅ Serialization test passed!")

def main():
    """Run all preset tests"""
    print("🚀 Starting Preset System Tests")
    print("=" * 50)
    
    try:
        test_preset_basic_functionality()
        test_default_presets()
        test_preset_serialization()
        
        print("\n" + "=" * 50)
        print("🎉 All preset system tests passed!")
        print("The preset system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 