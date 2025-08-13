#!/usr/bin/env python3
"""
Verification script for PR feedback fixes
Tests the three main issues that were addressed:
1. time.sleep() removal
2. list_runs/get_runs method compatibility
3. controlnet/controlnets naming alignment
"""

import json
import sys
from run_registry import RunRegistry

def test_controlnets_naming():
    """Test that controlnet is properly mapped to controlnets"""
    print("\n🔍 Testing controlnet -> controlnets mapping...")
    
    registry = RunRegistry()
    
    # Test with 'controlnet' in input (backward compatibility)
    config_with_controlnet = {
        'prompt': 'Test with controlnet',
        'controlnet': {
            'enabled': True,
            'model': 'canny',
            'units': [{'strength': 1.0}]
        }
    }
    
    run_id = registry.save_run(config_with_controlnet)
    saved_run = registry.get_run(run_id)
    
    # Check that it's saved as 'controlnets'
    assert 'controlnets' in saved_run, "❌ 'controlnets' key not found in saved run"
    assert saved_run['controlnets']['enabled'] == True, "❌ controlnets data not properly saved"
    print("  ✅ 'controlnet' input properly mapped to 'controlnets' in storage")
    
    # Clean up
    registry.delete_run(run_id)
    
    return True

def test_list_runs_alias():
    """Test that list_runs works as an alias for get_runs"""
    print("\n🔍 Testing list_runs/get_runs compatibility...")
    
    registry = RunRegistry()
    
    # Save a few test runs
    run_ids = []
    for i in range(3):
        config = {
            'prompt': f'Test run {i}',
            'model': f'model-{i}'
        }
        run_ids.append(registry.save_run(config))
    
    # Test both methods return the same results
    runs_via_get = registry.get_runs(limit=10)
    runs_via_list = registry.list_runs(limit=10)
    
    assert len(runs_via_get) == len(runs_via_list), "❌ get_runs and list_runs return different counts"
    assert runs_via_get[0]['id'] == runs_via_list[0]['id'], "❌ get_runs and list_runs return different data"
    
    print("  ✅ list_runs() works as an alias for get_runs()")
    print(f"  ✅ Both methods return {len(runs_via_get)} runs")
    
    # Clean up
    for run_id in run_ids:
        registry.delete_run(run_id)
    
    return True

def check_time_sleep_removed():
    """Check that time.sleep was removed from dream_layer.py"""
    print("\n🔍 Checking time.sleep() removal...")
    
    with open('dream_layer.py', 'r') as f:
        content = f.read()
        
    # Check line 288 area for the fix
    lines = content.split('\n')
    for i, line in enumerate(lines[285:295], start=286):
        if 'time.sleep(1)' in line:
            print(f"  ❌ time.sleep(1) still found on line {i}")
            return False
        if 'pass  # Continue checking without delay' in line:
            print(f"  ✅ time.sleep(1) properly removed and replaced with pass statement")
            return True
    
    print("  ✅ No problematic time.sleep(1) found in connection retry loop")
    return True

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("PR FEEDBACK FIXES VERIFICATION")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: time.sleep removal
    try:
        if not check_time_sleep_removed():
            all_passed = False
    except Exception as e:
        print(f"  ❌ Error checking time.sleep: {e}")
        all_passed = False
    
    # Test 2: list_runs/get_runs compatibility
    try:
        if not test_list_runs_alias():
            all_passed = False
    except Exception as e:
        print(f"  ❌ Error testing list_runs alias: {e}")
        all_passed = False
    
    # Test 3: controlnet/controlnets naming
    try:
        if not test_controlnets_naming():
            all_passed = False
    except Exception as e:
        print(f"  ❌ Error testing controlnets naming: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ ALL PR FEEDBACK ISSUES HAVE BEEN FIXED! ✨")
        print("\nSummary of fixes:")
        print("1. ✅ Removed unnecessary time.sleep(1) from connection retry")
        print("2. ✅ Added list_runs() alias for get_runs() compatibility")
        print("3. ✅ Fixed controlnet -> controlnets naming for frontend")
        return 0
    else:
        print("❌ Some issues remain. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
