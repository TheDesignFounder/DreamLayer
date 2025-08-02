# Inpainting Feature

DreamLayer AI provides powerful inpainting capabilities with support for both uploaded mask files and manual drawing tools.

## Overview

Inpainting allows you to selectively modify parts of an image while preserving the rest. This is useful for:

- Removing unwanted objects
- Adding new elements to images
- Fixing imperfections
- Creative image editing

## Mask Upload

### Supported Formats

- **File type**: PNG only
- **Size limit**: Maximum 10 MB
- **Color format**: Black and white
  - **White areas**: Will be preserved during inpainting
  - **Black areas**: Will be inpainted based on your prompt

### Usage

1. Upload your input image
2. Upload your mask file using the drop-zone
3. Enter your prompt describing what should appear in the black areas
4. Adjust denoising strength (0.0 - 1.0)
5. Click Generate

### Technical Details

- Mask files are validated for type and size
- A 128px thumbnail preview is generated
- The mask is attached as `mask=file` in multipart payloads
- Automatic scaling is applied if needed

## Manual Drawing

### Draw Mask Tool

- Click "Draw Mask" to enter drawing mode
- Use your mouse to draw on the image
- Adjust brush size for precision
- Use undo/redo for corrections

### Drawing Controls

- **Brush Size**: Adjust from 1px to 100px
- **Undo**: Remove last stroke
- **Clear**: Remove all drawn areas
- **Invert**: Swap drawn and undrawn areas

## Best Practices

### Mask Creation

- Use high-contrast masks for best results
- Ensure clean edges around areas to inpaint
- Avoid very small or very large mask areas
- Test with different denoising strengths

### Prompt Engineering

- Be specific about what should appear in masked areas
- Use negative prompts to avoid unwanted elements
- Consider the surrounding context when writing prompts
- Experiment with different prompt weights

### Technical Tips

- Higher denoising strength = more creative freedom
- Lower denoising strength = more faithful to original
- Use appropriate model for your use case
- Consider using ControlNet for complex inpainting tasks

## API Reference

### Endpoint

```
POST /api/img2img
```

### Request Format

```python
files = {
    'image': ('input.png', image_file, 'image/png'),
    'mask': ('mask.png', mask_file, 'image/png')
}

data = {
    'prompt': 'Your prompt here',
    'negative_prompt': 'Negative prompt',
    'denoising_strength': 0.75
}
```

### Response Format

```json
{
  "status": "success",
  "images": ["path/to/generated/image.png"],
  "metadata": {
    "prompt": "Your prompt here",
    "negative_prompt": "Negative prompt",
    "denoising_strength": 0.75
  }
}
```

## Troubleshooting

### Common Issues

- **Mask too large**: Reduce file size or use manual drawing
- **Poor results**: Adjust denoising strength or improve prompt
- **Upload errors**: Check file format and size limits
- **Generation fails**: Verify model compatibility

### Performance Tips

- Use smaller images for faster processing
- Optimize mask resolution for your use case
- Consider batch processing for multiple images
- Use appropriate hardware acceleration
