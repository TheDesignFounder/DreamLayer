"""
Constants for DreamLayer backend to avoid hardcoded values
"""

# Image generation limits
DIMENSION_LIMITS = {
    'MIN': 64,
    'MAX': 2048,
    'DEFAULT': 512,
}

BATCH_SIZE_LIMITS = {
    'MIN': 1,
    'MAX': 8,
    'DEFAULT': 1,
}

# Sampling parameters
SAMPLING_LIMITS = {
    'STEPS': {
        'MIN': 1,
        'MAX': 150,
        'DEFAULT': 20,
    },
    'CFG_SCALE': {
        'MIN': 1.0,
        'MAX': 20.0,
        'DEFAULT': 7.0,
    }
}

# Seed generation
SEED_LIMITS = {
    'MAX_VALUE': 2**32 - 1,
    'MIN_VALUE': 0,
}

# Base64 detection
BASE64_DETECTION = {
    'MIN_LENGTH': 100,
    'PREFIXES': ['data:image', '/9j/'],
    'PATTERN': r'^[A-Za-z0-9+/]+=*$',
}

# File paths
DEFAULT_PATHS = {
    'CONTROLNET_INPUT': 'controlnet_input.png',
    'COMFYUI_INPUT_DIR': 'ComfyUI/input',
}

# ControlNet mappings
CONTROLNET_TYPE_MAPPING = {
    'openpose': 'openpose',
    'canny': 'canny/lineart/anime_lineart/mlsd',
    'depth': 'depth',
    'normal': 'normal',
    'segment': 'segment',
    'tile': 'tile',
    'repaint': 'repaint'
}

# Server configuration
SERVER_CONFIG = {
    'PORTS': {
        'IMG2IMG': 5004,
        'EXTRAS': 5003,
        'MODEL_SERVICE': 5002,
    },
    'HOSTS': {
        'COMFY_API': 'http://127.0.0.1:8188',
        'LOCALHOST_EXTRAS': 'http://localhost:5003',
    }
}

# Built-in categories that should not be deleted
PROTECTED_CATEGORIES = [
    'general', 'portrait', 'landscape', 'art', 
    'photography', 'fantasy', 'scifi', 'anime', 'custom'
]