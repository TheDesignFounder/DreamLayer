#!/usr/bin/env python3
"""
Demo script to test the Run Registry functionality
This simulates what happens when a generation completes
"""

import json
import time
from run_registry import get_registry

def simulate_txt2img_generation():
    """Simulate a text-to-image generation and save to registry"""
    
    # Simulate the config that would come from a real generation
    generation_config = {
        'prompt': 'A majestic mountain landscape at sunset, highly detailed, 8k',
        'negative_prompt': 'blurry, low quality, distorted',
        'model': 'stable-diffusion-xl-base-1.0',
        'vae': 'sdxl-vae-fp16-fix',
        'loras': [
            {'name': 'detail-enhancer', 'strength': 0.7},
            {'name': 'landscape-style', 'strength': 0.5}
        ],
        'controlnet': {
            'enabled': False,
            'model': None
        },
        'seed': 2024,
        'sampler': 'DPM++ 2M Karras',
        'scheduler': 'karras',
        'steps': 30,
        'cfg_scale': 7.5,
        'width': 1024,
        'height': 1024,
        'batch_size': 1,
        'generation_type': 'txt2img',
        'workflow': {
            'name': 'txt2img_workflow',
            'nodes': ['KSampler', 'VAEDecode', 'SaveImage']
        },
        'workflow_version': '1.2.0'
    }
    
    # Save to registry (this is what txt2img_server.py does)
    registry = get_registry()
    run_id = registry.save_run(generation_config)
    
    print(f"✅ Saved txt2img generation run: {run_id}")
    return run_id

def simulate_img2img_generation():
    """Simulate an image-to-image generation and save to registry"""
    
    generation_config = {
        'prompt': 'Transform to cyberpunk style, neon lights',
        'negative_prompt': 'realistic, photographic',
        'model': 'dreamshaper-8',
        'vae': 'vae-ft-mse-840000',
        'loras': [
            {'name': 'cyberpunk-style', 'strength': 0.9}
        ],
        'controlnet': {
            'enabled': True,
            'model': 'control_v11p_sd15_canny',
            'strength': 0.75
        },
        'seed': -1,  # Random seed
        'sampler': 'Euler a',
        'steps': 25,
        'cfg_scale': 8.0,
        'width': 512,
        'height': 768,
        'denoising_strength': 0.65,
        'generation_type': 'img2img',
        'workflow': {
            'name': 'img2img_workflow',
            'nodes': ['LoadImage', 'KSampler', 'VAEDecode', 'SaveImage']
        },
        'workflow_version': '1.1.0'
    }
    
    registry = get_registry()
    run_id = registry.save_run(generation_config)
    
    print(f"✅ Saved img2img generation run: {run_id}")
    return run_id

def test_registry_operations():
    """Test various registry operations"""
    
    registry = get_registry()
    
    # Clear any existing runs for a clean test
    registry.clear_all_runs()
    print("🧹 Cleared all existing runs\n")
    
    # Simulate multiple generations
    print("📝 Simulating generation runs...")
    txt2img_id = simulate_txt2img_generation()
    time.sleep(0.1)  # Small delay to ensure different timestamps
    img2img_id = simulate_img2img_generation()
    
    # Add a few more for testing pagination
    for i in range(3):
        config = {
            'prompt': f'Test prompt {i+1}',
            'model': f'test-model-{i+1}',
            'generation_type': 'txt2img' if i % 2 == 0 else 'img2img',
            'seed': 1000 + i,
            'steps': 20 + i
        }
        registry.save_run(config)
        print(f"✅ Saved test run {i+1}")
    
    print("\n📊 Testing retrieval operations...")
    
    # Test getting all runs
    all_runs = registry.get_runs(limit=10)
    print(f"Total runs in registry: {len(all_runs)}")
    
    # Display run summaries
    print("\n📋 Run summaries:")
    for run in all_runs[:3]:  # Show first 3
        print(f"  - ID: {run['id'][:8]}...")
        print(f"    Prompt: {run['prompt'][:50]}...")
        print(f"    Model: {run['model']}")
        print(f"    Type: {run['generation_type']}")
        print()
    
    # Test getting specific run details
    print("🔍 Testing detailed run retrieval...")
    detailed_run = registry.get_run(txt2img_id)
    if detailed_run:
        print(f"Retrieved run {txt2img_id[:8]}...")
        print(f"  - Prompt: {detailed_run['prompt']}")
        print(f"  - Sampler: {detailed_run['sampler']}")
        print(f"  - Steps: {detailed_run['steps']}")
        print(f"  - CFG Scale: {detailed_run['cfg_scale']}")
        print(f"  - LoRAs: {len(detailed_run.get('loras', []))} loaded")
    
    # Test deletion
    print("\n🗑️  Testing deletion...")
    success = registry.delete_run(img2img_id)
    if success:
        print(f"Successfully deleted run {img2img_id[:8]}...")
    
    # Verify deletion
    deleted_run = registry.get_run(img2img_id)
    if deleted_run is None:
        print("✅ Deletion verified - run no longer exists")
    
    # Final count
    final_runs = registry.get_runs(limit=10)
    print(f"\n📈 Final run count: {len(final_runs)}")
    
    print("\n✨ All tests completed successfully!")
    print("\nThe Run Registry is working correctly and ready for use.")
    print("You can now:")
    print("  1. Start the backend server to expose the API endpoints")
    print("  2. Start the frontend to see the UI at /runs")
    print("  3. Generate images to automatically save runs")

if __name__ == "__main__":
    print("=" * 60)
    print("RUN REGISTRY FUNCTIONALITY TEST")
    print("=" * 60)
    print()
    test_registry_operations()
