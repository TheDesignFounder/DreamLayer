"""
Direct Database Integration for txt2img/img2img Servers
Allows direct database writes without going through run_registry API
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

def save_run_to_database(generation_data: Dict[str, Any], generated_images: List[str], generation_type: str) -> bool:
    """
    Save a completed run directly to database using unified functions
    """
    try:
        from .unified_database_queries import save_run_to_database as save_run_func, save_assets_to_database, save_clipscore_to_database
        
        # Create run data structure
        run_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Ensure generated_images is properly formatted
        if not generated_images:
            generated_images = []
        
        run_data = {
            'run_id': run_id,
            'timestamp': timestamp,
            'model': generation_data.get('model') or generation_data.get('model_name', 'unknown'),
            'vae': generation_data.get('vae'),
            'loras': generation_data.get('loras', []),
            'controlnets': generation_data.get('controlnets', []),
            'prompt': generation_data.get('prompt', ''),
            'negative_prompt': generation_data.get('negative_prompt', ''),
            'seed': generation_data.get('seed', 0),
            'sampler': generation_data.get('sampler', 'euler'),
            'steps': generation_data.get('steps', 20),
            'cfg_scale': generation_data.get('cfg_scale', 7.0),
            'width': generation_data.get('width', 512),
            'height': generation_data.get('height', 512),
            'batch_size': generation_data.get('batch_size', 1),
            'batch_count': generation_data.get('batch_count', 1),
            'workflow': generation_data.get('workflow', {}),
            'version': '1.0.0',
            'generation_type': generation_type,
            'generated_images': generated_images  # Add this to run data
        }
        
        # Save run to database using unified function
        success = save_run_func(run_data)
        if not success:
            print(f"❌ Failed to save run {run_id} to database")
            return False
        
        # Save assets to database using unified function
        if generated_images:
            asset_success = save_assets_to_database(run_id, timestamp, generated_images)
            if not asset_success:
                print(f"⚠️ Failed to save assets for run {run_id}")
        
        print(f"✅ Saved run {run_id} to database with {len(generated_images)} images")
        
        # Calculate ClipScore immediately (not async)
        try:
            if generated_images and run_data.get('prompt'):
                clip_score = calculate_clipscore_sync(run_data, generated_images)
                if clip_score is not None:
                    save_clipscore_to_database(run_id, timestamp, clip_score)
                    print(f"✅ Calculated and saved ClipScore {clip_score:.4f} for run {run_id[:8]}...")
                else:
                    print(f"⚠️ ClipScore calculation returned None for run {run_id[:8]}...")
        except Exception as e:
            print(f"⚠️ ClipScore calculation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving run to database: {e}")
        return False

def calculate_clipscore_sync(run_data: Dict[str, Any], generated_images: List[str]) -> Optional[float]:
    """Calculate ClipScore synchronously for immediate database save"""
    try:
        from .clip_score_metrics import get_clip_calculator
        
        clip_calculator = get_clip_calculator()
        if not clip_calculator:
            print("⚠️ ClipScore calculator not available")
            return None
        
        # Get first image path
        if not generated_images:
            print("⚠️ No generated images for ClipScore calculation")
            return None
        
        # Fix: Use correct output directory path
        output_dir = os.path.join('..', 'Dream_Layer_Resources', 'output')
        image_path = os.path.abspath(os.path.join(output_dir, generated_images[0]))
        
        if not os.path.exists(image_path):
            print(f"⚠️ Image file not found: {image_path}")
            return None
        
        # Calculate ClipScore
        prompt = run_data.get('prompt', '')
        if not prompt:
            print("⚠️ No prompt for ClipScore calculation")
            return None
        
        clip_score = clip_calculator.compute_clip_score(prompt, image_path)
        return clip_score
        
    except Exception as e:
        print(f"⚠️ ClipScore calculation error: {e}")
        return None

def save_clipscore_to_database(run_id: str, timestamp: str, clip_score: float):
    """Save ClipScore metric to database"""
    try:
        sys.path.append(os.path.join('..', 'data', 'scripts'))
        from database import DreamLayerDB
        
        db = DreamLayerDB()
        
        with db.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO metrics (
                    run_id, timestamp, metric_name, metric_value
                ) VALUES (?, ?, ?, ?)
            """, (run_id, timestamp, 'clip_score_mean', clip_score))
            conn.commit()
        
    except Exception as e:
        print(f"Error saving ClipScore to database: {e}")

def save_run_with_fallback(generation_data: Dict[str, Any], generated_images: List[str], generation_type: str) -> Dict[str, Any]:
    """
    Save run to database with fallback to API if database fails
    
    Returns:
        Dict with status information
    """
    # Try direct database save first
    db_success = save_run_to_database(generation_data, generated_images, generation_type)
    
    if db_success:
        return {
            'success': True,
            'method': 'database',
            'message': 'Run saved directly to database'
        }
    
    # Fallback to API method
    try:
        import requests
        from dataclasses import asdict
        
        # Create run config (reuse existing function)
        sys.path.append('..')
        from run_registry import create_run_config_from_generation_data
        
        run_config = create_run_config_from_generation_data(
            generation_data, generated_images, generation_type
        )
        
        # Send to run registry API
        response = requests.post(
            "http://localhost:5005/api/runs",
            json=asdict(run_config),
            timeout=5
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'method': 'api',
                'message': 'Run saved via API fallback'
            }
        else:
            return {
                'success': False,
                'method': 'api',
                'message': f'API fallback failed: {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'method': 'fallback',
            'message': f'Both database and API failed: {e}'
        }

# Convenience function for easy integration
def save_generation_run(generation_data: Dict[str, Any], generated_images: List[str], generation_type: str) -> bool:
    """
    Main function to save a generation run
    Use this in txt2img_server.py and img2img_server.py
    """
    result = save_run_with_fallback(generation_data, generated_images, generation_type)
    
    if result['success']:
        print(f"✅ Run saved successfully via {result['method']}: {result['message']}")
        return True
    else:
        print(f"❌ Failed to save run: {result['message']}")
        return False

if __name__ == "__main__":
    # Test the direct database integration
    print("🧪 Testing Direct Database Integration")
    print("=" * 40)
    
    # Test data
    test_generation_data = {
        'model': 'test-model',
        'prompt': 'test prompt for direct database integration',
        'negative_prompt': '',
        'seed': 12345,
        'sampler': 'euler',
        'steps': 20,
        'cfg_scale': 7.0,
        'width': 512,
        'height': 512,
        'batch_size': 1,
        'batch_count': 1
    }
    
    test_images = ['test_image.png']
    
    # Test save
    success = save_generation_run(test_generation_data, test_images, 'txt2img')
    
    if success:
        print("🎉 Direct database integration test PASSED!")
    else:
        print("❌ Direct database integration test FAILED!")
