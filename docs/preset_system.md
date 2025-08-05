# Preset System Documentation

## Overview

The DreamLayer preset system allows users to create, manage, and apply named, version-pinned presets for image generation settings. Presets include generation parameters, ControlNet configurations, and are stored with hash-based version pinning for consistency.

## Features

### Core Functionality
- **Create Presets**: Save current generation settings as named presets
- **Select Presets**: Apply preset settings to current generation parameters
- **Edit Presets**: Update preset names, descriptions, and settings
- **Delete Presets**: Remove custom presets (default presets cannot be deleted)
- **Version Pinning**: Each preset has a hash that changes when settings are modified
- **Default Presets**: Pre-configured presets including "SDXL Base", "Base + Refiner", and "Fast Generation"

### Technical Features
- **Hash-based Versioning**: Presets include MD5 hashes of their settings for validation
- **Persistent Storage**: Presets are saved to JSON files and persist between sessions
- **API Integration**: Full REST API for preset management
- **Frontend Integration**: React components with Zustand state management
- **Metadata Integration**: Preset information is included in generation metadata

## Architecture

### Backend Components

#### `preset_manager.py`
- **PresetManager**: Core class for preset CRUD operations
- **Preset**: Dataclass representing a preset with all metadata
- **Hash Generation**: MD5-based hashing for version pinning
- **File Persistence**: JSON-based storage with automatic loading/saving

#### API Endpoints (`dream_layer.py`)
- `GET /api/presets` - List all presets
- `POST /api/presets` - Create new preset
- `GET /api/presets/<id>` - Get specific preset
- `PUT /api/presets/<id>` - Update preset
- `DELETE /api/presets/<id>` - Delete preset
- `POST /api/presets/validate-hash` - Validate preset hash

### Frontend Components

#### `usePresetStore.ts`
- **Zustand Store**: Manages preset state with persistence
- **CRUD Operations**: Create, read, update, delete presets
- **Hash Generation**: Client-side hash generation for validation
- **Default Presets**: Automatic initialization of default presets

#### `PresetManager.tsx`
- **React Component**: UI for preset management
- **Create Dialog**: Modal for creating new presets
- **Edit Dialog**: Modal for editing existing presets
- **Preset List**: Display all presets with actions
- **Selection**: Apply presets to current settings

#### `presetService.ts`
- **API Client**: Service for backend communication
- **Error Handling**: Consistent error handling for API calls
- **Type Safety**: TypeScript interfaces for all operations

## Usage

### Creating a Preset
1. Navigate to the "Presets" tab in the Txt2Img interface
2. Configure your desired generation settings
3. Click "Create Preset"
4. Enter a name and optional description
5. Click "Create Preset" to save

### Applying a Preset
1. Go to the "Presets" tab
2. Find the desired preset in the list
3. Click "Select" to apply the preset
4. The generation settings will be updated automatically

### Editing a Preset
1. In the "Presets" tab, click the edit icon on a preset
2. Modify the name, description, or current settings
3. Click "Update Preset" to save changes

### Deleting a Preset
1. In the "Presets" tab, click the delete icon on a custom preset
2. Confirm deletion in the dialog
3. Note: Default presets cannot be deleted

## Default Presets

### SDXL Base
- **Description**: Standard SDXL generation settings
- **Settings**: 1024x1024, 20 steps, Euler sampler, 7.0 CFG

### Base + Refiner
- **Description**: SDXL with refiner for enhanced quality
- **Settings**: Same as SDXL Base plus refiner enabled at 0.8

### Fast Generation
- **Description**: Optimized for speed with fewer steps
- **Settings**: 512x512, 10 steps, Euler sampler, 7.0 CFG

## Technical Details

### Hash Generation
Presets use MD5 hashing of JSON-serialized settings to ensure version pinning:

```python
def generate_hash(self, data: Dict[str, Any]) -> str:
    sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.md5(sorted_data.encode('utf-8')).hexdigest()
```

### Preset Structure
```typescript
interface Preset {
  id: string;
  name: string;
  description?: string;
  version: string;
  hash: string;
  settings: CoreGenerationSettings;
  controlnet?: ControlNetRequest;
  created_at: string;
  updated_at: string;
  is_default?: boolean;
}
```

### Metadata Integration
When a preset is selected for generation, preset information is included in the workflow metadata:

```json
{
  "meta": {
    "preset": {
      "id": "preset-123",
      "name": "My Custom Preset",
      "version": "1.0.0",
      "hash": "abc123hash"
    }
  }
}
```

## Testing

### Running Tests
```bash
# Run the basic test suite
python dream_layer_backend/run_preset_tests.py

# Run pytest tests
pytest dream_layer_backend/tests/test_preset_system.py
```

### Test Coverage
- ✅ Preset creation and retrieval
- ✅ Hash validation and version pinning
- ✅ API endpoint functionality
- ✅ Default preset initialization
- ✅ Preset serialization and persistence
- ✅ Generation with preset metadata

## API Reference

### Create Preset
```http
POST /api/presets
Content-Type: application/json

{
  "name": "My Preset",
  "description": "Optional description",
  "settings": {
    "prompt": "example prompt",
    "model_name": "model.safetensors",
    "steps": 20,
    "cfg_scale": 7.0
  },
  "controlnet": {
    "enabled": true,
    "units": [...]
  }
}
```

### Get All Presets
```http
GET /api/presets
```

### Update Preset
```http
PUT /api/presets/{preset_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "settings": {
    "steps": 30
  }
}
```

### Validate Preset Hash
```http
POST /api/presets/validate-hash
Content-Type: application/json

{
  "preset_id": "preset-123",
  "settings": {...},
  "controlnet": {...}
}
```

## Future Enhancements

### Planned Features
- **Preset Categories**: Organize presets by type or use case
- **Preset Sharing**: Export/import presets between users
- **Preset Templates**: Pre-built templates for common use cases
- **Version History**: Track changes to presets over time
- **Preset Analytics**: Usage statistics and recommendations

### Technical Improvements
- **Compression**: Compress preset data for storage efficiency
- **Validation**: Enhanced validation of preset settings
- **Migration**: Automatic migration of preset formats
- **Backup**: Automatic backup of preset data 