export interface RunConfig {
  // Model settings
  model: string;
  vae?: string;
  loras?: Array<{
    name: string;
    strength: number;
  }>;
  controlnets?: Array<{
    name: string;
    strength: number;
  }>;
  
  // Prompt settings
  prompt: string;
  negative_prompt: string;
  
  // Generation settings
  seed: number;
  sampler: string;
  steps: number;
  cfg_scale: number;
  
  // Workflow and version
  workflow: any;
  version: string;
  
  // Additional settings
  width: number;
  height: number;
  batch_size: number;
  batch_count: number;
}

export interface Run {
  id: string;
  timestamp: number;
  config: RunConfig;
  images?: Array<{
    filename: string;
    url: string;
  }>;
  status: 'completed' | 'failed' | 'running';
}

export interface RunRegistryState {
  runs: Run[];
  selectedRun: Run | null;
  isLoading: boolean;
  error: string | null;
} 