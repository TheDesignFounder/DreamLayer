# DreamLayer Backend

The DreamLayer backend is a Flask-based API server that provides a bridge between the frontend interface and ComfyUI, along with additional features for model management, progress tracking, and file handling.

## 🚀 Features

### Core Functionality

- **ComfyUI Integration**: Seamless integration with ComfyUI for image generation
- **Model Management**: Dynamic discovery and management of local and API-based models
- **Progress Tracking**: Real-time generation progress with WebSocket-like polling
- **File Management**: Cross-platform file operations and image serving
- **Settings Management**: Persistent configuration storage and management

### API Endpoints

#### Model Management

- `GET /api/models` - Get available checkpoint models
- `GET /api/lora-models` - Get available LoRA models
- `GET /api/upscaler-models` - Get available upscaler models
- `GET /api/controlnet/models` - Get available ControlNet models

#### Progress Tracking

- `GET /queue/progress` - Get current generation progress (500ms polling)
- `POST /queue/reset` - Reset progress tracking (for testing)

#### File Operations

- `POST /api/upload-mask` - Upload mask files for inpainting (PNG, ≤10MB)
- `POST /api/upload-controlnet-image` - Upload ControlNet reference images
- `GET /api/images/<filename>` - Serve generated images
- `POST /api/show-in-folder` - Open file location in system file manager

#### Generation

- `POST /api/generate` - Start image generation with progress tracking
- `POST /api/send-to-img2img` - Send image to img2img workflow
- `POST /api/send-to-extras` - Send image to extras processing

#### Utilities

- `GET /api/fetch-prompt` - Get random positive/negative prompts
- `POST /api/settings/paths` - Update path configurations

## 🛠️ Enhanced Features (July 2025)

### Real-time Progress Tracking

```python
# Progress tracking with ComfyUI queue integration
@app.route('/queue/progress', methods=['GET'])
def get_queue_progress():
    """Get current generation progress with real-time updates"""
    # Integrates with ComfyUI queue system
    # Returns: {"percent": 75, "status": "processing", "message": "Generating..."}
```

### Advanced Mask Upload

```python
# Secure mask file upload with validation
@app.route('/api/upload-mask', methods=['POST'])
def upload_mask():
    """Upload mask file for inpainting with validation"""
    # Validates: PNG format, ≤10MB size
    # Generates unique timestamped filenames
    # Saves to ComfyUI input directory
```

### Enhanced Model Discovery

```python
# Dynamic model discovery with API integration
def get_available_models():
    """Fetch models from ComfyUI + API-based models"""
    # Discovers local ComfyUI models
    # Adds API models based on available keys
    # Returns formatted model list with friendly names
```

### Cross-platform File Management

```python
# Cross-platform file operations
@app.route('/api/show-in-folder', methods=['POST'])
def show_in_folder():
    """Open file in system file manager (Windows/macOS/Linux)"""
    # Windows: explorer /select
    # macOS: open -R
    # Linux: xdg-open
```

## 🔧 Configuration

### Environment Variables

```bash
# ComfyUI CPU mode (optional)
DREAMLAYER_COMFYUI_CPU_MODE=true

# API Keys for external models
OPENAI_API_KEY=sk-...
BFL_API_KEY=flux-...
IDEOGRAM_API_KEY=id-...
```

### Directory Structure

```
dream_layer_backend/
├── dream_layer.py              # Main Flask application
├── shared_utils.py             # Shared utility functions
├── settings.json               # Persistent settings storage
├── requirements.txt            # Python dependencies
├── restart_server.sh           # Server restart script
└── dream_layer_backend_utils/  # Utility modules
    ├── random_prompt_generator.py
    ├── fetch_advanced_models.py
    └── workflow_execution.py
```

## 🚦 API Response Formats

### Success Response

```json
{
  "status": "success",
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Detailed error description",
  "code": 400
}
```

### Progress Response

```json
{
  "percent": 75,
  "status": "processing",
  "message": "Generating image...",
  "job_id": "uuid-string"
}
```

## 🔒 Security Features

### File Upload Validation

- **Type Validation**: Only PNG files for masks
- **Size Limits**: 10MB maximum file size
- **Path Sanitization**: Prevents directory traversal
- **Unique Naming**: Timestamped filenames prevent conflicts

### CORS Configuration

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    },
    r"/queue/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})
```

## 📊 Performance Optimizations

### Efficient Model Loading

- **Lazy Loading**: Models loaded only when needed
- **Caching**: Model lists cached to reduce API calls
- **Error Handling**: Graceful fallbacks for unavailable models

### Progress Tracking

- **Non-blocking**: Progress updates don't block generation
- **Efficient Polling**: 500ms intervals balance responsiveness and performance
- **Queue Integration**: Real-time status from ComfyUI queue system

## 🧪 Testing

### Manual Testing

```bash
# Test progress endpoint
curl http://localhost:5002/queue/progress

# Test model discovery
curl http://localhost:5002/api/models

# Test mask upload
curl -X POST -F "file=@mask.png" http://localhost:5002/api/upload-mask
```

### Integration Testing

- **ComfyUI Integration**: Validates ComfyUI server connectivity
- **File Operations**: Tests cross-platform file management
- **API Endpoints**: Comprehensive endpoint testing

## 🔄 Development Workflow

### Starting the Server

```bash
cd dream_layer_backend
python dream_layer.py
```

### Development Mode

- **Auto-reload**: Flask debug mode for development
- **Error Logging**: Comprehensive error tracking
- **CORS Enabled**: Frontend development support

### Production Deployment

- **Process Management**: Use gunicorn or similar WSGI server
- **Reverse Proxy**: Nginx recommended for production
- **SSL/TLS**: HTTPS configuration for security

## 📝 API Documentation

### Model Management Endpoints

#### GET /api/models

Returns available checkpoint models from ComfyUI and API providers.

**Response:**

```json
{
  "status": "success",
  "models": [
    {
      "id": "model-filename.safetensors",
      "name": "Model Display Name",
      "filename": "model-filename.safetensors"
    }
  ]
}
```

#### GET /queue/progress

Returns current generation progress with real-time updates.

**Response:**

```json
{
  "percent": 75,
  "status": "processing",
  "message": "Generating image...",
  "job_id": "uuid-string"
}
```

#### POST /api/upload-mask

Upload mask file for inpainting operations.

**Request:** Multipart form data with 'file' field
**Validation:** PNG format, ≤10MB size
**Response:**

```json
{
  "status": "success",
  "message": "Mask uploaded successfully",
  "filename": "mask_20250710_143022_original.png",
  "size": 1048576
}
```

## 🐛 Troubleshooting

### Common Issues

#### ComfyUI Connection Failed

```bash
# Check ComfyUI server status
curl http://localhost:8188

# Verify ComfyUI directory path
ls -la ComfyUI/
```

#### Model Discovery Issues

```bash
# Check model directory permissions
ls -la /path/to/models/

# Verify API keys
echo $OPENAI_API_KEY
```

#### File Upload Errors

```bash
# Check file permissions
ls -la ComfyUI/input/

# Verify file size and format
file mask.png
du -h mask.png
```

## 📈 Monitoring

### Health Checks

- **ComfyUI Status**: Regular connectivity checks
- **Model Availability**: Periodic model discovery
- **File System**: Directory accessibility validation

### Logging

- **Request Logging**: All API requests logged
- **Error Tracking**: Comprehensive error reporting
- **Performance Metrics**: Response time monitoring

## 🔮 Future Enhancements

### Planned Features

- **WebSocket Support**: Real-time bidirectional communication
- **Batch Processing**: Multiple image generation queuing
- **Advanced Caching**: Redis integration for model caching
- **API Rate Limiting**: Request throttling for stability
- **Metrics Dashboard**: Real-time performance monitoring

### Integration Roadmap

- **Database Support**: PostgreSQL/SQLite for persistent storage
- **Authentication**: User management and API key authentication
- **Cloud Storage**: S3/GCS integration for image storage
- **Microservices**: Service decomposition for scalability
