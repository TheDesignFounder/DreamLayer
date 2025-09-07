#!/usr/bin/env python3
"""
Test frontend gallery data sync by simulating a frontend image generation and sync
"""

import requests
import json
from datetime import datetime, timezone

def simulate_frontend_image_generation():
    """Simulate what happens when frontend generates images and syncs to backend"""
    
    # Simulate gallery data that frontend would send after generating images
    simulated_gallery_data = {
        "txt2img": [
            {
                "id": f"frontend_sim_{datetime.now().timestamp()}",
                "filename": "DreamLayer_00027_.png",
                "url": "http://localhost:5001/api/images/DreamLayer_00027_.png",
                "prompt": "test auto sync image",
                "negativePrompt": "blurry", 
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "euler",
                    "steps": 15,
                    "cfg_scale": 7.0,
                    "width": 256,
                    "height": 256,
                    "seed": 123456789,
                    "batch_size": 1
                }
            }
        ],
        "img2img": []
    }
    
    print("🎯 Simulating frontend gallery data sync...")
    print(f"Sending data for {len(simulated_gallery_data['txt2img'])} txt2img images")
    
    # Send to backend
    try:
        response = requests.post(
            'http://localhost:5002/api/gallery-data',
            json=simulated_gallery_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Gallery data sync successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Gallery data sync failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error syncing gallery data: {e}")
        return False

def test_reports_generation():
    """Test report generation after gallery sync"""
    print("\n📋 Testing report generation...")
    
    try:
        response = requests.post(
            'http://localhost:5002/api/reports/generate',
            json={'filename': 'frontend_sync_test_report.zip'},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report generation successful!")
            print(f"Total images in report: {result.get('total_images')}")
            print(f"Generation types: {result.get('generation_types')}")
            print(f"File size: {result.get('bundle_size_bytes')} bytes")
            print(f"CSV valid: {result.get('csv_validation', {}).get('valid')}")
            print(f"Paths valid: {result.get('path_validation', {}).get('valid')}")
            return True
        else:
            print(f"❌ Report generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

def main():
    print("🧪 Testing Frontend → Backend Gallery Sync → Reports Workflow")
    print("=" * 60)
    
    # Step 1: Simulate frontend sending gallery data
    if simulate_frontend_image_generation():
        # Step 2: Test report generation
        if test_reports_generation():
            print("\n🎉 Complete workflow test PASSED!")
            print("Frontend auto-sync is working correctly.")
        else:
            print("\n❌ Report generation test FAILED")
    else:
        print("\n❌ Gallery sync test FAILED")

if __name__ == "__main__":
    main()
