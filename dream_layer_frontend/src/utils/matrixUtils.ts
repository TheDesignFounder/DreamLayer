import { ParameterRange, ParsedParameter, MatrixJob, MatrixParameters } from '@/types/matrixRunner';
import { Txt2ImgCoreSettings } from '@/types/generationSettings';

// Parse parameter input string into structured format
export function parseParameter(input: string): ParsedParameter {
  const trimmed = input.trim();
  
  // Check if it's a range (e.g., "1-5")
  const rangeMatch = trimmed.match(/^(\d+)-(\d+)$/);
  if (rangeMatch) {
    const start = parseInt(rangeMatch[1]);
    const end = parseInt(rangeMatch[2]);
    const values = [];
    for (let i = start; i <= end; i++) {
      values.push(i);
    }
    return {
      type: 'range',
      values,
      original: trimmed
    };
  }
  
  // Check if it's a comma-separated list
  if (trimmed.includes(',')) {
    const values = trimmed.split(',').map(item => {
      const trimmedItem = item.trim();
      // Try to parse as number first
      const num = parseFloat(trimmedItem);
      return isNaN(num) ? trimmedItem : num;
    });
    return {
      type: 'list',
      values,
      original: trimmed
    };
  }
  
  // Single value
  const num = parseFloat(trimmed);
  const value = isNaN(num) ? trimmed : num;
  return {
    type: 'list',
    values: [value],
    original: trimmed
  };
}

// Generate deterministic job ID from parameters
export function generateJobId(parameters: Txt2ImgCoreSettings): string {
  // Create a deterministic string representation
  const paramString = JSON.stringify({
    seed: parameters.seed,
    sampler_name: parameters.sampler_name,
    steps: parameters.steps,
    cfg_scale: parameters.cfg_scale,
    width: parameters.width,
    height: parameters.height,
    batch_size: parameters.batch_size,
    batch_count: parameters.batch_count,
    prompt: parameters.prompt,
    negative_prompt: parameters.negative_prompt,
    model_name: parameters.model_name
  });
  
  // Simple hash function for deterministic ID
  let hash = 0;
  for (let i = 0; i < paramString.length; i++) {
    const char = paramString.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  return `job_${Math.abs(hash).toString(36)}`;
}

// Generate all job combinations from matrix parameters
export function generateJobs(
  parameters: MatrixParameters,
  baseSettings: Txt2ImgCoreSettings
): MatrixJob[] {
  const jobs: MatrixJob[] = [];
  
  // Get all parameter values
  const seeds = parameters.seeds?.values || [baseSettings.seed];
  const samplers = parameters.samplers?.values || [baseSettings.sampler_name];
  const steps = parameters.steps?.values || [baseSettings.steps];
  const cfgScales = parameters.cfg_scale?.values || [baseSettings.cfg_scale];
  const widths = parameters.width?.values || [baseSettings.width];
  const heights = parameters.height?.values || [baseSettings.height];
  const batchSizes = parameters.batch_size?.values || [baseSettings.batch_size];
  const batchCounts = parameters.batch_count?.values || [baseSettings.batch_count];
  
  // Generate all combinations
  for (const seed of seeds) {
    for (const sampler of samplers) {
      for (const step of steps) {
        for (const cfg of cfgScales) {
          for (const width of widths) {
            for (const height of heights) {
              for (const batchSize of batchSizes) {
                for (const batchCount of batchCounts) {
                  const jobParameters: Txt2ImgCoreSettings = {
                    ...baseSettings,
                    seed: Number(seed),
                    sampler_name: String(sampler),
                    steps: Number(step),
                    cfg_scale: Number(cfg),
                    width: Number(width),
                    height: Number(height),
                    batch_size: Number(batchSize),
                    batch_count: Number(batchCount),
                    random_seed: false // Disable random seed for matrix generation
                  };
                  
                  const job: MatrixJob = {
                    id: generateJobId(jobParameters),
                    status: 'pending',
                    parameters: jobParameters,
                    createdAt: Date.now()
                  };
                  
                  jobs.push(job);
                }
              }
            }
          }
        }
      }
    }
  }
  
  return jobs;
}

// Calculate estimated time remaining
export function calculateETA(
  completedJobs: number,
  totalJobs: number,
  averageTimePerJob: number,
  startTime?: number
): number | undefined {
  if (!startTime || completedJobs === 0 || averageTimePerJob === 0) {
    return undefined;
  }
  
  const remainingJobs = totalJobs - completedJobs;
  return remainingJobs * averageTimePerJob;
}

// Update average time per job
export function updateAverageTimePerJob(
  currentAverage: number,
  newJobTime: number,
  totalCompletedJobs: number
): number {
  if (totalCompletedJobs === 1) {
    return newJobTime;
  }
  
  // Weighted average
  return (currentAverage * (totalCompletedJobs - 1) + newJobTime) / totalCompletedJobs;
}

// Group jobs by similar parameters for batching
export function groupJobsForBatching(jobs: MatrixJob[]): MatrixJob[][] {
  const groups: Map<string, MatrixJob[]> = new Map();
  
  for (const job of jobs) {
    // Create a key based on parameters that affect GPU context
    const batchKey = JSON.stringify({
      model_name: job.parameters.model_name,
      width: job.parameters.width,
      height: job.parameters.height,
      vae_name: job.parameters.vae_name,
      lora: job.parameters.lora
    });
    
    if (!groups.has(batchKey)) {
      groups.set(batchKey, []);
    }
    groups.get(batchKey)!.push(job);
  }
  
  return Array.from(groups.values());
}

// Validate parameter ranges
export function validateParameterRange(
  param: keyof MatrixParameters,
  range: ParameterRange
): { isValid: boolean; error?: string } {
  const { type, values } = range;
  
  if (values.length === 0) {
    return { isValid: false, error: 'Parameter range cannot be empty' };
  }
  
  switch (param) {
    case 'seeds':
      if (type === 'range') {
        for (const value of values) {
          if (typeof value !== 'number' || value < -1 || value > 2147483647) {
            return { isValid: false, error: 'Seeds must be numbers between -1 and 2147483647' };
          }
        }
      }
      break;
      
    case 'steps':
      if (type === 'range') {
        for (const value of values) {
          if (typeof value !== 'number' || value < 1 || value > 150) {
            return { isValid: false, error: 'Steps must be numbers between 1 and 150' };
          }
        }
      }
      break;
      
    case 'cfg_scale':
      if (type === 'range') {
        for (const value of values) {
          if (typeof value !== 'number' || value < 1 || value > 20) {
            return { isValid: false, error: 'CFG Scale must be numbers between 1 and 20' };
          }
        }
      }
      break;
      
    case 'width':
    case 'height':
      if (type === 'range') {
        for (const value of values) {
          if (typeof value !== 'number' || value < 64 || value > 2048) {
            return { isValid: false, error: `${param} must be numbers between 64 and 2048` };
          }
        }
      }
      break;
      
    case 'batch_size':
    case 'batch_count':
      if (type === 'range') {
        for (const value of values) {
          if (typeof value !== 'number' || value < 1 || value > 100) {
            return { isValid: false, error: `${param} must be numbers between 1 and 100` };
          }
        }
      }
      break;
  }
  
  return { isValid: true };
}

// Format time duration for display
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
}

// Calculate total job count from parameters
export function calculateTotalJobs(parameters: MatrixParameters): number {
  const seeds = parameters.seeds?.values.length || 1;
  const samplers = parameters.samplers?.values.length || 1;
  const steps = parameters.steps?.values.length || 1;
  const cfgScales = parameters.cfg_scale?.values.length || 1;
  const widths = parameters.width?.values.length || 1;
  const heights = parameters.height?.values.length || 1;
  const batchSizes = parameters.batch_size?.values.length || 1;
  const batchCounts = parameters.batch_count?.values.length || 1;
  
  return seeds * samplers * steps * cfgScales * widths * heights * batchSizes * batchCounts;
} 