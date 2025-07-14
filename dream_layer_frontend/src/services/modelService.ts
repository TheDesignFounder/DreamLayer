// src/services/modelService.ts

export interface CheckpointModel {
  id: string;
  name: string;
  filename: string;
}

export interface RandomPromptResponse {
  status: string;
  message: string;
  type: string;
  prompt: string;
}

const API_URL = import.meta.env.VITE_API_URL;

// ✅ Fetch available models
export const fetchAvailableModels = async (): Promise<CheckpointModel[]> => {
  try {
    const response = await fetch(`${API_URL}/api/models`);
    if (!response.ok) throw new Error('Failed to fetch models');

    const data = await response.json();
    if (data.status === 'success' && Array.isArray(data.models)) {
      return data.models;
    } else {
      throw new Error('Invalid response format');
    }
  } catch (error) {
    console.error('❌ Error fetching models:', error);
    throw error;
  }
};

// ✅ Fetch random prompt (positive or negative)
export const fetchRandomPrompt = async (type: 'positive' | 'negative'): Promise<string> => {
  try {
    console.log(`🔄 Calling fetch-prompt API with type: ${type}`);
    const response = await fetch(`${API_URL}/api/fetch-prompt?type=${type}`);
    if (!response.ok) throw new Error(`Failed to fetch ${type} prompt`);

    const data: RandomPromptResponse = await response.json();
    console.log(`✅ Got prompt:`, data);

    if (data.status === 'success') {
      return data.prompt;
    } else {
      throw new Error(data.message || 'Unknown error');
    }
  } catch (error) {
    console.error(`❌ Error fetching ${type} prompt:`, error);
    throw error;
  }
};

// ✅ Fetch upscaler models
export const fetchUpscalerModels = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_URL}/api/upscaler-models`);
    if (!response.ok) throw new Error('Failed to fetch upscaler models');

    const data = await response.json();
    return data.models || [];
  } catch (error) {
    console.error('❌ Error fetching upscaler models:', error);
    return [];
  }
};
