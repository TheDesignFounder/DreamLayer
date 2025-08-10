# Utils Module

Documentation for utility modules in DreamLayer AI.

## Overview

The utils module provides essential utility functions for API key management, model fetching, prompt generation, and file operations.

## Core Components

### API Key Management (`api_key_injector.py`)

Handles secure API key management for external services.

#### Key Functions

**`read_api_keys_from_env()`**
```python
def read_api_keys_from_env():
    """
    Read API keys from environment variables
    
    Returns:
        dict: Dictionary of API key names and values
    """
    api_keys = {}
    
    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        api_keys['OPENAI_API_KEY'] = openai_key
    
    # Check for Ideogram API key
    ideogram_key = os.getenv('IDEOGRAM_API_KEY')
    if ideogram_key:
        api_keys['IDEOGRAM_API_KEY'] = ideogram_key
    
    # Check for BFL API key
    bfl_key = os.getenv('BFL_API_KEY')
    if bfl_key:
        api_keys['BFL_API_KEY'] = bfl_key
    
    return api_keys
```

**`validate_api_key(api_key, service)`**
```python
def validate_api_key(api_key: str, service: str):
    """
    Validate API key format for specific service
    
    Parameters:
        api_key (str): API key to validate
        service (str): Service name (openai, ideogram, bfl)
    
    Returns:
        bool: True if valid, False otherwise
    """
```

### Model Fetching (`fetch_advanced_models.py`)

Manages model discovery and loading from various sources.

#### Key Functions

**`get_lora_models(models_dir)`**
```python
def get_lora_models(models_dir: str):
    """
    Fetch available LoRA models from the models directory
    
    Parameters:
        models_dir (str): Path to models directory
    
    Returns:
        list: List of LoRA model objects
    """
```

**`get_settings()`**
```python
def get_settings():
    """
    Load application settings from settings.json
    
    Returns:
        dict: Application settings
    """
```

**`is_valid_directory(path)`**
```python
def is_valid_directory(path: str):
    """
    Check if a directory path is valid and accessible
    
    Parameters:
        path (str): Directory path to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
```

**`get_upscaler_models(models_dir)`**
```python
def get_upscaler_models(models_dir: str):
    """
    Fetch available upscaler models from the models directory
    
    Parameters:
        models_dir (str): Path to models directory
    
    Returns:
        list: List of upscaler model objects
    """
```

**`get_controlnet_models(models_dir)`**
```python
def get_controlnet_models(models_dir: str):
    """
    Fetch available ControlNet models from the models directory
    
    Parameters:
        models_dir (str): Path to models directory
    
    Returns:
        list: List of ControlNet model objects
    """
```

### Prompt Generation (`random_prompt_generator.py`)

Generates random prompts for inspiration and testing.

#### Key Functions

**`fetch_positive_prompt()`**
```python
def fetch_positive_prompt():
    """
    Fetch a random positive prompt from the prompt database
    
    Returns:
        str: Random positive prompt
    """
```

**`fetch_negative_prompt()`**
```python
def fetch_negative_prompt():
    """
    Fetch a random negative prompt from the prompt database
    
    Returns:
        str: Random negative prompt
    """
```

**`load_prompts_from_file(file_path)`**
```python
def load_prompts_from_file(file_path: str):
    """
    Load prompts from a text file
    
    Parameters:
        file_path (str): Path to prompt file
    
    Returns:
        list: List of prompts from file
    """
```

### File Operations (`file_operations.py`)

Handles file system operations and image processing.

#### Key Functions

**`save_image(image_data, filename, output_dir)`**
```python
def save_image(image_data: bytes, filename: str, output_dir: str):
    """
    Save image data to file system
    
    Parameters:
        image_data (bytes): Image data to save
        filename (str): Output filename
        output_dir (str): Output directory path
    
    Returns:
        str: Path to saved image file
    """
```

**`copy_file_to_directory(source_path, target_dir)`**
```python
def copy_file_to_directory(source_path: str, target_dir: str):
    """
    Copy a file to a target directory
    
    Parameters:
        source_path (str): Source file path
        target_dir (str): Target directory path
    
    Returns:
        str: Path to copied file
    """
```

**`open_file_in_explorer(file_path)`**
```python
def open_file_in_explorer(file_path: str):
    """
    Open file in system file explorer
    
    Parameters:
        file_path (str): Path to file to open
    
    Returns:
        bool: True if successful, False otherwise
    """
```

## Configuration Management

### Settings Structure

```python
# Default settings structure
DEFAULT_SETTINGS = {
    "outputDirectory": "Dream_Layer_Resources/output",
    "modelsDirectory": None,
    "serverPort": 5000,
    "comfyuiPort": 8188,
    "frontendPort": 8080,
    "enableLogging": True,
    "logLevel": "INFO"
}
```

### Settings Loading

```python
def load_settings():
    """
    Load settings from settings.json file
    
    Returns:
        dict: Application settings
    """
    settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        # Return default settings if file doesn't exist
        return DEFAULT_SETTINGS.copy()
    except json.JSONDecodeError:
        print("Error: Invalid settings.json file")
        return DEFAULT_SETTINGS.copy()
```

### Settings Saving

```python
def save_settings(settings: dict):
    """
    Save settings to settings.json file
    
    Parameters:
        settings (dict): Settings to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
    
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
```

## Model Management

### Model Discovery

```python
def discover_models(models_dir: str, model_type: str):
    """
    Discover models of specific type in directory
    
    Parameters:
        models_dir (str): Models directory path
        model_type (str): Type of models to discover (checkpoint, lora, etc.)
    
    Returns:
        list: List of discovered model files
    """
    if not models_dir or not os.path.exists(models_dir):
        return []
    
    model_extensions = {
        'checkpoint': ['.safetensors', '.ckpt'],
        'lora': ['.safetensors', '.pt'],
        'controlnet': ['.safetensors', '.pth'],
        'upscaler': ['.pth', '.bin']
    }
    
    extensions = model_extensions.get(model_type, [])
    models = []
    
    for file in os.listdir(models_dir):
        if any(file.endswith(ext) for ext in extensions):
            models.append(file)
    
    return models
```

### Model Validation

```python
def validate_model_file(file_path: str):
    """
    Validate model file integrity
    
    Parameters:
        file_path (str): Path to model file
    
    Returns:
        dict: Validation result with status and details
    """
    if not os.path.exists(file_path):
        return {"valid": False, "error": "File not found"}
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return {"valid": False, "error": "File is empty"}
    
    # Check file extension
    valid_extensions = ['.safetensors', '.ckpt', '.pt', '.pth', '.bin']
    if not any(file_path.endswith(ext) for ext in valid_extensions):
        return {"valid": False, "error": "Invalid file extension"}
    
    return {"valid": True, "file_size": file_size}
```

## Error Handling

### Utility Error Classes

```python
class ModelError(Exception):
    """Raised when there's an error with model operations"""
    pass

class APIKeyError(Exception):
    """Raised when there's an error with API key management"""
    pass

class FileOperationError(Exception):
    """Raised when there's an error with file operations"""
    pass
```

### Error Handling Functions

```python
def handle_model_error(error: Exception, model_name: str):
    """
    Handle model-related errors
    
    Parameters:
        error (Exception): The error that occurred
        model_name (str): Name of the model that caused the error
    
    Returns:
        dict: Error response with details
    """
    return {
        "status": "error",
        "type": "model_error",
        "model": model_name,
        "message": str(error),
        "timestamp": time.time()
    }

def handle_api_error(error: Exception, service: str):
    """
    Handle API-related errors
    
    Parameters:
        error (Exception): The error that occurred
        service (str): Name of the service that caused the error
    
    Returns:
        dict: Error response with details
    """
    return {
        "status": "error",
        "type": "api_error",
        "service": service,
        "message": str(error),
        "timestamp": time.time()
    }
```

## Logging and Monitoring

### Logging Configuration

```python
def setup_logging(log_level: str = "INFO"):
    """
    Setup logging configuration
    
    Parameters:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/dream_layer.log'),
            logging.StreamHandler()
        ]
    )
```

### Performance Monitoring

```python
def monitor_function_performance(func):
    """
    Decorator to monitor function performance
    
    Parameters:
        func: Function to monitor
    
    Returns:
        Wrapped function with performance monitoring
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper
```

## Best Practices

### API Key Security

1. **Environment Variables** - Store API keys in environment variables, not in code
2. **Validation** - Always validate API keys before use
3. **Rotation** - Regularly rotate API keys for security
4. **Logging** - Never log API keys in plain text

### File Operations

1. **Path Validation** - Always validate file paths before operations
2. **Error Handling** - Implement proper error handling for file operations
3. **Permissions** - Check file permissions before read/write operations
4. **Cleanup** - Clean up temporary files after use

### Model Management

1. **Validation** - Validate model files before loading
2. **Caching** - Cache model metadata for faster discovery
3. **Fallbacks** - Provide fallback models when primary models fail
4. **Monitoring** - Monitor model loading times and errors

---

*For more details, see the [API Reference](../api_reference.md) and [Architecture Guide](../architecture.md).* 