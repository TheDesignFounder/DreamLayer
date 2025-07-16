export interface CheckpointModel {
  id: string;
  name: string;
  filename: string;
}

export const fetchAvailableModels = async (): Promise<CheckpointModel[]> => {
  try {
    const response = await fetch('http://localhost:5002/api/models');
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }
    
    const data = await response.json();
    if (data.status === 'success' && Array.isArray(data.models)) {
      return data.models;
    } else {
      throw new Error('Invalid response format');
    }
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
};

export interface RandomPromptResponse {
  status: string;
  message: string;
  type: string;
  prompt: string;
}

export const fetchRandomPrompt = async (type: 'positive' | 'negative'): Promise<string> => {
  try {
    console.log(`🔄 Frontend: Calling fetch-prompt API with type: ${type}`);
    const response = await fetch(`http://localhost:5002/api/fetch-prompt?type=${type}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch ${type} prompt: ${response.statusText}`);
    }
    
    const data: RandomPromptResponse = await response.json();
    console.log(`✅ Frontend: Received response:`, data);
    
    if (data.status === 'success') {
      return data.prompt;
    } else {
      throw new Error(data.message || 'Failed to fetch prompt');
    }
  } catch (error) {
    console.error(`❌ Frontend: Error fetching ${type} prompt:`, error);
    throw error;
  }
};

export const fetchUpscalerModels = async () => {
  const response = await fetch('http://localhost:5002/api/upscaler-models');
  const data = await response.json();
  return data.models;
}; 

export const addAPIBasedModel = async (alias: string, apiKey: string): Promise<boolean> => {
  const response = await fetch('http://localhost:5002/api/add-api-key', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      alias, 
      'api-key': apiKey
    }),
  });

  if (!response.ok) {
    console.error('Failed to add API-based model');
    return false;
  }

  return true;
};
