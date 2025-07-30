# Luma Text2Img Node

## Overview

The Luma Text2Img node (`LumaImageGenerationNode`) provides text-to-image generation capabilities using the Luma AI API. This node allows users to generate high-quality images from text prompts with various customization options.

## Features

- **Text-to-Image Generation**: Convert text prompts into high-quality images
- **Multiple Models**: Support for different Luma image models (photon-1, photon-flash-1)
- **Aspect Ratio Control**: Various aspect ratios including 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, 9:21
- **Image References**: Use reference images to influence generation style
- **Style Transfer**: Apply style images with customizable weights
- **Character References**: Use character images for consistent character generation
- **Seed Control**: Reproducible results with seed parameter

## Setup

### Environment Variables

Set your Luma API key in the environment:

```bash
export LUMA_API_KEY=your-api-key
```

Or create a `.env` file in the project root:

```
LUMA_API_KEY=your-api-key
```

### API Key Handling

The node uses the ComfyUI API infrastructure for authentication. API keys are handled through hidden parameters:
- `auth_token`: AUTH_TOKEN_COMFY_ORG
- `comfy_api_key`: API_KEY_COMFY_ORG

If the API key is not set, the node will raise a clear error message:
"Missing LUMA_API_KEY. Set it as an environment variable."

## Node Parameters

### Required Parameters

- **prompt** (string): Text description of the image to generate
  - Minimum length: 3 characters
  - Supports multiline input
  - Default: ""

- **model** (combo): Luma image model to use
  - Options: photon-1, photon-flash-1
  - Default: photon-1

- **aspect_ratio** (combo): Aspect ratio of the generated image
  - Options: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9, 9:21
  - Default: 16:9

- **seed** (int): Random seed for reproducible results
  - Range: 0 to 0xFFFFFFFFFFFFFFFF
  - Default: 0
  - Note: Results are non-deterministic regardless of seed

- **style_image_weight** (float): Weight of style image influence
  - Range: 0.0 to 1.0
  - Default: 1.0
  - Step: 0.01

### Optional Parameters

- **image_luma_ref** (LUMA_REF): Reference images to influence generation
  - Up to 4 images can be considered
  - Use LumaReferenceNode to create references

- **style_image** (IMAGE): Style reference image
  - Only 1 image will be used
  - Influences the artistic style of the output

- **character_image** (IMAGE): Character reference images
  - Can be a batch of multiple images
  - Up to 4 images can be considered
  - Used for consistent character generation

### Hidden Parameters

- **auth_token**: Authentication token (automatically handled)
- **comfy_api_key**: ComfyUI API key (automatically handled)
- **unique_id**: Unique node identifier (automatically handled)

## Output

- **IMAGE**: Generated image as a torch.Tensor
  - Format: (1, H, W, C) where C is typically 3 (RGB)
  - Compatible with ComfyUI image processing nodes

## Usage Examples

### Basic Text-to-Image

```
prompt: "A beautiful sunset over mountains"
model: photon-1
aspect_ratio: 16:9
seed: 42
style_image_weight: 1.0
```

### With Style Reference

```
prompt: "A futuristic cityscape"
model: photon-flash-1
aspect_ratio: 21:9
seed: 123
style_image_weight: 0.8
style_image: [reference image]
```

### With Character Reference

```
prompt: "A portrait of a character in a fantasy setting"
model: photon-1
aspect_ratio: 1:1
seed: 456
style_image_weight: 1.0
character_image: [character reference images]
```

## API Endpoints

The node uses the following Luma API endpoints:

1. **Initial Request**: `POST /proxy/luma/generations/image`
   - Creates the image generation request
   - Returns a generation ID

2. **Polling**: `GET /proxy/luma/generations/{id}`
   - Polls for completion status
   - Returns the final image URL when complete

3. **Image Download**: Downloads the generated image from the provided URL

## Error Handling

- **Missing API Key**: Clear error message with setup instructions
- **Invalid Prompt**: Validation for minimum length and content
- **Network Errors**: Proper error handling for API communication
- **Generation Failures**: Handles failed generations gracefully

## Integration with ComfyUI

The node integrates seamlessly with other ComfyUI nodes:

- **Input**: Can receive text embeddings from CLIPTextEncode nodes
- **Output**: Compatible with image processing, upscaling, and saving nodes
- **Workflow**: Can be part of complex image generation workflows

## Testing

Run the test suite to verify functionality:

```bash
cd ComfyUI
python -m pytest tests-unit/comfy_api_nodes_test/test_luma_text2img.py -v
```

## Troubleshooting

### Common Issues

1. **"Missing LUMA_API_KEY"**
   - Solution: Set the LUMA_API_KEY environment variable
   - Check: `echo $LUMA_API_KEY` (Linux/Mac) or `echo %LUMA_API_KEY%` (Windows)

2. **"Invalid prompt"**
   - Solution: Ensure prompt is at least 3 characters long
   - Check: Remove extra whitespace and ensure meaningful content

3. **"Generation failed"**
   - Solution: Check API key validity and network connectivity
   - Check: Verify Luma API service status

4. **"Network error"**
   - Solution: Check internet connection and firewall settings
   - Check: Verify ComfyUI can access external APIs

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export COMFYUI_DEBUG=1
```

## Contributing

When contributing to the Luma Text2Img node:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any parameter changes
4. Ensure backward compatibility
5. Test with real API keys in integration tests

## License

This node is part of the DreamLayer project and follows the same licensing terms. 