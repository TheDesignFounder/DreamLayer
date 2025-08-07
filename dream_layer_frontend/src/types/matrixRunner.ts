import { Txt2ImgCoreSettings } from './generationSettings';

// Parameter range types for matrix generation
export interface ParameterRange {
  type: 'list' | 'range';
  values: (string | number)[];
  original: string; // Store the original input string
}

export interface MatrixParameters {
  seeds?: ParameterRange;
  samplers?: ParameterRange;
  steps?: ParameterRange;
  cfg_scale?: ParameterRange;
  width?: ParameterRange;
  height?: ParameterRange;
  batch_size?: ParameterRange;
  batch_count?: ParameterRange;
}

// Job definition for matrix generation
export interface MatrixJob {
  id: string; // Deterministic hash of parameters
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  parameters: Txt2ImgCoreSettings;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  error?: string;
  result?: {
    images: Array<{
      id: string;
      url: string;
      prompt: string;
      negativePrompt: string;
      timestamp: number;
      settings: Partial<Txt2ImgCoreSettings>;
    }>;
  };
}

// Matrix runner state
export interface MatrixRunnerState {
  // Current matrix configuration
  parameters: MatrixParameters;
  baseSettings: Txt2ImgCoreSettings;
  
  // Job management
  jobs: MatrixJob[];
  currentJobIndex: number;
  isRunning: boolean;
  isPaused: boolean;
  
  // Statistics
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  pendingJobs: number;
  
  // Progress tracking
  startTime?: number;
  estimatedTimeRemaining?: number;
  averageTimePerJob?: number;
  
  // UI state
  showProgressGrid: boolean;
  autoBatch: boolean;
}

// Matrix runner actions
export interface MatrixRunnerActions {
  // Parameter management
  setParameter: (param: keyof MatrixParameters, range: ParameterRange) => void;
  setBaseSettings: (settings: Partial<Txt2ImgCoreSettings>) => void;
  
  // Job management
  generateJobs: () => void;
  startMatrix: () => void;
  pauseMatrix: () => void;
  resumeMatrix: () => void;
  stopMatrix: () => void;
  clearJobs: () => void;
  
  // Job execution
  executeNextJob: () => Promise<void>;
  updateJobStatus: (jobId: string, status: MatrixJob['status'], result?: MatrixJob['result'], error?: string, duration?: number) => void;
  
  // UI actions
  toggleProgressGrid: () => void;
  toggleAutoBatch: () => void;
  
  // Persistence
  saveToIndexedDB: () => Promise<void>;
  loadFromIndexedDB: () => Promise<void>;
}

export type MatrixRunnerStore = MatrixRunnerState & MatrixRunnerActions;

// Utility types for parameter parsing
export interface ParsedParameter {
  type: 'list' | 'range';
  values: (string | number)[];
  original: string;
}

// Matrix generation result
export interface MatrixGenerationResult {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  duration: number;
  averageTimePerJob: number;
  jobs: MatrixJob[];
} 