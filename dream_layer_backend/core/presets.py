"""
Presets Module for DreamLayer AI

Manages version-pinned presets for reproducible generation configurations.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Default presets file location
DEFAULT_PRESETS_FILE = Path("presets/presets.json")


class Preset:
    """Represents a generation preset with version pinning."""
    
    def __init__(
        self,
        name: str,
        version: int = 1,
        models: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        preset_hash: Optional[str] = None,
        description: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.name = name
        self.version = version
        self.models = models or {}
        self.params = params or {}
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        
        # Compute hash if not provided
        if preset_hash is None:
            self.preset_hash = self._compute_hash()
        else:
            self.preset_hash = preset_hash
    
    def _compute_hash(self) -> str:
        """Compute stable SHA256 hash of preset configuration."""
        # Create a stable representation for hashing (exclude name and version for stability)
        hash_data = {
            "models": self._sort_dict(self.models),
            "params": self._sort_dict(self.params)
        }
        
        # Convert to sorted JSON string for deterministic hashing
        hash_string = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()
    
    def _sort_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sort dictionary for deterministic hashing."""
        if not isinstance(d, dict):
            return d
        
        sorted_dict = {}
        for key in sorted(d.keys()):
            value = d[key]
            if isinstance(value, dict):
                sorted_dict[key] = self._sort_dict(value)
            elif isinstance(value, list):
                sorted_dict[key] = [self._sort_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                sorted_dict[key] = value
        
        return sorted_dict
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "models": self.models,
            "params": self.params,
            "preset_hash": self.preset_hash,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preset':
        """Create preset from dictionary representation."""
        return cls(
            name=data["name"],
            version=data.get("version", 1),
            models=data.get("models", {}),
            params=data.get("params", {}),
            preset_hash=data.get("preset_hash"),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def update(self, **kwargs) -> None:
        """Update preset fields and recompute hash."""
        for key, value in kwargs.items():
            if key == "params" and isinstance(value, dict):
                # Update params dictionary
                self.params.update(value)
            elif key == "models" and isinstance(value, dict):
                # Update models dictionary
                self.models.update(value)
            elif hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp and recompute hash
        self.updated_at = datetime.now().isoformat()
        self.preset_hash = self._compute_hash()
    
    def is_compatible_with(self, other: 'Preset') -> bool:
        """Check if this preset is compatible with another preset."""
        # Check if the configurations are compatible (same models and params)
        return self.preset_hash == other.preset_hash


class PresetManager:
    """Manages loading, saving, and operations on presets."""
    
    def __init__(self, presets_file: Optional[Path] = None):
        self.presets_file = presets_file or DEFAULT_PRESETS_FILE
        self.presets: Dict[str, Preset] = {}
        self._load_presets()
    
    def _load_presets(self) -> None:
        """Load presets from file."""
        try:
            if self.presets_file.exists():
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load presets
                for preset_data in data.get("presets", []):
                    preset = Preset.from_dict(preset_data)
                    self.presets[preset.name] = preset
                    
                print(f"Loaded {len(self.presets)} presets from {self.presets_file}")
            else:
                print(f"Presets file not found: {self.presets_file}")
                self._create_default_presets()
                
        except Exception as e:
            print(f"Error loading presets: {e}")
            self._create_default_presets()
    
    def _create_default_presets(self) -> None:
        """Create default presets if none exist."""
        default_presets = [
            Preset(
                name="default",
                description="Default generation settings",
                models={
                    "checkpoint": "juggernautXL_v8Rundiffusion.safetensors",
                    "vae": "auto"
                },
                params={
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler": "euler",
                    "scheduler": "normal",
                    "width": 512,
                    "height": 512,
                    "batch_size": 1
                }
            ),
            Preset(
                name="high_quality",
                description="High quality generation with more steps",
                models={
                    "checkpoint": "juggernautXL_v8Rundiffusion.safetensors",
                    "vae": "auto"
                },
                params={
                    "steps": 50,
                    "cfg": 7.0,
                    "sampler": "dpmpp_2m",
                    "scheduler": "karras",
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            ),
            Preset(
                name="fast",
                description="Fast generation with fewer steps",
                models={
                    "checkpoint": "juggernautXL_v8Rundiffusion.safetensors",
                    "vae": "auto"
                },
                params={
                    "steps": 10,
                    "cfg": 7.0,
                    "sampler": "euler",
                    "scheduler": "normal",
                    "width": 512,
                    "height": 512,
                    "batch_size": 4
                }
            )
        ]
        
        for preset in default_presets:
            self.presets[preset.name] = preset
        
        self._save_presets()
        print(f"Created {len(default_presets)} default presets")
    
    def _save_presets(self) -> None:
        """Save presets to file."""
        try:
            # Ensure directory exists
            self.presets_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for saving
            data = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "presets": [preset.to_dict() for preset in self.presets.values()]
            }
            
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"Saved {len(self.presets)} presets to {self.presets_file}")
            
        except Exception as e:
            print(f"Error saving presets: {e}")
    
    def get_preset(self, name: str) -> Optional[Preset]:
        """Get a preset by name."""
        return self.presets.get(name)
    
    def list_presets(self) -> List[str]:
        """List all preset names."""
        return sorted(self.presets.keys())
    
    def add_preset(self, preset: Preset) -> None:
        """Add or update a preset."""
        self.presets[preset.name] = preset
        self._save_presets()
        print(f"Added/updated preset: {preset.name}")
    
    def remove_preset(self, name: str) -> bool:
        """Remove a preset by name."""
        if name in self.presets:
            del self.presets[name]
            self._save_presets()
            print(f"Removed preset: {name}")
            return True
        return False
    
    def create_preset_from_config(
        self, 
        name: str, 
        config: Dict[str, Any], 
        description: str = ""
    ) -> Preset:
        """Create a new preset from a generation configuration."""
        # Extract models and params from config
        models = {}
        params = {}
        
        # Model-related keys
        model_keys = ['model_name', 'vae_name', 'lora_name', 'controlnet_model']
        for key in model_keys:
            if key in config and config[key]:
                models[key] = config[key]
        
        # Parameter-related keys
        param_keys = [
            'steps', 'cfg_scale', 'sampler_name', 'scheduler', 'width', 'height',
            'batch_size', 'seed', 'denoising_strength', 'tile_size', 'tile_overlap'
        ]
        for key in param_keys:
            if key in config and config[key] is not None:
                params[key] = config[key]
        
        # Create preset
        preset = Preset(
            name=name,
            models=models,
            params=params,
            description=description
        )
        
        self.add_preset(preset)
        return preset
    
    def apply_preset_to_config(self, preset_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a preset to a generation configuration."""
        preset = self.get_preset(preset_name)
        if not preset:
            raise ValueError(f"Preset not found: {preset_name}")
        
        # Create a copy of the config
        updated_config = config.copy()
        
        # Apply preset parameters (only if not already set in config)
        for key, value in preset.params.items():
            if key not in updated_config:
                updated_config[key] = value
        
        # Apply preset models (only if not already set in config)
        for key, value in preset.models.items():
            if key == 'checkpoint':
                if 'model_name' not in updated_config:
                    updated_config['model_name'] = value
            elif key == 'vae_name':
                if 'vae_name' not in updated_config:
                    updated_config['vae_name'] = value
            elif key == 'lora_name':
                if 'lora_name' not in updated_config:
                    updated_config['lora_name'] = value
            elif key == 'controlnet_model':
                if 'controlnet_model' not in updated_config:
                    updated_config['controlnet_model'] = value
            else:
                if key not in updated_config:
                    updated_config[key] = value
        
        # Add preset metadata
        updated_config['preset_name'] = preset.name
        updated_config['preset_hash'] = preset.preset_hash
        
        return updated_config
    
    def validate_preset(self, preset_name: str) -> Dict[str, Any]:
        """Validate a preset configuration."""
        preset = self.get_preset(preset_name)
        if not preset:
            return {"valid": False, "error": f"Preset not found: {preset_name}"}
        
        # Check if preset hash is still valid
        current_hash = preset._compute_hash()
        hash_valid = current_hash == preset.preset_hash
        
        # Check if referenced models exist
        missing_models = []
        for model_type, model_name in preset.models.items():
            if not self._model_exists(model_type, model_name):
                missing_models.append(f"{model_type}: {model_name}")
        
        return {
            "valid": hash_valid and len(missing_models) == 0,
            "hash_valid": hash_valid,
            "missing_models": missing_models,
            "preset": preset.to_dict()
        }
    
    def _model_exists(self, model_type: str, model_name: str) -> bool:
        """Check if a model exists in the system."""
        # This is a simplified check - in a real implementation,
        # you would check against the actual model directories
        if model_name == "auto":
            return True
        
        # For now, assume models exist if they have valid extensions
        valid_extensions = {'.safetensors', '.ckpt', '.pth', '.pt', '.bin'}
        return Path(model_name).suffix.lower() in valid_extensions


# Global preset manager instance
_preset_manager: Optional[PresetManager] = None


def get_preset_manager() -> PresetManager:
    """Get the global preset manager instance."""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = PresetManager()
    return _preset_manager


def load_presets(path: Path) -> Dict[str, Preset]:
    """Load presets from a specific path."""
    manager = PresetManager(path)
    return manager.presets


def save_presets(path: Path, presets: Dict[str, Preset]) -> None:
    """Save presets to a specific path."""
    manager = PresetManager(path)
    manager.presets = presets
    manager._save_presets()


def compute_preset_hash(preset: Dict[str, Any]) -> str:
    """Compute hash for a preset dictionary."""
    temp_preset = Preset.from_dict(preset)
    return temp_preset.preset_hash
