export interface RunConfig {
  run_id: string;
  timestamp: string;
  model: string;
  vae?: string;
  loras: Array<{
    name: string;
    strength: number;
    [key: string]: any;
  }>;
  controlnets: Array<{
    model: string;
    strength: number;
    enabled: boolean;
    [key: string]: any;
  }>;
  prompt: string;
  negative_prompt: string;
  seed: number;
  sampler: string;
  steps: number;
  cfg_scale: number;
  width: number;
  height: number;
  batch_size: number;
  batch_count: number;
  workflow: Record<string, any>;
  version: string;
  generated_images: string[];
  generation_type: 'txt2img' | 'img2img';
  // Enhanced with metrics from database integration
  clip_score_mean?: number;
  fid_score?: number;
  // Composition correctness metrics
  macro_precision?: number;
  macro_recall?: number;
  macro_f1?: number;
}

export interface RunRegistryResponse {
  status: 'success' | 'error';
  runs?: RunConfig[];
  run?: RunConfig;
  message?: string;
}

export interface RunRegistryState {
  runs: RunConfig[];
  loading: boolean;
  error: string | null;
  selectedRun: RunConfig | null;
}

export interface RunRegistryActions {
  fetchRuns: () => Promise<void>;
  fetchRun: (runId: string) => Promise<void>;
  deleteRun: (runId: string) => Promise<void>;
  clearError: () => void;
  setSelectedRun: (run: RunConfig | null) => void;
}
