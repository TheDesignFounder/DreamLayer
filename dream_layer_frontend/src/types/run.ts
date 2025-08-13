/**
 * Type definitions for generation runs
 */

export interface RunConfig {
  // Core generation parameters
  model: string;
  vae: string;
  prompt: string;
  negative_prompt: string;
  seed: number;
  sampler: string;
  scheduler: string;
  steps: number;
  cfg_scale: number;
  width: number;
  height: number;
  batch_size: number;
  
  // Advanced features
  loras: Record<string, any>;
  controlnets: Record<string, any>;
  face_restoration: Record<string, any>;
  tiling: boolean;
  hires_fix: Record<string, any>;
  refiner: Record<string, any>;
  
  // Workflow information
  workflow: Record<string, any>;
  workflow_version: string;
  generation_type: string;
  
  // Output information
  output_images: string[];
  
  // Additional metadata
  custom_workflow?: any;
  extras: Record<string, any>;
}

export interface Run {
  id: string;
  timestamp: string;
  config: RunConfig;
}

export interface RunSummary {
  id: string;
  timestamp: string;
  prompt: string;
  model: string;
  generation_type: string;
}

export interface RunsResponse {
  status: string;
  runs: RunSummary[];
}

export interface RunResponse {
  status: string;
  run: Run;
}

export interface SaveRunResponse {
  status: string;
  run_id: string;
}
