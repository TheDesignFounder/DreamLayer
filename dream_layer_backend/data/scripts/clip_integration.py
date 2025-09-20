"""
Enhanced ClipScore Integration with Database
Handles ClipScore calculation with proper path resolution using database
"""

import os
import logging
from typing import Optional, Dict, Any, List
from queries import DreamLayerQueries

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseClipScoreCalculator:
    """ClipScore calculator that uses database for path resolution"""
    
    def __init__(self):
        self.queries = DreamLayerQueries()
        self.clip_calculator = None
        self._initialize_clip_calculator()
    
    def _initialize_clip_calculator(self):
        """Initialize the ClipScore calculator"""
        try:
            from dream_layer_backend_utils.clip_score_metrics import get_clip_calculator
            self.clip_calculator = get_clip_calculator()
            if self.clip_calculator:
                logger.info("ClipScore calculator initialized successfully")
            else:
                logger.error("Failed to initialize ClipScore calculator")
        except ImportError as e:
            logger.error(f"Could not import ClipScore calculator: {e}")
    
    def calculate_for_run(self, run_id: str, image_index: int = 0) -> Optional[float]:
        """Calculate ClipScore for a specific run and image"""
        if not self.clip_calculator:
            logger.error("ClipScore calculator not available")
            return None
        
        try:
            # Get run data
            run = self.queries.db.get_run(run_id)
            if not run:
                logger.error(f"Run {run_id} not found in database")
                return None
            
            # Get image path from database
            image_path = self.queries.get_image_path_for_clip_score(run_id, image_index)
            if not image_path:
                logger.error(f"No image path found for run {run_id}")
                return None
            
            # Get prompt
            prompt = run.get('prompt', '')
            if not prompt:
                logger.error(f"No prompt found for run {run_id}")
                return None
            
            # Calculate ClipScore
            clip_score = self.clip_calculator.compute_clip_score(prompt, image_path)
            
            # Save to database
            if self.queries.save_clip_score(run_id, run['timestamp'], clip_score):
                logger.info(f"Calculated and saved ClipScore {clip_score:.4f} for run {run_id}")
                return clip_score
            else:
                logger.error(f"Failed to save ClipScore for run {run_id}")
                return clip_score  # Return value even if save failed
            
        except Exception as e:
            logger.error(f"Error calculating ClipScore for run {run_id}: {e}")
            return None
    
    def calculate_batch(self, limit: int = 2000) -> Dict[str, Any]:
        """Calculate ClipScore for multiple runs that don't have it"""
        if not self.clip_calculator:
            logger.error("ClipScore calculator not available")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Get runs without ClipScore
        runs_without_clip = self.queries.get_runs_without_clip_score(limit)
        
        stats = {
            "total": len(runs_without_clip),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        logger.info(f"Calculating ClipScore for {stats['total']} runs...")
        
        for run in runs_without_clip:
            run_id = run['run_id']
            if not self.queries.can_compute_metrics_for_run(run_id): continue
            clip_score = self.calculate_for_run(run_id)
            
            if clip_score is not None:
                stats["success"] += 1
                stats["results"].append({
                    "run_id": run_id,
                    "clip_score": clip_score,
                    "prompt": run.get('prompt', '')[:50] + "..."
                })
            else:
                stats["failed"] += 1
        
        logger.info(f"Batch calculation complete: {stats['success']} success, {stats['failed']} failed")
        return stats
    
    def recalculate_all(self, force: bool = False) -> Dict[str, Any]:
        """Recalculate ClipScore for all runs (use with caution)"""
        if not force:
            logger.warning("Use recalculate_all(force=True) to recalculate all ClipScores")
            return {"error": "Force parameter required"}
        
        if not self.clip_calculator:
            logger.error("ClipScore calculator not available")
            return {"success": 0, "failed": 0, "total": 0}
        
        # Get all runs
        all_runs = self.queries.db.get_all_runs()
        
        stats = {
            "total": len(all_runs),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        logger.info(f"Recalculating ClipScore for {stats['total']} runs...")
        
        for run in all_runs:
            run_id = run['run_id']
            
            try:
                # Get image path
                image_path = self.queries.get_image_path_for_clip_score(run_id)
                if not image_path:
                    stats["failed"] += 1
                    continue
                
                # Calculate ClipScore
                prompt = run.get('prompt', '')
                if not prompt:
                    stats["failed"] += 1
                    continue
                
                clip_score = self.clip_calculator.compute_clip_score(prompt, image_path)
                
                # Save to database (will overwrite existing)
                if self.queries.save_clip_score(run_id, run['timestamp'], clip_score):
                    stats["success"] += 1
                    stats["results"].append({
                        "run_id": run_id,
                        "clip_score": clip_score
                    })
                else:
                    stats["failed"] += 1
                
            except Exception as e:
                logger.error(f"Error recalculating ClipScore for run {run_id}: {e}")
                stats["failed"] += 1
        
        logger.info(f"Recalculation complete: {stats['success']} success, {stats['failed']} failed")
        return stats

def calculate_missing_clip_scores(limit: int = 2000) -> Dict[str, Any]:
    """Convenience function to calculate missing ClipScores"""
    calculator = DatabaseClipScoreCalculator()
    return calculator.calculate_batch(limit)

def compute_clip_score_for_run(run_id: str) -> Optional[float]:
    """Convenience function to calculate ClipScore for a single run"""
    calculator = DatabaseClipScoreCalculator()
    return calculator.calculate_for_run(run_id)

if __name__ == "__main__":
    # Test ClipScore calculation
    calculator = DatabaseClipScoreCalculator()
    
    # Calculate for runs without ClipScore
    stats = calculator.calculate_batch(limit=10)
    print(f"Calculated ClipScore for {stats['success']}/{stats['total']} runs")
    
    # Show results
    for result in stats['results'][:5]:
        print(f"Run {result['run_id']}: ClipScore {result['clip_score']:.4f}")
