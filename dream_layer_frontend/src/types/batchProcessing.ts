export interface BatchJob {
  id: string;
  name: string;
  type: 'txt2img' | 'img2img';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  settings: Record<string, any>;
  inputImage?: string; // For img2img jobs
  results: string[]; // Array of generated image URLs
  error?: string;
  totalImages: number;
  completedImages: number;
}

export interface BatchQueueItem {
  job: BatchJob;
  promptVariations?: string[];
  settingsVariations?: Record<string, any>[];
}

export interface BatchProcessingStats {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  totalImages: number;
  processingTime: number;
  queueSize: number;
}