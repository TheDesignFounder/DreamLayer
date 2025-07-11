# Pika 2.2 Video Upgrade Guide

## Overview
This guide explains how to upgrade the current Pika single-frame implementation to full video generation.

## Current Implementation
The current `pika_frame` node generates stylized single frames by:
1. Calling Pika API with `video: false`
2. Extracting exactly one frame from the response
3. Converting to PNG format
4. Exposing motion_strength parameter (unused in single-frame mode)

## Upgrade to Full Video Generation

### 1. API Changes Required

#### Current API Call (Single Frame)
```typescript
const apiRequest = {
  prompt_text: "A beautiful sunset over mountains",
  negative_prompt: "blurry, low quality",
  seed: 12345,
  resolution: "1080p",
  duration: "5s",
  aspect_ratio: 1.7778,
  motion_strength: 0.7,
  video: false, // SINGLE FRAME MODE
};
```

#### Upgraded API Call (Full Video)
```typescript
const apiRequest = {
  prompt_text: "A beautiful sunset over mountains",
  negative_prompt: "blurry, low quality",
  seed: 12345,
  resolution: "1080p",
  duration: "5s",
  aspect_ratio: 1.7778,
  motion_strength: 0.7,
  video: true, // FULL VIDEO MODE
};
```

### 2. Response Format Changes

#### Current Response (Single Frame)
```typescript
interface PikaFrameResponse {
  success: boolean;
  frame_url: string; // Single PNG frame
  generation_id: string;
}
```

#### Upgraded Response (Full Video)
```typescript
interface PikaVideoResponse {
  success: boolean;
  video_url: string; // Full video file (MP4)
  duration: number; // Video duration in seconds
  frame_count: number; // Total frames in video
  frames?: string[]; // Optional individual frame URLs
  generation_id: string;
}
```

### 3. Component Updates Required

#### File: `src/types/pika.ts`
```typescript
// Add new interfaces for video mode
export interface PikaVideoRequest extends PikaFrameRequest {
  video: true; // Always true for video mode
}

export interface PikaVideoResponse {
  success: boolean;
  video_url: string;
  duration: number;
  frame_count: number;
  frames?: string[];
  generation_id: string;
}

export interface PikaVideoResult {
  id: string;
  video_url: string;
  duration: number;
  frame_count: number;
  prompt: string;
  negative_prompt: string;
  settings: PikaFrameSettings;
  timestamp: number;
}
```

#### File: `src/services/pikaService.ts`
```typescript
// Add new service function for video generation
export const generatePikaVideo = async (request: PikaVideoRequest): Promise<PikaVideoResult> => {
  const apiRequest = {
    ...request,
    video: true, // CRITICAL: Set to true for video generation
  };

  // Make API call...
  const response = await fetch(PIKA_API_CONFIG.ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(apiRequest),
  });

  const data: PikaVideoResponse = await response.json();
  
  // Verify we got a video URL
  if (!data.success || !data.video_url) {
    throw new Error('Failed to generate video');
  }

  return {
    id: `pika-video-${Date.now()}`,
    video_url: data.video_url,
    duration: data.duration,
    frame_count: data.frame_count,
    prompt: request.prompt_text,
    negative_prompt: request.negative_prompt,
    settings: request,
    timestamp: Date.now(),
  };
};
```

#### File: `src/stores/usePikaStore.ts`
```typescript
// Add video-specific state
interface PikaState {
  // ... existing frame state
  videos: PikaVideoResult[];
  
  // Add video actions
  addVideo: (video: PikaVideoResult) => void;
  removeVideo: (videoId: string) => void;
  clearVideos: () => void;
}
```

#### File: `src/components/PikaFrameGenerator.tsx`
```typescript
// Add video mode toggle
const [videoMode, setVideoMode] = useState(false);

// Update generation function
const handleGenerate = async () => {
  if (videoMode) {
    // Call generatePikaVideo instead of generatePikaFrame
    const result = await generatePikaVideo({
      ...settings,
      video: true,
    });
    actions.addVideo(result);
  } else {
    // Existing frame generation logic
    const result = await generatePikaFrame({
      ...settings,
      video: false,
    });
    actions.addFrame(result);
  }
};

// Add video player component
const VideoPlayer = ({ videoUrl }: { videoUrl: string }) => (
  <video 
    controls 
    className="w-full h-full object-cover rounded-lg"
    src={videoUrl}
  >
    Your browser does not support the video tag.
  </video>
);
```

### 4. UI/UX Enhancements for Video Mode

#### Motion Strength Becomes Active
- In single-frame mode: Parameter is exposed but unused
- In video mode: Controls the amount of motion/animation in the generated video
- Range: 0.0 (minimal motion) to 1.0 (maximum motion)

#### Duration Controls
- Single-frame mode: Duration is ignored
- Video mode: Duration determines video length (3s, 5s, 10s, 15s)

#### Video Preview
- Replace static image preview with video player
- Add video controls (play, pause, seek)
- Show video metadata (duration, frame count)

#### Download Options
- Single-frame mode: Download PNG
- Video mode: Download MP4, or extract individual frames

### 5. Implementation Steps

1. **Add Video Mode Toggle**
   ```typescript
   const [videoMode, setVideoMode] = useState(false);
   ```

2. **Update API Integration**
   ```typescript
   const generateContent = videoMode ? generatePikaVideo : generatePikaFrame;
   ```

3. **Add Video Player Component**
   ```typescript
   {videoMode ? (
     <VideoPlayer videoUrl={result.video_url} />
   ) : (
     <img src={result.frame_url} alt="Generated frame" />
   )}
   ```

4. **Enable Motion Strength**
   ```typescript
   // Motion strength becomes functional in video mode
   <Slider
     value={[settings.motion_strength]}
     onValueChange={(value) => actions.setMotionStrength(value[0])}
     disabled={!videoMode} // Only enabled in video mode
   />
   ```

5. **Update Progress Handling**
   ```typescript
   // Video generation typically takes longer
   const timeout = videoMode ? 60000 : 30000; // 60s for video, 30s for frame
   ```

### 6. Backend Integration Notes

#### Endpoint Changes
- Current: `/api/pika/frame` (single frame)
- Video: `/api/pika/video` (full video) or same endpoint with `video: true`

#### Response Validation
```typescript
// Current: Verify PNG frame
if (!data.frame_url || !data.frame_url.includes('.png')) {
  throw new Error('Invalid frame response');
}

// Video: Verify MP4 video
if (!data.video_url || !data.video_url.includes('.mp4')) {
  throw new Error('Invalid video response');
}
```

### 7. Testing Strategy

1. **Single Frame Mode** (Current)
   - ✅ Verify `video: false` in API call
   - ✅ Confirm exactly one frame extracted
   - ✅ Validate PNG format
   - ✅ Test motion_strength parameter (unused)

2. **Video Mode** (Upgraded)
   - ✅ Verify `video: true` in API call
   - ✅ Confirm video URL in response
   - ✅ Validate MP4 format
   - ✅ Test motion_strength parameter (functional)
   - ✅ Verify duration matches request
   - ✅ Test video playback

### 8. Configuration Changes

#### Environment Variables
```env
# Single frame mode
PIKA_MODE=frame
PIKA_TIMEOUT=30000

# Video mode
PIKA_MODE=video
PIKA_TIMEOUT=60000
```

#### Feature Flags
```typescript
const ENABLE_PIKA_VIDEO = process.env.ENABLE_PIKA_VIDEO === 'true';
```

### 9. Performance Considerations

- **Single Frame**: ~5-15 seconds generation time
- **Full Video**: ~30-60 seconds generation time
- **Storage**: Videos are significantly larger than single frames
- **Bandwidth**: Video streaming requires more bandwidth

### 10. Error Handling Updates

```typescript
// Add video-specific error types
export enum PikaErrorType {
  // ... existing errors
  VIDEO_GENERATION_ERROR = 'video_generation_error',
  VIDEO_PROCESSING_ERROR = 'video_processing_error',
  VIDEO_TIMEOUT_ERROR = 'video_timeout_error',
}
```

## Summary

The current implementation provides a solid foundation for video generation. The upgrade path is straightforward:

1. **Change `video: false` to `video: true`**
2. **Handle video response format instead of frame extraction**
3. **Make motion_strength parameter functional**
4. **Add video player UI components**
5. **Update progress and timeout handling**

This modular approach allows for easy switching between single-frame and full-video modes, making the component highly flexible for different use cases.