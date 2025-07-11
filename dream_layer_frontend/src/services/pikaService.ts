// Pika 2.2 API service for single-frame video generation
// Implements the ComfyUI Pika text-to-video API with video=false for frame extraction

import { 
  PikaFrameRequest, 
  PikaFrameResponse, 
  PikaFrameResult,
  PikaError,
  PikaErrorType,
  PIKA_API_CONFIG,
  validatePikaFrameRequest 
} from '@/types/pika';

/**
 * Generate a single frame from Pika 2.2 text-to-video API
 * This calls the Pika API with video=false to extract exactly one frame
 */
export const generatePikaFrame = async (request: PikaFrameRequest): Promise<PikaFrameResult> => {
  // Validate request
  if (!validatePikaFrameRequest(request)) {
    throw new Error('Invalid Pika frame request parameters');
  }

  try {
    // Prepare API request with video=false for single frame extraction
    const apiRequest = {
      ...request,
      video: false, // CRITICAL: Set to false for single frame extraction
    };

    console.log('🎬 Pika API: Generating single frame with request:', apiRequest);

    // Make API call to backend
    const response = await fetch(PIKA_API_CONFIG.ENDPOINT, {
      method: PIKA_API_CONFIG.METHOD,
      headers: {
        'Content-Type': PIKA_API_CONFIG.CONTENT_TYPE,
      },
      body: JSON.stringify(apiRequest),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Pika API Error:', response.status, errorText);
      
      throw {
        type: PikaErrorType.API_ERROR,
        message: `Pika API error: ${response.status}`,
        details: errorText,
      } as PikaError;
    }

    const data: PikaFrameResponse = await response.json();
    console.log('✅ Pika API Response:', data);

    // Verify we got exactly one frame
    if (!data.success || !data.frame_url) {
      throw {
        type: PikaErrorType.FRAME_EXTRACTION_ERROR,
        message: 'Failed to extract frame from Pika response',
        details: data,
      } as PikaError;
    }

    // Verify the frame is a PNG (as required by the challenge)
    if (!data.frame_url.toLowerCase().includes('.png')) {
      console.warn('⚠️ Pika API: Frame URL does not appear to be PNG format');
    }

    // Create result object
    const result: PikaFrameResult = {
      id: `pika-frame-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      frame_url: data.frame_url,
      prompt: request.prompt_text,
      negative_prompt: request.negative_prompt,
      settings: {
        prompt_text: request.prompt_text,
        negative_prompt: request.negative_prompt,
        seed: request.seed || 0,
        resolution: request.resolution || "1080p",
        duration: request.duration || "5s",
        aspect_ratio: request.aspect_ratio || 1.7778,
        motion_strength: request.motion_strength || 0.5,
      },
      timestamp: Date.now(),
      generation_id: data.generation_id,
    };

    console.log('🖼️ Pika Frame Generated:', result);
    return result;

  } catch (error) {
    console.error('❌ Pika Frame Generation Error:', error);
    
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw {
        type: PikaErrorType.NETWORK_ERROR,
        message: 'Network error connecting to Pika API',
        details: error.message,
      } as PikaError;
    }
    
    // Handle timeout errors
    if (error instanceof Error && error.name === 'AbortError') {
      throw {
        type: PikaErrorType.TIMEOUT_ERROR,
        message: 'Pika API request timed out',
        details: error.message,
      } as PikaError;
    }
    
    // Re-throw known Pika errors
    if (error && typeof error === 'object' && 'type' in error) {
      throw error;
    }
    
    // Handle unknown errors
    throw {
      type: PikaErrorType.API_ERROR,
      message: error instanceof Error ? error.message : 'Unknown Pika API error',
      details: error,
    } as PikaError;
  }
};

/**
 * Test connection to Pika API
 * Useful for debugging and health checks
 */
export const testPikaConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${PIKA_API_CONFIG.ENDPOINT}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.ok;
  } catch (error) {
    console.error('❌ Pika Connection Test Failed:', error);
    return false;
  }
};

/**
 * Validate that a frame URL is accessible and returns a PNG
 * This ensures the extracted frame is valid
 */
export const validatePikaFrame = async (frameUrl: string): Promise<boolean> => {
  try {
    const response = await fetch(frameUrl, { method: 'HEAD' });
    
    if (!response.ok) {
      return false;
    }
    
    const contentType = response.headers.get('content-type');
    return contentType?.includes('image/png') || false;
    
  } catch (error) {
    console.error('❌ Pika Frame Validation Error:', error);
    return false;
  }
};

/**
 * Convert video settings to frame settings
 * Useful for future video upgrade compatibility
 */
export const convertVideoSettingsToFrame = (videoSettings: any): PikaFrameRequest => {
  return {
    prompt_text: videoSettings.prompt_text || '',
    negative_prompt: videoSettings.negative_prompt || '',
    seed: videoSettings.seed || 0,
    resolution: videoSettings.resolution || '1080p',
    duration: videoSettings.duration || '5s',
    aspect_ratio: videoSettings.aspect_ratio || 1.7778,
    motion_strength: videoSettings.motion_strength || 0.5,
    video: false, // Always false for frame extraction
  };
};

/**
 * Generate a random seed for Pika frame generation
 */
export const generatePikaSeed = (): number => {
  return Math.floor(Math.random() * 1000000);
};

/**
 * Format Pika error for display
 */
export const formatPikaError = (error: PikaError): string => {
  switch (error.type) {
    case PikaErrorType.VALIDATION_ERROR:
      return `Validation Error: ${error.message}`;
    case PikaErrorType.API_ERROR:
      return `API Error: ${error.message}`;
    case PikaErrorType.NETWORK_ERROR:
      return `Network Error: ${error.message}`;
    case PikaErrorType.TIMEOUT_ERROR:
      return `Timeout Error: ${error.message}`;
    case PikaErrorType.FRAME_EXTRACTION_ERROR:
      return `Frame Extraction Error: ${error.message}`;
    default:
      return `Unknown Error: ${error.message}`;
  }
};