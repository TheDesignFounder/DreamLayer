"""
Run Registry Module
Handles storage and retrieval of generation runs with their configurations
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading

class RunRegistry:
    """Manages generation run history with thread-safe operations"""
    
    def __init__(self, storage_path: str = None):
        """Initialize the run registry with a storage path"""
        if storage_path is None:
            # Default to a runs directory in the parent folder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            storage_path = os.path.join(parent_dir, 'Dream_Layer_Resources', 'runs')
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        
        # Create index file if it doesn't exist
        self.index_file = self.storage_path / 'index.json'
        if not self.index_file.exists():
            self._save_index([])
    
    def _save_index(self, index: List[Dict]) -> None:
        """Save the index to file"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _load_index(self) -> List[Dict]:
        """Load the index from file"""
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_run(self, config: Dict[str, Any]) -> str:
        """
        Save a generation run configuration
        
        Args:
            config: The complete configuration dictionary including all generation parameters
            
        Returns:
            The generated run ID
        """
        with self.lock:
            # Generate unique run ID
            run_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create run data with all required fields at the top level
            run_data = {
                'id': run_id,
                'timestamp': timestamp,
                # Core generation parameters
                'model': config.get('model', config.get('model_name', config.get('ckpt_name', 'Unknown'))),
                'vae': config.get('vae', 'Default'),
                'prompt': config.get('prompt', ''),
                'negative_prompt': config.get('negative_prompt', ''),
                'seed': config.get('seed', -1),
                'sampler': config.get('sampler', config.get('sampler_name', 'euler')),
                'scheduler': config.get('scheduler', 'normal'),
                'steps': config.get('steps', 20),
                'cfg_scale': config.get('cfg_scale', 7.0),
                'width': config.get('width', 512),
                'height': config.get('height', 512),
                'batch_size': config.get('batch_size', 1),
                
                # Advanced features
                'loras': config.get('loras', []),
                'controlnets': config.get('controlnet', config.get('controlnets', {})),  # Map controlnet to controlnets for frontend compatibility
                
                # Generation metadata
                'generation_type': config.get('generation_type', 'txt2img'),
                'workflow': config.get('workflow', {}),
                'workflow_version': config.get('workflow_version', '1.0.0'),
                
                # Store the complete original config for reference
                'full_config': config
            }
            
            # Save run data to individual file
            run_file = self.storage_path / f'{run_id}.json'
            with open(run_file, 'w') as f:
                json.dump(run_data, f, indent=2)
            
            # Update index
            index = self._load_index()
            index_entry = {
                'id': run_id,
                'timestamp': timestamp,
                'prompt': run_data['prompt'][:100] + '...' if len(run_data['prompt']) > 100 else run_data['prompt'],
                'model': run_data['model'],
                'generation_type': run_data['generation_type']
            }
            index.insert(0, index_entry)  # Add to beginning for most recent first
            
            # Keep only last 1000 entries in index
            if len(index) > 1000:
                index = index[:1000]
            
            self._save_index(index)
            
            return run_id
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific run by ID
        
        Args:
            run_id: The run ID to retrieve
            
        Returns:
            The run data or None if not found
        """
        run_file = self.storage_path / f'{run_id}.json'
        if run_file.exists():
            try:
                with open(run_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None
    
    def get_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of recent runs
        
        Args:
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            
        Returns:
            List of run summaries
        """
        index = self._load_index()
        return index[offset:offset + limit]
    
    def delete_run(self, run_id: str) -> bool:
        """
        Delete a specific run
        
        Args:
            run_id: The run ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            # Remove file
            run_file = self.storage_path / f'{run_id}.json'
            if run_file.exists():
                run_file.unlink()
                
                # Update index
                index = self._load_index()
                index = [entry for entry in index if entry['id'] != run_id]
                self._save_index(index)
                
                return True
            return False
    
    def clear_all_runs(self) -> None:
        """Clear all runs from the registry"""
        with self.lock:
            # Remove all run files
            for run_file in self.storage_path.glob('*.json'):
                if run_file.name != 'index.json':
                    run_file.unlink()
            
            # Clear index
            self._save_index([])
    
    def list_runs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Alias for get_runs() to maintain compatibility with tests
        
        Args:
            limit: Maximum number of runs to return
            offset: Number of runs to skip
            
        Returns:
            List of run summaries
        """
        return self.get_runs(limit=limit, offset=offset)


# Global registry instance
_registry = None

def get_registry() -> RunRegistry:
    """Get the global run registry instance"""
    global _registry
    if _registry is None:
        _registry = RunRegistry()
    return _registry
