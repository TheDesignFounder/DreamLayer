"""
DreamLayer Migration Script
Converts existing run_registry.json data to SQLite database
Maintains backward compatibility and handles file path resolution
"""

import os
import json
import logging
from typing import Dict, List, Any
from database import DreamLayerDB

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DreamLayerMigration:
    """Handles migration from JSON to database"""
    
    def __init__(self, registry_path: str = None, output_dir: str = None):
        if registry_path is None:
            # Default path relative to dream_layer_backend
            script_dir = os.path.dirname(os.path.abspath(__file__))
            registry_path = os.path.join(script_dir, '..', '..', 'run_registry.json')
        
        if output_dir is None:
            # Default output directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, '..', '..', '..', 'Dream_Layer_Resources', 'output')
        
        self.registry_path = os.path.abspath(registry_path)
        self.output_dir = os.path.abspath(output_dir)
        self.db = DreamLayerDB()
        
        logger.info(f"Registry path: {self.registry_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def load_registry_data(self) -> Dict[str, Any]:
        """Load existing run_registry.json data"""
        try:
            if not os.path.exists(self.registry_path):
                logger.warning(f"Registry file not found: {self.registry_path}")
                return {}
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data)} runs from registry")
            return data
            
        except Exception as e:
            logger.error(f"Error loading registry data: {e}")
            return {}
    
    def migrate_single_run(self, run_id: str, run_data: Dict[str, Any]) -> bool:
        """Migrate a single run to database"""
        try:
            # Insert run data
            success = self.db.insert_run(run_data)
            if not success:
                logger.error(f"Failed to insert run {run_id}")
                return False
            
            # Insert assets if they exist
            generated_images = run_data.get('generated_images', [])
            if generated_images:
                success = self.db.insert_assets(
                    run_id, 
                    run_data.get('timestamp'),
                    generated_images,
                    self.output_dir
                )
                if not success:
                    logger.error(f"Failed to insert assets for run {run_id}")
                    return False
            
            logger.debug(f"Successfully migrated run {run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating run {run_id}: {e}")
            return False
    
    def migrate_all(self) -> Dict[str, int]:
        """Migrate all data from registry to database"""
        registry_data = self.load_registry_data()
        
        if not registry_data:
            logger.warning("No data to migrate")
            return {"total": 0, "success": 0, "failed": 0}
        
        stats = {"total": len(registry_data), "success": 0, "failed": 0}
        
        logger.info(f"Starting migration of {stats['total']} runs...")
        
        for run_id, run_data in registry_data.items():
            if self.migrate_single_run(run_id, run_data):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        logger.info(f"Migration complete: {stats['success']} success, {stats['failed']} failed")
        return stats
    
    def verify_migration(self) -> Dict[str, Any]:
        """Verify migration by comparing registry and database"""
        registry_data = self.load_registry_data()
        db_runs = {run['run_id']: run for run in self.db.get_all_runs()}
        
        verification = {
            "registry_count": len(registry_data),
            "database_count": len(db_runs),
            "missing_in_db": [],
            "extra_in_db": [],
            "asset_verification": {}
        }
        
        # Check for missing runs
        for run_id in registry_data:
            if run_id not in db_runs:
                verification["missing_in_db"].append(run_id)
        
        # Check for extra runs
        for run_id in db_runs:
            if run_id not in registry_data:
                verification["extra_in_db"].append(run_id)
        
        # Verify assets for each run
        for run_id in registry_data:
            if run_id in db_runs:
                registry_images = registry_data[run_id].get('generated_images', [])
                db_assets = self.db.get_run_assets(run_id)
                
                verification["asset_verification"][run_id] = {
                    "registry_images": len(registry_images),
                    "database_assets": len(db_assets),
                    "files_exist": sum(1 for asset in db_assets 
                                     if json.loads(asset.get('metadata', '{}')).get('exists', False))
                }
        
        return verification
    
    def check_file_paths(self) -> Dict[str, Any]:
        """Check file path resolution for all assets"""
        db_assets = []
        
        # Get all assets from database
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM assets")
            db_assets = [dict(row) for row in cursor.fetchall()]
        
        path_check = {
            "total_assets": len(db_assets),
            "files_exist": 0,
            "files_missing": 0,
            "missing_files": []
        }
        
        for asset in db_assets:
            full_path = asset.get('full_path')
            if full_path and os.path.exists(full_path):
                path_check["files_exist"] += 1
            else:
                path_check["files_missing"] += 1
                path_check["missing_files"].append({
                    "run_id": asset.get('run_id'),
                    "filename": asset.get('asset_value'),
                    "expected_path": full_path
                })
        
        return path_check

def run_migration():
    """Main migration function"""
    migration = DreamLayerMigration()
    
    # Run migration
    stats = migration.migrate_all()
    print(f"\nMigration Results:")
    print(f"Total runs: {stats['total']}")
    print(f"Successfully migrated: {stats['success']}")
    print(f"Failed: {stats['failed']}")
    
    # Verify migration
    verification = migration.verify_migration()
    print(f"\nVerification Results:")
    print(f"Registry runs: {verification['registry_count']}")
    print(f"Database runs: {verification['database_count']}")
    print(f"Missing in DB: {len(verification['missing_in_db'])}")
    print(f"Extra in DB: {len(verification['extra_in_db'])}")
    
    # Check file paths
    path_check = migration.check_file_paths()
    print(f"\nFile Path Check:")
    print(f"Total assets: {path_check['total_assets']}")
    print(f"Files exist: {path_check['files_exist']}")
    print(f"Files missing: {path_check['files_missing']}")
    
    if path_check['missing_files']:
        print(f"\nFirst 5 missing files:")
        for missing in path_check['missing_files'][:5]:
            print(f"  {missing['filename']} -> {missing['expected_path']}")
    
    return stats, verification, path_check

if __name__ == "__main__":
    run_migration()
