import { Run } from '@/types/run';

const API_BASE_URL = 'http://localhost:5000/api';

export interface RunService {
  getRuns: () => Promise<Run[]>;
  getRunById: (id: string) => Promise<Run | null>;
  createRun: (config: any) => Promise<Run>;
}

// Mock data for development - in production this would come from the backend
const mockRuns: Run[] = [
  {
    id: 'run_001',
    timestamp: Date.now() - 3600000, // 1 hour ago
    status: 'completed',
    config: {
      model: 'v1-5-pruned-emaonly-fp16.safetensors',
      vae: 'vae-ft-mse-840000-ema-pruned.safetensors',
      loras: [
        { name: 'lora_style_anime', strength: 0.8 }
      ],
      controlnets: [],
      prompt: 'A beautiful anime character in a magical forest',
      negative_prompt: 'blurry, low quality, distorted',
      seed: 123456789,
      sampler: 'euler',
      steps: 20,
      cfg_scale: 7.0,
      workflow: { nodes: {} },
      version: '1.0.0',
      width: 512,
      height: 512,
      batch_size: 1,
      batch_count: 1
    },
    images: [
      {
        filename: 'run_001_001.png',
        url: '/api/images/run_001_001.png'
      }
    ]
  },
  {
    id: 'run_002',
    timestamp: Date.now() - 7200000, // 2 hours ago
    status: 'completed',
    config: {
      model: 'v1-6-pruned-emaonly-fp16.safetensors',
      vae: undefined,
      loras: [],
      controlnets: [
        { name: 'control_v11p_sd15_canny', strength: 1.0 }
      ],
      prompt: 'A futuristic cityscape with neon lights',
      negative_prompt: 'dark, gloomy, broken',
      seed: 987654321,
      sampler: 'dpm++',
      steps: 30,
      cfg_scale: 8.5,
      workflow: { nodes: {} },
      version: '1.0.0',
      width: 768,
      height: 512,
      batch_size: 1,
      batch_count: 1
    },
    images: [
      {
        filename: 'run_002_001.png',
        url: '/api/images/run_002_001.png'
      }
    ]
  },
  {
    id: 'run_003',
    timestamp: Date.now() - 10800000, // 3 hours ago
    status: 'failed',
    config: {
      model: 'v1-5-pruned-emaonly-fp16.safetensors',
      vae: undefined,
      loras: [],
      controlnets: [],
      prompt: '',
      negative_prompt: '',
      seed: 555555555,
      sampler: 'euler',
      steps: 20,
      cfg_scale: 7.0,
      workflow: { nodes: {} },
      version: '1.0.0',
      width: 512,
      height: 512,
      batch_size: 1,
      batch_count: 1
    },
    images: []
  }
];

export const runService: RunService = {
  getRuns: async (): Promise<Run[]> => {
    try {
      // In production, this would be a real API call
      // const response = await fetch(`${API_BASE_URL}/runs`);
      // return await response.json();
      
      // For now, return mock data
      return mockRuns;
    } catch (error) {
      console.error('Error fetching runs:', error);
      throw new Error('Failed to fetch runs');
    }
  },

  getRunById: async (id: string): Promise<Run | null> => {
    try {
      // In production, this would be a real API call
      // const response = await fetch(`${API_BASE_URL}/runs/${id}`);
      // return await response.json();
      
      // For now, return mock data
      const run = mockRuns.find(r => r.id === id);
      return run || null;
    } catch (error) {
      console.error('Error fetching run:', error);
      throw new Error('Failed to fetch run');
    }
  },

  createRun: async (config: any): Promise<Run> => {
    try {
      // In production, this would be a real API call
      // const response = await fetch(`${API_BASE_URL}/runs`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(config)
      // });
      // return await response.json();
      
      // For now, create a mock run
      const newRun: Run = {
        id: `run_${Date.now()}`,
        timestamp: Date.now(),
        status: 'completed',
        config: {
          model: config.model_name || 'v1-5-pruned-emaonly-fp16.safetensors',
          vae: config.vae_name,
          loras: config.lora ? [{ name: config.lora.name, strength: config.lora.strength }] : [],
          controlnets: [],
          prompt: config.prompt || '',
          negative_prompt: config.negative_prompt || '',
          seed: config.seed || Math.floor(Math.random() * 1000000000),
          sampler: config.sampler_name || 'euler',
          steps: config.steps || 20,
          cfg_scale: config.cfg_scale || 7.0,
          workflow: config.workflow || { nodes: {} },
          version: '1.0.0',
          width: config.width || 512,
          height: config.height || 512,
          batch_size: config.batch_size || 1,
          batch_count: config.batch_count || 1
        },
        images: []
      };
      
      return newRun;
    } catch (error) {
      console.error('Error creating run:', error);
      throw new Error('Failed to create run');
    }
  }
}; 