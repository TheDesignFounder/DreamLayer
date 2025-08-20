# Usage Guide

Learn how to use DreamLayer AI effectively with API examples, workflow management, and advanced features based on the actual codebase.

## 🎨 Basic Usage

### Web Interface

1. **Start DreamLayer** (see [Installation Guide](installation.md))
2. **Open your browser** to http://localhost:8080
3. **Enter a prompt** in the text area
4. **Click Generate** to create your image

### Example Prompts

```bash
# Basic prompts
"A beautiful sunset over mountains, digital art"
"A cute cat sitting on a windowsill, watercolor style"
"A futuristic cityscape at night, neon lights, cyberpunk"

# Advanced prompts with modifiers
"A portrait of a woman, masterpiece, best quality, highly detailed, 8k uhd, dslr, high quality, film grain, Fujifilm XT3"
"A landscape painting, oil on canvas, impressionist style, Claude Monet, soft lighting, pastel colors"
```

## 🔌 API Usage

### Core Endpoints

#### Get Available Models
```bash
curl -X GET http://localhost:5000/api/models
```

**Response:**
```json
{
  "status": "success",
  "models": [
    {
      "id": "sd15.safetensors",
      "name": "Sd15",
      "filename": "sd15.safetensors"
    },
    {
      "id": "flux-pro",
      "name": "FLUX Pro",
      "filename": "flux-pro"
    }
  ]
}
```

#### Get LoRA Models
```bash
curl -X GET http://localhost:5000/api/lora-models
```

#### Get Upscaler Models
```bash
curl -X GET http://localhost:5000/api/upscaler-models
```

#### Get ControlNet Models
```bash
curl -X GET http://localhost:5000/api/controlnet/models
```

#### Fetch Random Prompts
```bash
curl -X GET http://localhost:5000/api/fetch-prompt
```

**Response:**
```json
{
  "positive": "A majestic dragon soaring through clouds",
  "negative": "blurry, low quality, distorted"
}
```

### File Operations

#### Upload ControlNet Image
```bash
curl -X POST http://localhost:5000/api/upload-controlnet-image \
  -F "image=@path/to/your/image.png"
```

**Response:**
```json
{
  "status": "success",
  "filename": "DreamLayer_CN_00001_.png"
}
```

#### Send Image to img2img
```bash
curl -X POST http://localhost:5000/api/send-to-img2img \
  -H "Content-Type: application/json" \
  -d '{"imagePath": "/path/to/image.png"}'
```

#### Send Image to Extras
```bash
curl -X POST http://localhost:5000/api/send-to-extras \
  -H "Content-Type: application/json" \
  -d '{"imagePath": "/path/to/image.png"}'
```

#### Show Image in Folder
```bash
curl -X POST http://localhost:5000/api/show-in-folder \
  -H "Content-Type: application/json" \
  -d '{"filePath": "/path/to/image.png"}'
```

### Settings Management

#### Configure Paths
```bash
curl -X POST http://localhost:5000/api/settings/paths \
  -H "Content-Type: application/json" \
  -d '{
    "outputDirectory": "/path/to/output",
    "modelsDirectory": "/path/to/models"
  }'
```

## 🎯 Advanced Features

### Text-to-Image Generation

DreamLayer supports multiple generation modes:

1. **Local Models** - Using ComfyUI with Stable Diffusion
2. **Cloud APIs** - DALL-E, Ideogram, FLUX (requires API keys)

#### Local Generation Workflow

```python
import requests
import json

# Load workflow
with open('workflows/txt2img/core_generation_workflow.json', 'r') as f:
    workflow = json.load(f)

# Modify workflow parameters
workflow['prompt']['text'] = "A beautiful sunset over mountains"
workflow['negative_prompt']['text'] = "blurry, low quality"

# Send to ComfyUI
response = requests.post('http://localhost:8188/prompt', json={
    'prompt': workflow
})

print(f"Generation started: {response.json()}")
```

#### Cloud API Generation

```python
import requests

# DALL-E 3 generation
def generate_dalle3(prompt, api_key):
    response = requests.post('https://api.openai.com/v1/images/generations', 
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': 'dall-e-3',
            'prompt': prompt,
            'n': 1,
            'size': '1024x1024'
        }
    )
    return response.json()

# Ideogram generation
def generate_ideogram(prompt, api_key):
    response = requests.post('https://api.ideogram.ai/api/generation',
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'prompt': prompt,
            'aspect_ratio': '1:1'
        }
    )
    return response.json()
```

### Image-to-Image Generation

```python
# Load img2img workflow
with open('workflows/img2img/core_generation_workflow.json', 'r') as f:
    workflow = json.load(f)

# Set input image
workflow['input_image']['image'] = "path/to/input/image.png"
workflow['prompt']['text'] = "Transform this into a painting"

# Send to ComfyUI
response = requests.post('http://localhost:8188/prompt', json={
    'prompt': workflow
})
```

### ControlNet Integration

```python
# Upload ControlNet image
with open('control_image.png', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:5000/api/upload-controlnet-image', 
                           files=files)

controlnet_image = response.json()['filename']

# Use in workflow
workflow['controlnet']['image'] = controlnet_image
workflow['controlnet']['strength'] = 0.8
```

## 🎨 Workflow Management

### Pre-configured Workflows

DreamLayer includes several pre-configured workflows:

- **`workflows/txt2img/core_generation_workflow.json`** - Basic text-to-image
- **`workflows/txt2img/bfl_core_generation_workflow.json`** - FLUX API integration
- **`workflows/txt2img/dalle_core_generation_workflow.json`** - DALL-E integration
- **`workflows/img2img/core_generation_workflow.json`** - Basic image-to-image
- **`workflows/img2img/bfl_core_generation_workflow.json`** - FLUX img2img

### Custom Workflows

Create custom workflows by modifying the JSON files:

```json
{
  "prompt": {
    "text": "Your prompt here",
    "weight": 1.0
  },
  "negative_prompt": {
    "text": "Your negative prompt here",
    "weight": 1.0
  },
  "model": {
    "name": "sd15.safetensors",
    "strength": 1.0
  },
  "sampler": {
    "name": "euler",
    "steps": 20,
    "cfg": 7.0
  },
  "output": {
    "width": 512,
    "height": 512,
    "batch_size": 1
  }
}
```

## 🔧 Configuration

### Environment Variables

Set up API keys for cloud models:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
IDEOGRAM_API_KEY=your_ideogram_api_key_here
BFL_API_KEY=your_bfl_api_key_here
```

### Directory Structure

```
DreamLayer/
├── dream_layer_backend/
│   ├── dream_layer.py          # Main Flask API
│   ├── txt2img_server.py       # Text-to-image server
│   ├── img2img_server.py       # Image-to-image server
│   └── controlnet.py           # ControlNet integration
├── dream_layer_frontend/       # React frontend
├── ComfyUI/                    # ComfyUI engine
├── workflows/                  # Pre-configured workflows
│   ├── txt2img/
│   └── img2img/
└── Dream_Layer_Resources/      # Output and resources
    └── output/                 # Generated images
```

## 🚀 Performance Optimization

### GPU Optimization

1. **Enable CUDA** - Ensure PyTorch is installed with CUDA support
2. **Optimize VRAM** - Use appropriate model sizes for your GPU
3. **Batch Processing** - Generate multiple images at once

### Memory Management

```python
# Clear GPU memory after generation
import torch
torch.cuda.empty_cache()

# Use CPU offloading for large models
workflow['model']['device'] = 'cpu'
```

### Speed Optimization

1. **Use smaller models** for faster generation
2. **Reduce steps** for quicker results
3. **Enable xformers** for attention optimization
4. **Use VAE in CPU** to save VRAM

## 🔍 Monitoring and Debugging

### Check Server Status

```bash
# Check Flask API
curl http://localhost:5000/api/models

# Check ComfyUI
curl http://localhost:8188/system_stats

# Check frontend
curl http://localhost:8080
```

### View Logs

```bash
# Flask API logs
tail -f logs/dream_layer.log

# ComfyUI logs
tail -f ComfyUI/logs/comfyui.log
```

### Debug Workflows

```python
# Validate workflow before sending
def validate_workflow(workflow):
    required_fields = ['prompt', 'model', 'sampler']
    for field in required_fields:
        if field not in workflow:
            raise ValueError(f"Missing required field: {field}")
    return True

# Test workflow
try:
    validate_workflow(workflow)
    response = requests.post('http://localhost:8188/prompt', json={'prompt': workflow})
    print(f"Workflow sent successfully: {response.json()}")
except Exception as e:
    print(f"Workflow validation failed: {e}")
```

## 🎯 Best Practices

### Prompt Engineering

1. **Be specific** - Include style, composition, lighting details
2. **Use negative prompts** - Exclude unwanted elements
3. **Experiment with weights** - Adjust prompt importance
4. **Use LoRA models** - For specific styles or subjects

### Model Selection

1. **SD 1.5** - Good balance of speed and quality
2. **SD XL** - Higher quality, more VRAM required
3. **Custom models** - Specialized for specific styles
4. **Cloud APIs** - When local generation isn't sufficient

### Workflow Optimization

1. **Reuse workflows** - Save successful configurations
2. **Batch processing** - Generate multiple variations
3. **Progressive refinement** - Start simple, add complexity
4. **Version control** - Track workflow changes

---

*For more advanced usage, see the [API Reference](api_reference.md) and [Architecture Guide](architecture.md).* 