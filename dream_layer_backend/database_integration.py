"""
Database Integration Wrapper for Existing report_bundle.py
Provides backward-compatible interface while using database backend
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional

# Add data scripts to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, 'data', 'scripts'))

try:
    from data.scripts.queries import DreamLayerQueries, get_csv_data
    from data.scripts.clip_integration import calculate_missing_clip_scores
    from data.scripts.fid_integration import calculate_missing_fid_scores
    from data.scripts.composition_integration import calculate_missing_composition_metrics
    from data.scripts.migration import DreamLayerMigration
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Database not available: {e}")
    DATABASE_AVAILABLE = False

class DatabaseIntegration:
    """Integration layer between database and existing code"""
    
    def __init__(self):
        self.queries = DreamLayerQueries() if DATABASE_AVAILABLE else None
        self.migration_done = False
    
    def ensure_migration(self):
        """Ensure data is migrated to database"""
        if not DATABASE_AVAILABLE or self.migration_done:
            return
        
        try:
            # Check if database has data
            if self.queries:
                runs = self.queries.db.get_all_runs(limit=1)
                if not runs:
                    print("Running database migration...")
                    migration = DreamLayerMigration()
                    stats = migration.migrate_all()
                    print(f"Migration complete: {stats['success']} runs migrated")
                
                self.migration_done = True
        except Exception as e:
            print(f"Migration error: {e}")
    
    def get_runs_for_csv(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get runs formatted for CSV export"""
        if not DATABASE_AVAILABLE:
            return []
        
        self.ensure_migration()
        
        # Calculate missing ClipScores
        try:
            stats = calculate_missing_clip_scores(limit=50)
            if stats['success'] > 0:
                print(f"Calculated ClipScore for {stats['success']} additional runs")
        except Exception as e:
            print(f"ClipScore calculation error: {e}")
        
        # Calculate missing FiD scores
        try:
            fid_stats = calculate_missing_fid_scores(limit=50)
            if fid_stats['success'] > 0:
                print(f"Calculated FiD for {fid_stats['success']} additional runs")
        except Exception as e:
            print(f"FiD calculation error: {e}")
        
        # Calculate missing composition metrics
        try:
            comp_stats = calculate_missing_composition_metrics(limit=50)
            if comp_stats['success'] > 0:
                print(f"Calculated composition metrics for {comp_stats['success']} additional runs")
        except Exception as e:
            print(f"Composition metrics calculation error: {e}")
        
        # Get CSV data
        return get_csv_data(limit)
    
    def is_database_enabled(self) -> bool:
        """Check if database is available and working"""
        return DATABASE_AVAILABLE and self.queries is not None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.is_database_enabled():
            return {"error": "Database not available"}
        
        try:
            self.ensure_migration()
            
            all_runs = self.queries.db.get_all_runs()
            metrics_summary = self.queries.get_metrics_summary()
            runs_without_clip = self.queries.get_runs_without_clip_score()
            
            return {
                "total_runs": len(all_runs),
                "runs_with_clip_score": len(all_runs) - len(runs_without_clip),
                "runs_without_clip_score": len(runs_without_clip),
                "metrics_available": list(metrics_summary.keys()),
                "database_path": self.queries.db.db_path
            }
        except Exception as e:
            return {"error": str(e)}

# Global instance for easy import
db_integration = DatabaseIntegration()

def get_database_csv_data(limit: int = None) -> List[Dict[str, Any]]:
    """Convenience function to get CSV data from database"""
    return db_integration.get_runs_for_csv(limit)

def ensure_clip_scores_calculated():
    """Convenience function to calculate missing ClipScores"""
    if db_integration.is_database_enabled():
        try:
            stats = calculate_missing_clip_scores(limit=100)
            return stats
        except Exception as e:
            print(f"Error calculating ClipScores: {e}")
            return {"error": str(e)}
    return {"error": "Database not available"}

def ensure_fid_scores_calculated():
    """Convenience function to calculate missing FiD scores"""
    if db_integration.is_database_enabled():
        try:
            stats = calculate_missing_fid_scores(limit=100)
            return stats
        except Exception as e:
            print(f"Error calculating FiD scores: {e}")
            return {"error": str(e)}
    return {"error": "Database not available"}

def ensure_composition_metrics_calculated():
    """Convenience function to calculate missing composition metrics"""
    if db_integration.is_database_enabled():
        try:
            stats = calculate_missing_composition_metrics(limit=100)
            return stats
        except Exception as e:
            print(f"Error calculating composition metrics: {e}")
            return {"error": str(e)}
    return {"error": "Database not available"}

if __name__ == "__main__":
    # Test the integration
    integration = DatabaseIntegration()
    
    print("Database Integration Test")
    print("=" * 30)
    
    # Check database status
    if integration.is_database_enabled():
        print("✓ Database available")
        
        # Get stats
        stats = integration.get_database_stats()
        print(f"✓ Total runs: {stats.get('total_runs', 0)}")
        print(f"✓ Runs with ClipScore: {stats.get('runs_with_clip_score', 0)}")
        print(f"✓ Database path: {stats.get('database_path', 'unknown')}")
        
        # Test CSV generation
        csv_data = integration.get_runs_for_csv(limit=3)
        print(f"✓ CSV data generated: {len(csv_data)} runs")
        
        if csv_data:
            sample = csv_data[0]
            print(f"✓ Sample ClipScore: {sample.get('clip_score_mean', 0.0)}")
    else:
        print("✗ Database not available")
