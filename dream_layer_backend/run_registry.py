import json
import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import Flask, jsonify, request
from flask_cors import CORS

@dataclass
class RunConfig:
    """Represents a frozen configuration for a completed run"""
    run_id: str
    timestamp: str
    model: str
    vae: Optional[str]
    loras: List[Dict[str, Any]]
    controlnets: List[Dict[str, Any]]
    prompt: str
    negative_prompt: str
    seed: int
    sampler: str
    steps: int
    cfg_scale: float
    width: int
    height: int
    batch_size: int
    batch_count: int
    workflow: Dict[str, Any]
    version: str
    generated_images: List[str]
    generation_type: str  # "txt2img" or "img2img"

class RunRegistry:
    """Manages completed runs and their configurations"""
    
    def __init__(self, storage_file: str = "run_registry.json"):
        self.storage_file = storage_file
        self.runs: Dict[str, RunConfig] = {}
        self.load_runs()
    
    def load_runs(self):
        """Load runs from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for run_id, run_data in data.items():
                        self.runs[run_id] = RunConfig(**run_data)
        except Exception as e:
            print(f"Error loading run registry: {e}")
    
    def save_runs(self):
        """Save runs to storage file"""
        try:
            data = {run_id: asdict(run_config) for run_id, run_config in self.runs.items()}
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving run registry: {e}")
    
    def add_run(self, config: RunConfig):
        """Add a completed run to the registry"""
        self.runs[config.run_id] = config
        self.save_runs()
    
    def get_run(self, run_id: str) -> Optional[RunConfig]:
        """Get a specific run by ID"""
        return self.runs.get(run_id)
    
    def get_all_runs(self) -> List[RunConfig]:
        """Get all runs sorted by timestamp (newest first)"""
        return sorted(self.runs.values(), key=lambda x: x.timestamp, reverse=True)
    
    def delete_run(self, run_id: str) -> bool:
        """Delete a run from the registry"""
        if run_id in self.runs:
            del self.runs[run_id]
            self.save_runs()
            return True
        return False

# Global registry instance
registry = RunRegistry()

def create_run_config_from_generation_data(
    generation_data: Dict[str, Any],
    generated_images: List[str],
    generation_type: str
) -> RunConfig:
    """Create a RunConfig from generation data"""
    
    # Extract configuration from generation data
    config = RunConfig(
        run_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        model=generation_data.get('model_name', 'unknown'),
        vae=generation_data.get('vae_name'),
        loras=generation_data.get('lora', []),
        controlnets=generation_data.get('controlnet', {}).get('units', []),
        prompt=generation_data.get('prompt', ''),
        negative_prompt=generation_data.get('negative_prompt', ''),
        seed=generation_data.get('seed', 0),
        sampler=generation_data.get('sampler_name', 'euler'),
        steps=generation_data.get('steps', 20),
        cfg_scale=generation_data.get('cfg_scale', 7.0),
        width=generation_data.get('width', 512),
        height=generation_data.get('height', 512),
        batch_size=generation_data.get('batch_size', 1),
        batch_count=generation_data.get('batch_count', 1),
        workflow=generation_data.get('workflow', {}),
        version="1.0.0",  # TODO: Get from app version
        generated_images=generated_images,
        generation_type=generation_type
    )
    
    return config

# Flask app for run registry API
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/runs', methods=['GET'])
def get_runs():
    """Get all completed runs"""
    try:
        runs = registry.get_all_runs()
        return jsonify({
            "status": "success",
            "runs": [asdict(run) for run in runs]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/runs/<run_id>', methods=['GET'])
def get_run(run_id: str):
    """Get a specific run by ID"""
    try:
        run = registry.get_run(run_id)
        if run:
            return jsonify({
                "status": "success",
                "run": asdict(run)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Run not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/runs', methods=['POST'])
def add_run():
    """Add a new completed run"""
    try:
        data = request.json
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Create run config from the provided data
        run_config = RunConfig(
            run_id=data.get('run_id', str(uuid.uuid4())),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            model=data.get('model', 'unknown'),
            vae=data.get('vae'),
            loras=data.get('loras', []),
            controlnets=data.get('controlnets', []),
            prompt=data.get('prompt', ''),
            negative_prompt=data.get('negative_prompt', ''),
            seed=data.get('seed', 0),
            sampler=data.get('sampler', 'euler'),
            steps=data.get('steps', 20),
            cfg_scale=data.get('cfg_scale', 7.0),
            width=data.get('width', 512),
            height=data.get('height', 512),
            batch_size=data.get('batch_size', 1),
            batch_count=data.get('batch_count', 1),
            workflow=data.get('workflow', {}),
            version=data.get('version', '1.0.0'),
            generated_images=data.get('generated_images', []),
            generation_type=data.get('generation_type', 'txt2img')
        )
        
        registry.add_run(run_config)
        
        return jsonify({
            "status": "success",
            "run_id": run_config.run_id,
            "message": "Run added successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/runs/<run_id>', methods=['DELETE'])
def delete_run(run_id: str):
    """Delete a run"""
    try:
        success = registry.delete_run(run_id)
        if success:
            return jsonify({
                "status": "success",
                "message": "Run deleted successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Run not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)