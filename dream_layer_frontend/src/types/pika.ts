// Pika 2.2 API types and interfaces for single-frame video generation
// Based on ComfyUI Pika text-to-video API documentation

import { VALIDATION_LIMITS, PIKA_CONSTANTS, ASPECT_RATIOS } from '@/constants/validation';
import { API_ENDPOINTS, API_TIMEOUTS } from '@/constants/api';

export interface PikaFrameRequest {
  // Required parameters
  prompt_text: string;
  negative_prompt: string;
  
  // Optional parameters with defaults
  seed?: number; // default: 0
  resolution?: PikaResolution; // default: "1080p"
  duration?: PikaDuration; // default: "5s"
  aspect_ratio?: number; // default: 1.7778, range: 0.4-2.5
  
  // Motion strength parameter (exposed for future video upgrade)
  motion_strength?: number; // default: 0.5, range: 0-1
  
  // Single frame mode flag
  video?: boolean; // Set to false for single frame extraction
}

export interface PikaFrameResponse {
  success: boolean;
  frame_url?: string; // URL to the extracted PNG frame
  error?: string;
  generation_id?: string;
  timestamp?: number;
}

export interface PikaFrameSettings {
  prompt_text: string;
  negative_prompt: string;
  seed: number;
  resolution: PikaResolution;
  duration: PikaDuration;
  aspect_ratio: number;
  motion_strength: number;
}

// Pika resolution options
export type PikaResolution = 
  | "720p"
  | "1080p"
  | "1440p"
  | "4K";

// Pika duration options (for future video upgrade)
export type PikaDuration = 
  | "3s"
  | "5s"
  | "10s"
  | "15s";

// Default settings for Pika frame generation
export const defaultPikaFrameSettings: PikaFrameSettings = {
  prompt_text: "",
  negative_prompt: "",
  seed: 0,
  resolution: "1080p",
  duration: "5s", // Used for aspect ratio calculation
  aspect_ratio: 1.7778, // 16:9 aspect ratio
  motion_strength: 0.5, // Exposed for future video upgrade
};

// Pika frame generation result
export interface PikaFrameResult {
  id: string;
  frame_url: string;
  prompt: string;
  negative_prompt: string;
  settings: PikaFrameSettings;
  timestamp: number;
  generation_id?: string;
}

// API endpoint configuration
export const PIKA_API_CONFIG = {
  ENDPOINT: API_ENDPOINTS.PIKA_SERVICE.BASE,
  METHOD: 'POST',
  CONTENT_TYPE: 'application/json',
  TIMEOUT: API_TIMEOUTS.DEFAULT,
};

// Validation functions
export const validatePikaFrameRequest = (request: PikaFrameRequest): boolean => {
  // Basic validation
  if (!request.prompt_text || request.prompt_text.trim().length === 0) {
    return false;
  }
  
  // Resolution validation
  if (request.resolution !== undefined) {
    if (!PIKA_CONSTANTS.VALID_RESOLUTIONS.includes(request.resolution)) {
      return false;
    }
  }
  
  // Duration validation
  if (request.duration !== undefined) {
    if (!PIKA_CONSTANTS.VALID_DURATIONS.includes(request.duration)) {
      return false;
    }
  }
  
  // Aspect ratio validation
  if (request.aspect_ratio !== undefined) {
    if (request.aspect_ratio < VALIDATION_LIMITS.ASPECT_RATIO.MIN || 
        request.aspect_ratio > VALIDATION_LIMITS.ASPECT_RATIO.MAX) {
      return false;
    }
  }
  
  // Motion strength validation
  if (request.motion_strength !== undefined) {
    if (request.motion_strength < VALIDATION_LIMITS.MOTION_STRENGTH.MIN || 
        request.motion_strength > VALIDATION_LIMITS.MOTION_STRENGTH.MAX) {
      return false;
    }
  }
  
  return true;
};

// Helper function to get aspect ratio display name
export const getAspectRatioDisplayName = (ratio: number): string => {
  const commonRatios: Record<number, string> = {
    1.7778: "16:9 (Widescreen)",
    1.3333: "4:3 (Standard)",
    1.0: "1:1 (Square)",
    0.5625: "9:16 (Vertical)",
    2.4: "21:9 (Ultrawide)",
  };
  
  // Find closest match
  const closest = Object.keys(commonRatios)
    .map(Number)
    .reduce((prev, curr) => 
      Math.abs(curr - ratio) < Math.abs(prev - ratio) ? curr : prev
    );
  
  return commonRatios[closest] || `${ratio.toFixed(2)}:1`;
};

// Error types for Pika API
export enum PikaErrorType {
  VALIDATION_ERROR = 'validation_error',
  API_ERROR = 'api_error',
  NETWORK_ERROR = 'network_error',
  TIMEOUT_ERROR = 'timeout_error',
  FRAME_EXTRACTION_ERROR = 'frame_extraction_error',
}

export interface PikaError {
  type: PikaErrorType;
  message: string;
  details?: any;
}