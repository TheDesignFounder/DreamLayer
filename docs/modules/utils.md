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

    # Check for Stability AI API key
    stability_key = os.getenv('STABILITY_API_KEY')
    if stability_key:
        api_keys['STABILITY_API_KEY'] = stability_key

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

\*\*`
