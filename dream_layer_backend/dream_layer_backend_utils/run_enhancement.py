"""
Run Enhancement Utilities
Provides ClipScore integration and run data enhancement using existing metrics infrastructure
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import asdict

def enhance_runs_with_clipscore(runs_list: List[Any]) -> List[Dict[str, Any]]:
    """
    Enhance run data with ClipScore using existing metrics infrastructure
    
    Args:
        runs_list: List of RunConfig objects or dictionaries
        
    Returns:
        List of dictionaries with ClipScore data included
    """
    try:
        # Import the existing ClipScore calculator
        from .clip_score_metrics import get_clip_calculator
        
        # Import database integration
        sys.path.append(os.path.join('..', 'data', 'scripts'))
        from database import DreamLayerDB
        
        db = DreamLayerDB()
        clip_calculator = get_clip_calculator()
        
        enhanced_runs = []
        
        for run in runs_list:
            # Convert to dict if it's a dataclass
            run_dict = run if isinstance(run, dict) else asdict(run)
            
            # Try to get existing ClipScore from database
            clip_score = get_clipscore_from_database(db, run_dict['run_id'])
            
            if clip_score is None and clip_calculator:
                # Calculate ClipScore if not exists
                clip_score = calculate_clipscore_for_run(
                    clip_calculator, 
                    run_dict, 
                    db
                )
            
            # Add ClipScore to run data
            run_dict['clip_score_mean'] = clip_score
            enhanced_runs.append(run_dict)
        
        return enhanced_runs
        
    except Exception as e:
        print(f"Error enhancing runs with ClipScore: {e}")
        # Return original runs if enhancement fails
        return [run if isinstance(run, dict) else asdict(run) for run in runs_list]

def get_clipscore_from_database(db: Any, run_id: str) -> Optional[float]:
    """Get existing ClipScore from database"""
    try:
        with db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT metric_value FROM metrics WHERE run_id = ? AND metric_name = 'clip_score_mean'",
                (run_id,)
            )
            result = cursor.fetchone()
            return result['metric_value'] if result else None
    except Exception as e:
        print(f"Error getting ClipScore from database for {run_id}: {e}")
        return None

def calculate_clipscore_for_run(clip_calculator: Any, run_dict: Dict[str, Any], db: Any) -> Optional[float]:
    """Calculate ClipScore for a run and save to database"""
    try:
        # Get image path
        image_path = get_image_path_for_run(run_dict)
        if not image_path or not os.path.exists(image_path):
            return None
        
        # Get prompt
        prompt = run_dict.get('prompt', '')
        if not prompt:
            return None
        
        # Calculate ClipScore using existing metrics infrastructure
        clip_score = clip_calculator.compute_clip_score(prompt, image_path)
        
        # Save to database
        save_clipscore_to_database(db, run_dict['run_id'], run_dict['timestamp'], clip_score)
        
        print(f"✅ Calculated ClipScore {clip_score:.4f} for run {run_dict['run_id'][:8]}...")
        return clip_score
        
    except Exception as e:
        print(f"Error calculating ClipScore for run {run_dict['run_id']}: {e}")
        return None

def get_image_path_for_run(run_dict: Dict[str, Any]) -> Optional[str]:
    """Get full image path for a run"""
    try:
        generated_images = run_dict.get('generated_images', [])
        if not generated_images:
            return None
        
        # Use first generated image
        filename = generated_images[0]
        
        # Construct full path
        output_dir = os.path.join('..', '..', 'Dream_Layer_Resources', 'output')
        full_path = os.path.abspath(os.path.join(output_dir, filename))
        
        return full_path if os.path.exists(full_path) else None
        
    except Exception as e:
        print(f"Error getting image path: {e}")
        return None

def save_clipscore_to_database(db: Any, run_id: str, timestamp: str, clip_score: float) -> bool:
    """Save ClipScore to database"""
    try:
        with db.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO metrics (
                    run_id, timestamp, metric_name, metric_value
                ) VALUES (?, ?, ?, ?)
            """, (run_id, timestamp, 'clip_score_mean', clip_score))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error saving ClipScore to database: {e}")
        return False

def batch_calculate_clipscore(run_ids: Optional[List[str]] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Calculate ClipScore for multiple runs in batch
    
    Args:
        run_ids: Optional list of specific run IDs to process
        limit: Maximum number of runs to process
        
    Returns:
        Dictionary with calculation statistics
    """
    try:
        from .clip_score_metrics import get_clip_calculator
        sys.path.append(os.path.join('..', 'data', 'scripts'))
        from database import DreamLayerDB
        
        db = DreamLayerDB()
        clip_calculator = get_clip_calculator()
        
        if not clip_calculator:
            return {"error": "ClipScore calculator not available"}
        
        # Get runs to process
        if run_ids:
            # Process specific runs
            runs_to_process = []
            for run_id in run_ids:
                run_data = db.get_run(run_id)
                if run_data:
                    runs_to_process.append(run_data)
        else:
            # Get runs without ClipScore
            with db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT r.* FROM runs r
                    LEFT JOIN metrics m ON r.run_id = m.run_id AND m.metric_name = 'clip_score_mean'
                    WHERE m.run_id IS NULL
                    ORDER BY r.timestamp DESC
                    LIMIT ?
                """, (limit,))
                runs_to_process = [dict(row) for row in cursor.fetchall()]
        
        # Calculate ClipScore for each run
        stats = {
            "total": len(runs_to_process),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        for run_data in runs_to_process:
            clip_score = calculate_clipscore_for_run(clip_calculator, run_data, db)
            
            if clip_score is not None:
                stats["success"] += 1
                stats["results"].append({
                    "run_id": run_data["run_id"],
                    "clip_score": clip_score
                })
            else:
                stats["failed"] += 1
        
        print(f"Batch ClipScore calculation: {stats['success']} success, {stats['failed']} failed")
        return stats
        
    except Exception as e:
        return {"error": str(e)}

# Convenience functions for easy import
def get_enhanced_runs(runs_list: List[Any]) -> List[Dict[str, Any]]:
    """Convenience function to get runs with ClipScore"""
    return enhance_runs_with_clipscore(runs_list)

def calculate_missing_clipscores(limit: int = 50) -> Dict[str, Any]:
    """Convenience function to calculate missing ClipScores"""
    return batch_calculate_clipscore(limit=limit)

if __name__ == "__main__":
    # Test the enhancement functionality
    print("🧪 Testing Run Enhancement with ClipScore")
    print("=" * 45)
    
    # Import run registry for testing
    sys.path.append('..')
    from run_registry import registry
    
    # Test with first 3 runs
    runs = registry.get_all_runs()[:3]
    enhanced = enhance_runs_with_clipscore(runs)
    
    for i, run in enumerate(enhanced):
        print(f"Run {i+1}:")
        print(f"  ID: {run['run_id'][:8]}...")
        print(f"  Model: {run['model']}")
        print(f"  Prompt: {run['prompt'][:30]}...")
        print(f"  ClipScore: {run.get('clip_score_mean', 'None')}")
        print()
