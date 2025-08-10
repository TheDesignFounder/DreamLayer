import { ControlNetRequest } from './controlnet';
import { LoraRequest } from './lora';

export interface CoreGenerationSettings {
  // Basic Settings
  prompt: string;
  negative_prompt: string;
  model_name: string;
  lora: LoraRequest | null;  // LoRA configuration, null if none selected

  // Sampling Settings
  sampler_name: string;  // e.g., "euler", "dpm++", etc.
  scheduler: string;     // e.g., "normal", "karras", etc.
  steps: number;         // Range: 1-150, Default: 20
  cfg_scale: number;     // Range: 1-20, Default: 7.0
  denoising_strength?: number; // Range: 0-1, Default: 0.75 (for img2img)

  // Size Settings
  width: number;         // Range: 64-2048, Default: 512
  height: number;        // Range: 64-2048, Default: 512
  resize_mode?: string;  // e.g., "just_resize", "crop_and_resize", "fill"

  // Batch Settings
  batch_size: number;    // Default: 1
  batch_count: number;   // Default: 1

  // Seed Settings
  seed: number;         // -1 for random, or specific seed value
  random_seed: boolean; // Whether to use random seed each time

  // Image Input Settings (for img2img)
  input_image?: string;  // Base64 encoded image data
  mask?: string;        // Base64 encoded mask data for inpainting

  // Advanced Settings
  vae_name?: string;    // Name of the VAE model to use
  clip_skip?: number;   // Number of CLIP layers to skip
  tiling?: boolean;     // Enable seamless tiling
  tile_size?: number;   // Tile size for tiling (default: 512)
  tile_overlap?: number; // Overlap between tiles (default: 64)
  hires_fix?: boolean;  // Enable hires fix
  karras_sigmas?: boolean; // Use Karras sigmas scheduling

  // Hires.fix Settings
  hires_fix_enabled?: boolean;        // Enable hires fix
  hires_fix_upscale_method?: string;  // "upscale-by" or "resize-to"
  hires_fix_upscale_factor?: number;  // Range: 1-10, Default: 2.5
  hires_fix_hires_steps?: number;     // Range: 1-30, Default: 15
  hires_fix_denoising_strength?: number; // Range: 0-1, Default: 0.5
  hires_fix_resize_width?: number;    // Range: 64-8192, Default: 4000
  hires_fix_resize_height?: number;   // Range: 64-8192, Default: 4000
  hires_fix_upscaler?: string;        // Upscaler model name, Default: "4x-ultrasharp"

  // Face Restoration Settings
  restore_faces?: boolean;        // Enable face restoration
  face_restoration_model?: string; // "codeformer" or "gfpgan"
  codeformer_weight?: number;     // Range: 0-1, Default: 0.5
  gfpgan_weight?: number;         // Range: 0-1, Default: 0.5

  // Refiner Settings
  refiner_enabled?: boolean;
  refiner_model?: string;
  refiner_switch_at?: number;
}

// Default values for core generation settings
export const defaultCoreSettings: CoreGenerationSettings = {
  prompt: '',
  negative_prompt: '',
  model_name: 'v1-6-pruned-emaonly-fp16.safetensors',
  sampler_name: 'euler',
  scheduler: 'normal',
  steps: 20,
  cfg_scale: 7.0,
  denoising_strength: 0.75,
  width: 512,
  height: 512,
  batch_size: 1,
  batch_count: 1,
  seed: -1,
  random_seed: true,
  clip_skip: 1,
  tiling: false,
  tile_size: 512,
  tile_overlap: 64,
  hires_fix: false,
  karras_sigmas: false,
  lora: null,
  restore_faces: false,
  face_restoration_model: 'codeformer',
  codeformer_weight: 0.5,
  gfpgan_weight: 0.5,
  // Hires.fix defaults
  hires_fix_enabled: false,
  hires_fix_upscale_method: 'upscale-by',
  hires_fix_upscale_factor: 2.5,
  hires_fix_hires_steps: 15,
  hires_fix_denoising_strength: 0.5,
  hires_fix_resize_width: 4000,
  hires_fix_resize_height: 4000,
  hires_fix_upscaler: '4x-ultrasharp',
  refiner_enabled: false,
  refiner_model: 'none',
  refiner_switch_at: 0.8
};

// Type for the response from the backend
export interface GenerationResponse {
  status: 'success' | 'error';
  message: string;
  comfy_response?: {
    prompt_id: string;
    generated_images?: Array<{
      filename: string;
      type: string;
      subfolder?: string;
      url: string;
    }>;
  };
  workflow?: any;
  error?: string;
}

// Type for the gallery image results
export interface ImageResult {
  id: string;
  url: string;
  prompt: string;
  negativePrompt: string;
  timestamp: number;
  settings: Partial<CoreGenerationSettings>;
  matrixInfo?: { // Optional property for matrix generation info
    xValue: string | number | null;
    yValue: string | number | null;
    zValue: string | number | null;
  };
}

// Type for txt2img specific settings
export interface Txt2ImgCoreSettings extends CoreGenerationSettings {
  // Any additional txt2img specific settings can be added here
}

// Default values for txt2img settings
export const defaultTxt2ImgSettings: Txt2ImgCoreSettings = {
  ...defaultCoreSettings,
  // Override any default values specific to txt2img here
};

// --- Matrix Generation Types ---

// The parameters that can be used in the matrix
export const MATRIX_PARAMETERS = [
  'Nothing',
  'Seed',
  'Steps',
  'CFG Scale',
  'Sampler',
  'Denoising',
  'Clip skip',
  'Hires steps',
] as const;

export type MatrixParameterName = typeof MATRIX_PARAMETERS[number];

export interface MatrixParameter {
  name: MatrixParameterName;
  type: 'range' | 'list';
  values: string; // Comma-separated or range (e.g., "1-5")
  enabled: boolean;
}

export interface MatrixSettings {
  xAxis: MatrixParameter;
  yAxis: MatrixParameter;
  zAxis: MatrixParameter;
  drawLegend: boolean;
  includeSubImages: boolean;
  includeSubgrids: boolean;
  keepSeedsForRows: boolean;
}

export interface MatrixJob {
  id: string;
  settings: CoreGenerationSettings;
  xValue: string | number | null;
  yValue: string | number | null;
  zValue: string | number | null;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: any;
}

export const defaultMatrixParameter: MatrixParameter = {
  name: 'Nothing',
  type: 'list',
  values: '',
  enabled: false,
};

export const defaultMatrixSettings: MatrixSettings = {
  xAxis: { ...defaultMatrixParameter },
  yAxis: { ...defaultMatrixParameter },
  zAxis: { ...defaultMatrixParameter },
  drawLegend: true,
  includeSubImages: false,
  includeSubgrids: false,
  keepSeedsForRows: true,
}; 