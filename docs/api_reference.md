# API Reference

Complete API documentation for DreamLayer AI based on the actual codebase implementation.

## Core API Endpoints

### Main Flask Application (`dream_layer.py`)

#### Models Management

**GET `/api/models`** - Get available checkpoint models
```python
# [Source: dream_layer.py lines 150-180]
def get_available_models():
    """
    Fetch available checkpoint models from ComfyUI and append closed-source models
    Returns: List of model objects with id, name, and filename
    """
```

**Response Format:**
```json
{
    "status": "success",
    "models": [
        {
            "id": "model_filename.safetensors",
            "name": "Model Display Name",
            "filename": "model_filename.safetensors"
        }
    ]
}
```

#### LoRA Models

**GET `/api/lora-models`** - Get available LoRA models
```python
# [Source: dream_layer.py lines 271-293]
def get_available_lora_models():
    """
    Fetch available LoRA models from the configured models directory
    Returns: List of LoRA model objects
    """
```

#### Upscaler Models

**GET `/api/upscaler-models`** - Get available upscaler models
```python
# [Source: dream_layer.py lines 323-329]
def get_upscaler_models_endpoint():
    """
    Fetch available upscaler models from the configured models directory
    Returns: List of upscaler model objects
    """
```

#### ControlNet Models

**GET `/api/controlnet/models`** - Get available ControlNet models
```python
# [Source: dream_layer.py lines 466-486]
def get_controlnet_models_endpoint():
    """
    Fetch available ControlNet models from the configured models directory
    Returns: List of ControlNet model objects
    """
```

#### Settings Management

**POST `/api/settings/paths`** - Configure output and models directories
```python
# [Source: dream_layer.py lines 200-226]
def handle_path_settings():
    """
    Endpoint to handle path configuration settings
    Request Body: {"outputDirectory": "path", "modelsDirectory": "path"}
    """
```

**Request Format:**
```json
{
    "outputDirectory": "/path/to/output",
    "modelsDirectory": "/path/to/models"
}
```

#### Prompt Generation

**GET `/api/fetch-prompt`** - Get random positive and negative prompts
```python
# [Source: dream_layer.py lines 311-322]
def fetch_prompt():
    """
    Fetch random positive and negative prompts from the prompt generator
    Returns: {"positive": "prompt", "negative": "prompt"}
    """
```

#### File Operations

**POST `/api/show-in-folder`** - Open file in system file manager
```python
# [Source: dream_layer.py lines 330-363]
def show_in_folder():
    """
    Open the specified file in the system's default file manager
    Request Body: {"filePath": "path/to/file"}
    """
```

**POST `/api/send-to-img2img`** - Send image to img2img workflow
```python
# [Source: dream_layer.py lines 364-381]
def send_to_img2img():
    """
    Send an image to the img2img workflow by copying it to the img2img directory
    Request Body: {"imagePath": "path/to/image"}
    """
```

**POST `/api/send-to-extras`** - Send image to extras workflow
```python
# [Source: dream_layer.py lines 382-405]
def send_to_extras():
    """
    Send an image to the extras workflow by copying it to the extras directory
    Request Body: {"imagePath": "path/to/image"}
    """
```

#### File Upload

**POST `/api/upload-model`** - Upload model files to ComfyUI models directory
```python
# [Source: dream_layer.py lines 456-481]
def upload_model():
    """
    Upload model files to appropriate ComfyUI model directories
    Request: Multipart form data with model file and model_type
    Supports: .safetensors, .ckpt, .pth, .pt, .bin formats
    """
```

**Request Format:**
```
Content-Type: multipart/form-data

file: <model file>
model_type: checkpoints|loras|controlnet|upscale_models|vae|embeddings|hypernetworks
```

**Response Format:**
```json
{
    "status": "success",
    "filename": "timestamped_filename.safetensors",
    "original_filename": "original_name.safetensors",
    "display_name": "Original Name",
    "model_type": "checkpoints",
    "filepath": "/path/to/saved/file",
    "size": 1234567890,
    "message": "Model uploaded successfully to checkpoints"
}
```

**POST `/api/upload-controlnet-image`** - Upload ControlNet image
```python
# [Source: dream_layer.py lines 406-448]
def upload_controlnet_image():
    """
    Upload and save a ControlNet image to the served_images directory
    Request: Multipart form data with image file
    Returns: {"status": "success", "filename": "saved_filename.png"}
    """
```

#### Image Serving

**GET `/api/images/<filename>`** - Serve generated images
```python
# [Source: dream_layer.py lines 449-465]
def serve_image(filename):
    """
    Serve generated images from the output directory
    Path Parameter: filename - Name of the image file to serve
    Returns: Image file or 404 if not found
    """
```

## Utility Functions

### Directory Management

**`get_directories()`** - Get output and models directories
```python
# [Source: dream_layer.py lines 35-75]
def get_directories() -> Tuple[str, Optional[str]]:
    """
    Get the absolute paths to the output and models directories from settings
    Returns: Tuple of (output_dir, models_dir)
    """
```

### ComfyUI Integration

**`import_comfyui_main()`** - Import ComfyUI main module
```python
# [Source: dream_layer.py lines 77-95]
def import_comfyui_main():
    """
    Import ComfyUI main module only when needed
    Returns: ComfyUI start function or None if import fails
    """
```

### Settings Management

**`save_settings(settings)`** - Save path settings to file
```python
# [Source: dream_layer.py lines 182-190]
def save_settings(settings):
    """
    Save path settings to a file
    Parameters: settings - Dictionary of settings to save
    Returns: True if successful, False otherwise
    """
```

## Server Management

### ComfyUI Server

**`start_comfy_server()`** - Start ComfyUI server in background
```python
# [Source: dream_layer.py lines 227-265]
def start_comfy_server():
    """
    Start ComfyUI server in a separate thread
    Handles server startup and error logging
    """
```

### Flask Server

**`start_flask_server()`** - Start Flask API server
```python
# [Source: dream_layer.py lines 266-270]
def start_flask_server():
    """
    Start the Flask API server on the configured port
    """
```

## Configuration

### API Key Mapping

```python
# [Source: dream_layer.py lines 25-35]
API_KEY_TO_MODELS = {
    "BFL_API_KEY": [
        {"id": "flux-pro", "name": "FLUX Pro", "filename": "flux-pro"},
        {"id": "flux-dev", "name": "FLUX Dev", "filename": "flux-dev"},
    ],
    "OPENAI_API_KEY": [
        {"id": "dall-e-3", "name": "DALL-E 3", "filename": "dall-e-3"},
        {"id": "dall-e-2", "name": "DALL-E 2", "filename": "dall-e-2"},
    ],
    "IDEOGRAM_API_KEY": [
        {"id": "ideogram-v3", "name": "Ideogram V3", "filename": "ideogram-v3"},
    ]
}
```

### CORS Configuration

```python
# [Source: dream_layer.py lines 97-108]
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
```

## Related Documentation

- [Architecture Overview](architecture.md) - System design and component relationships
- [Usage Guide](usage.md) - How to use the API endpoints
- [Installation Guide](installation.md) - Setup and configuration instructions 