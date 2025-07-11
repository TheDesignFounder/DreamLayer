# Pika Frame Node - Single Frame Generation

## 🎯 Overview

The **Pika Frame Node** generates stylized still frames using the Pika 2.2 API by requesting minimum duration video and extracting the first frame. This node is designed to output high-quality single frames while maintaining compatibility for future video generation upgrades.

## 🔧 Technical Implementation

### Key Features:
- **Single Frame Output**: Calls Pika API with minimum duration (5s) and extracts first frame
- **Frame Verification**: Ensures exactly one frame is returned from the API
- **PNG Extraction**: Extracts the frame and converts it to PNG format
- **Motion Strength Parameter**: Exposes `motion_strength` for future video functionality

### Node Parameters:
- **`image`**: Input image to generate a stylized frame from
- **`prompt_text`**: Text prompt for stylization (multiline)
- **`negative_prompt`**: Negative prompt to avoid unwanted features
- **`seed`**: Random seed for reproducible results
- **`resolution`**: Output resolution (1080p, 720p)
- **`motion_strength`**: Motion strength parameter (0.0-1.0, currently unused)

## 🚀 Usage

1. **Connect an input image** to the `image` input
2. **Set your prompt** describing the desired stylization
3. **Adjust resolution** based on your needs
4. **Set motion_strength** (preserved for future video upgrades)
5. **Execute** to generate a single stylized frame

## 📈 Upgrading to Full Video Generation

### Option 1: Modify Existing Node

To upgrade the current node to generate full videos:

```python
# Change the duration for longer videos
pika_request_data = PikaBodyGenerate22I2vGenerate22I2vPost(
    promptText=prompt_text,
    negativePrompt=negative_prompt,
    seed=seed,
    resolution=resolution,
    duration=duration,  # Use actual duration (5 or 10 seconds)
)

# Update return type and processing
RETURN_TYPES = ("VIDEO",)  # Change from IMAGE to VIDEO

# Use motion_strength parameter in video generation
def generate_video(self, ...):
    # Apply motion_strength to video generation parameters
    # This parameter controls the amount of motion in the generated video
    pass
```

### Option 2: Create New Video Node

Create a separate `PikaVideoNode` that extends the frame node:

```python
class PikaVideoNode(PikaFrameNode):
    """Extended version for full video generation."""
    
    RETURN_TYPES = ("VIDEO",)
    FUNCTION = "generate_video"
    DESCRIPTION = "Generate full videos using Pika 2.2 API with motion_strength."
    
    @classmethod
    def INPUT_TYPES(cls):
        inputs = super().INPUT_TYPES()
        inputs["required"]["duration"] = (
            IO.INT,
            {"default": 3, "min": 1, "max": 10, "step": 1},
        )
        return inputs
    
    def generate_video(self, motion_strength: float, duration: int, **kwargs):
        # Use motion_strength for video generation
        # Return video instead of single frame
        pass
```

## 🎨 Motion Strength Parameter

The `motion_strength` parameter (0.0-1.0) is included for future video generation:

- **0.0**: Minimal motion, close to still frame
- **0.5**: Moderate motion, balanced animation
- **1.0**: Maximum motion, dynamic animation

**Current Status**: Parameter is exposed but not used in single-frame generation. When upgrading to video, this parameter will control the intensity of motion in the generated video.

## 🔍 API Integration Details

### Request Structure:
```python
# Single frame request (minimum duration, extract first frame)
pika_request_data = PikaBodyGenerate22I2vGenerate22I2vPost(
    promptText=prompt_text,
    negativePrompt=negative_prompt,
    seed=seed,
    resolution=resolution,
    duration=5,  # Minimum duration (extract first frame)
)
```

### Frame Extraction:
1. **API Call**: Submit request to Pika API with minimum duration (5s)
2. **Polling**: Wait for completion using task ID
3. **Download**: Download generated video from response URL
4. **Extraction**: Extract first frame from video using OpenCV
5. **Conversion**: Convert frame to PNG tensor format
6. **Validation**: Verify tensor shape is `[1, H, W, C]`

## 📋 Error Handling

The node includes robust error handling:
- **API Failures**: Detailed error messages with response codes
- **Frame Count Validation**: Ensures exactly one frame is returned
- **Download Failures**: Handles network issues during frame extraction
- **Processing Errors**: Catches OpenCV and PIL processing errors

## 🧪 Testing

To test the node:
1. **Verify API Connection**: Check that Pika API credentials are configured
2. **Test Single Frame**: Confirm exactly one frame is returned
3. **Validate PNG Format**: Ensure output is valid PNG tensor
4. **Check Motion Parameter**: Verify `motion_strength` is exposed (even if unused)

## 🔄 Future Enhancements

When upgrading to full video generation:
1. **Enable Video Mode**: Set `video=True` in API request
2. **Use Motion Strength**: Apply parameter to control video motion
3. **Handle Video Output**: Process video files instead of single frames
4. **Update Duration**: Use actual duration instead of fixed value
5. **Enhance Polling**: Adjust timeout for longer video generation

---

**Implementation Status**: ✅ Complete  
**API Integration**: ✅ Pika 2.2 Compatible  
**Single Frame Output**: ✅ Verified  
**Motion Strength**: ✅ Exposed for Future Use  
**Upgrade Path**: ✅ Documented