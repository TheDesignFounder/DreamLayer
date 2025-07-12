// API configuration constants
export const API_ENDPOINTS = {
  MODEL_SERVICE: {
    BASE: process.env.REACT_APP_MODEL_SERVICE_URL || 'http://localhost:5002',
    MODELS: '/api/models',
    FETCH_PROMPT: '/api/fetch-prompt',
    UPSCALER_MODELS: '/api/upscaler-models',
  },
  
  PIKA_SERVICE: {
    BASE: process.env.REACT_APP_PIKA_API_ENDPOINT || '/api/pika/frame',
    FRAME: '/frame',
    VIDEO: '/video',
  },
  
  COMFY_UI: {
    BASE: process.env.REACT_APP_COMFY_API_URL || 'http://127.0.0.1:8188',
  },
} as const;

// Server ports
export const SERVER_PORTS = {
  IMG2IMG: parseInt(process.env.IMG2IMG_PORT || '5004'),
  EXTRAS: parseInt(process.env.EXTRAS_PORT || '5003'),
  MODEL_SERVICE: parseInt(process.env.MODEL_SERVICE_PORT || '5002'),
} as const;

// API timeouts
export const API_TIMEOUTS = {
  DEFAULT: 30000,
  UPLOAD: 60000,
  GENERATION: 120000,
} as const;