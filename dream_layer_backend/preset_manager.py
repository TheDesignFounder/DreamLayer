import json
import os
import hashlib
import uuid
import logging
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Preset:
    id: str
    name: str
    description: Optional[str]
    version: str
    hash: str
    settings: Dict[str, Any]
    controlnet: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    is_default: bool = False

class PresetManager:
    def __init__(self, presets_file: str = "presets.json"):
        self.presets_file = presets_file
        self.presets: Dict[str, Preset] = {}
        self.load_presets()
        self.initialize_default_presets()

    def generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate a hash for preset settings to ensure version pinning"""
        # Sort keys to ensure consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.md5(sorted_data.encode('utf-8')).hexdigest()

    def load_presets(self):
        """Load presets from file"""
        try:
            if os.path.exists(self.presets_file):
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.presets = {
                        preset_id: Preset(**preset_data)
                        for preset_id, preset_data in data.items()
                    }
                logging.info(f"Successfully loaded {len(self.presets)} presets from {self.presets_file}")
        except Exception as e:
            logging.error(f"Error loading presets from {self.presets_file}: {str(e)}")
            self.presets = {}

    def save_presets(self):
        """Save presets to file using atomic write operations"""
        try:
            # Convert presets to serializable format
            data = {
                preset_id: asdict(preset)
                for preset_id, preset in self.presets.items()
            }
            
            # Create a temporary file in the same directory as the target file
            preset_dir = os.path.dirname(os.path.abspath(self.presets_file))
            with tempfile.NamedTemporaryFile(mode='w', 
                                           dir=preset_dir,
                                           prefix='.presets_tmp_',
                                           suffix='.json',
                                           delete=False,
                                           encoding='utf-8') as temp_file:
                # Write data to temporary file
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                
            # Rename temporary file to target file (atomic on POSIX systems)
            # On Windows, this will fail if the target exists, so we need to handle that
            try:
                os.replace(temp_file.name, self.presets_file)
            except OSError:
                # On Windows, explicitly remove the target file first
                os.remove(self.presets_file)
                os.rename(temp_file.name, self.presets_file)
                
            logging.info(f"Successfully saved {len(self.presets)} presets to {self.presets_file}")
        except Exception as e:
            logging.error(f"Error saving presets to {self.presets_file}: {str(e)}")
            # Clean up temporary file if it exists
            if 'temp_file' in locals():
                try:
                    os.unlink(temp_file.name)
                except OSError:
                    pass
            raise

    def initialize_default_presets(self):
        """Initialize default presets if none exist"""
        if not self.presets:
            default_presets = [
                {
                    "name": "SDXL Base",
                    "description": "Standard SDXL generation settings",
                    "version": "1.0.0",
                    "settings": {
                        "prompt": "",
                        "negative_prompt": "",
                        "model_name": "juggernautXL_v8Rundiffusion.safetensors",
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "steps": 20,
                        "cfg_scale": 7.0,
                        "width": 1024,
                        "height": 1024,
                        "batch_size": 1,
                        "batch_count": 1,
                        "seed": -1,
                        "random_seed": True,
                        "lora": None
                    },
                    "controlnet": None
                },
                {
                    "name": "Base + Refiner",
                    "description": "SDXL with refiner for enhanced quality",
                    "version": "1.0.0",
                    "settings": {
                        "prompt": "",
                        "negative_prompt": "",
                        "model_name": "juggernautXL_v8Rundiffusion.safetensors",
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "steps": 20,
                        "cfg_scale": 7.0,
                        "width": 1024,
                        "height": 1024,
                        "batch_size": 1,
                        "batch_count": 1,
                        "seed": -1,
                        "random_seed": True,
                        "lora": None,
                        "refiner_enabled": True,
                        "refiner_model": "sd_xl_refiner_1.0.safetensors",
                        "refiner_switch_at": 0.8
                    },
                    "controlnet": None
                },
                {
                    "name": "Fast Generation",
                    "description": "Optimized for speed with fewer steps",
                    "version": "1.0.0",
                    "settings": {
                        "prompt": "",
                        "negative_prompt": "",
                        "model_name": "juggernautXL_v8Rundiffusion.safetensors",
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "steps": 10,
                        "cfg_scale": 7.0,
                        "width": 512,
                        "height": 512,
                        "batch_size": 1,
                        "batch_count": 1,
                        "seed": -1,
                        "random_seed": True,
                        "lora": None
                    },
                    "controlnet": None
                }
            ]

            now = datetime.now().isoformat()
            for i, preset_data in enumerate(default_presets):
                preset_id = f"default-{i}"
                hash_data = {
                    "settings": preset_data["settings"],
                    "controlnet": preset_data["controlnet"]
                }
                
                preset = Preset(
                    id=preset_id,
                    name=preset_data["name"],
                    description=preset_data["description"],
                    version=preset_data["version"],
                    hash=self.generate_hash(hash_data),
                    settings=preset_data["settings"],
                    controlnet=preset_data["controlnet"],
                    created_at=now,
                    updated_at=now,
                    is_default=True
                )
                self.presets[preset_id] = preset

            self.save_presets()

    def create_preset(self, name: str, description: Optional[str], settings: Dict[str, Any], controlnet: Optional[Dict[str, Any]] = None) -> Preset:
        """Create a new preset with a unique ID using UUID and timestamp"""
        # Generate a unique ID combining timestamp and UUID
        timestamp = int(datetime.now().timestamp())
        unique_uuid = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
        preset_id = f"preset-{timestamp}-{unique_uuid}"
        now = datetime.now().isoformat()
        
        hash_data = {
            "settings": settings,
            "controlnet": controlnet
        }
        
        preset = Preset(
            id=preset_id,
            name=name,
            description=description,
            version="1.0.0",
            hash=self.generate_hash(hash_data),
            settings=settings,
            controlnet=controlnet,
            created_at=now,
            updated_at=now,
            is_default=False
        )
        
        self.presets[preset_id] = preset
        self.save_presets()
        return preset

    def update_preset(self, preset_id: str, name: Optional[str] = None, description: Optional[str] = None, 
                     settings: Optional[Dict[str, Any]] = None, controlnet: Optional[Dict[str, Any]] = None) -> Optional[Preset]:
        """Update an existing preset"""
        if preset_id not in self.presets:
            return None
            
        preset = self.presets[preset_id]
        
        if name is not None:
            preset.name = name
        if description is not None:
            preset.description = description
        if settings is not None:
            preset.settings = settings
        if controlnet is not None:
            preset.controlnet = controlnet
            
        # Regenerate hash if settings or controlnet changed
        if settings is not None or controlnet is not None:
            hash_data = {
                "settings": preset.settings,
                "controlnet": preset.controlnet
            }
            preset.hash = self.generate_hash(hash_data)
            
        preset.updated_at = datetime.now().isoformat()
        self.save_presets()
        return preset

    def delete_preset(self, preset_id: str) -> bool:
        """Delete a preset"""
        if preset_id not in self.presets:
            return False
            
        preset = self.presets[preset_id]
        if preset.is_default:
            return False  # Cannot delete default presets
            
        del self.presets[preset_id]
        self.save_presets()
        return True

    def get_preset(self, preset_id: str) -> Optional[Preset]:
        """Get a preset by ID"""
        return self.presets.get(preset_id)

    def get_all_presets(self) -> List[Preset]:
        """Get all presets"""
        return list(self.presets.values())

    def get_preset_by_hash(self, hash_value: str) -> Optional[Preset]:
        """Get a preset by its hash"""
        for preset in self.presets.values():
            if preset.hash == hash_value:
                return preset
        return None

    def validate_preset_hash(self, preset_id: str, settings: Dict[str, Any], controlnet: Optional[Dict[str, Any]] = None) -> bool:
        """Validate that a preset's hash matches the current settings"""
        preset = self.get_preset(preset_id)
        if not preset:
            return False
            
        hash_data = {
            "settings": settings,
            "controlnet": controlnet
        }
        current_hash = self.generate_hash(hash_data)
        return preset.hash == current_hash 