import { CoreGenerationSettings } from './generationSettings';
import { ControlNetRequest } from './controlnet';

export interface Preset {
  id: string;
  name: string;
  description?: string;
  version: string;
  hash: string;
  settings: CoreGenerationSettings;
  controlnet?: ControlNetRequest;
  created_at: string;
  updated_at: string;
  is_default?: boolean;
}

export interface PresetCreateRequest {
  name: string;
  description?: string;
  settings: CoreGenerationSettings;
  controlnet?: ControlNetRequest;
}

export interface PresetUpdateRequest {
  name?: string;
  description?: string;
  settings?: CoreGenerationSettings;
  controlnet?: ControlNetRequest;
}

export interface PresetResponse {
  status: 'success' | 'error';
  message?: string;
  preset?: Preset;
  presets?: Preset[];
}

// Default presets
export const DEFAULT_PRESETS: Omit<Preset, 'id' | 'hash' | 'created_at' | 'updated_at'>[] = [
  {
    name: 'SDXL Base',
    description: 'Standard SDXL generation settings',
    version: '1.0.0',
    settings: {
      prompt: '',
      negative_prompt: '',
      model_name: 'juggernautXL_v8Rundiffusion.safetensors',
      sampler_name: 'euler',
      scheduler: 'normal',
      steps: 20,
      cfg_scale: 7.0,
      width: 1024,
      height: 1024,
      batch_size: 1,
      batch_count: 1,
      seed: -1,
      random_seed: true,
      lora: null
    }
  },
  {
    name: 'Base + Refiner',
    description: 'SDXL with refiner for enhanced quality',
    version: '1.0.0',
    settings: {
      prompt: '',
      negative_prompt: '',
      model_name: 'juggernautXL_v8Rundiffusion.safetensors',
      sampler_name: 'euler',
      scheduler: 'normal',
      steps: 20,
      cfg_scale: 7.0,
      width: 1024,
      height: 1024,
      batch_size: 1,
      batch_count: 1,
      seed: -1,
      random_seed: true,
      lora: null,
      refiner_enabled: true,
      refiner_model: 'sd_xl_refiner_1.0.safetensors',
      refiner_switch_at: 0.8
    }
  },
  {
    name: 'Fast Generation',
    description: 'Optimized for speed with fewer steps',
    version: '1.0.0',
    settings: {
      prompt: '',
      negative_prompt: '',
      model_name: 'juggernautXL_v8Rundiffusion.safetensors',
      sampler_name: 'euler',
      scheduler: 'normal',
      steps: 10,
      cfg_scale: 7.0,
      width: 512,
      height: 512,
      batch_size: 1,
      batch_count: 1,
      seed: -1,
      random_seed: true,
      lora: null
    }
  }
]; 