# Dream Layer Backend

This directory contains the backend server components for the Dream Layer project.

## Components

- `dream_layer.py`: Main application file
- `txt2img_server.py`: Text-to-Image generation server
- `img2img_server.py`: Image-to-Image generation server

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the servers:

```bash
# Start comfyui server
python dream_layer.py

# Start txt2img server
python txt2img_server.py

# Start img2img server (in a separate terminal)
python img2img_server.py
```

The servers will be available at:

- Text-to-Image API: http://localhost:5001/api/txt2img
- Image-to-Image API: http://localhost:5001/api/img2img

## Production Server & Timeout for Long Image Generation

For long-running image generation jobs (especially on CPU), the default Flask development server may time out before the job completes. To avoid this, we recommend running the txt2img server with [waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/):

```
pip install waitress
python txt2img_server.py
```

This will:

- Serve the API using waitress (production-grade WSGI server)
- Set a 30 minute (1800 seconds) timeout for requests, so even very slow jobs do not fail

If waitress is not installed, the server will fall back to Flask's development server, which is not recommended for production or long jobs.

## Inpainting Mask Support

- The backend now supports inpainting with masks by inserting a `VAEEncodeForInpaint` node into the workflow when a mask is uploaded.
- The output of `VAEEncodeForInpaint` is used as the `latent_image` input to the `KSampler` node. **Do not** add a `mask` input to `KSampler`.
- This matches ComfyUI's standard inpainting design and avoids errors.

### Troubleshooting

- **Error:** `KSampler.sample() got an unexpected keyword argument 'mask'`
  - **Cause:** The workflow tried to pass a `mask` input to the `KSampler` node, which is not supported.
  - **Fix:** The workflow builder now uses `VAEEncodeForInpaint` to encode the image and mask, and wires its output to `KSampler`'s `latent_image` input. No `mask` input is added to `KSampler`.
