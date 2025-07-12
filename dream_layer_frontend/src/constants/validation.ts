// Validation constants for input limits and ranges
export const VALIDATION_LIMITS = {
  // Image dimensions
  DIMENSION: {
    MIN: 64,
    MAX: 2048,
    DEFAULT: 512,
  },
  
  // Batch processing
  BATCH_SIZE: {
    MIN: 1,
    MAX: 8,
    DEFAULT: 1,
  },
  
  // Sampling parameters
  STEPS: {
    MIN: 1,
    MAX: 150,
    DEFAULT: 20,
  },
  
  CFG_SCALE: {
    MIN: 1.0,
    MAX: 20.0,
    DEFAULT: 7.0,
  },
  
  // Pika specific limits
  ASPECT_RATIO: {
    MIN: 0.4,
    MAX: 2.5,
    DEFAULT: 1.7778, // 16:9
  },
  
  MOTION_STRENGTH: {
    MIN: 0,
    MAX: 1,
    DEFAULT: 0.7,
  },
  
  // Base64 detection
  BASE64_MIN_LENGTH: 100,
  
  // Seed range
  SEED_MAX_VALUE: 2**32 - 1,
} as const;

// Common aspect ratios
export const ASPECT_RATIOS = {
  WIDESCREEN: 1.7778, // 16:9
  STANDARD: 1.3333,   // 4:3
  SQUARE: 1.0,        // 1:1
  PORTRAIT: 0.75,     // 3:4
} as const;

// Pika enumeration constants
export const PIKA_CONSTANTS = {
  VALID_RESOLUTIONS: ["720p", "1080p", "1440p", "4K"] as const,
  VALID_DURATIONS: ["3s", "5s", "10s", "15s"] as const,
  TIMEOUT_MS: 30000,
} as const;