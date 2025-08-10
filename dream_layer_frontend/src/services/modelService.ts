export interface CheckpointModel {
  id: string;
  name: string;
  filename: string;
}

export const fetchAvailableModels = async (): Promise<CheckpointModel[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`);
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
    const response = await fetch(`${API_BASE_URL}/api/fetch-prompt?type=${type}`);
    
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
    try {
        const response = await fetch(`${API_BASE_URL}/api/upscaler-models`);
        if (!response.ok) {
            throw new Error('Failed to fetch upscaler models');
        }
        const data = await response.json();
        return data.models || [];
    } catch (error) {
        console.error('Error fetching upscaler models:', error);
        throw error;
    }
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

export const fetchLoraModels = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/lora-models`);
        if (!response.ok) {
            throw new Error('Failed to fetch LoRA models');
        }
        const data = await response.json();
        return data.models || [];
    } catch (error) {
        console.error('Error fetching LoRA models:', error);
        throw error;
    }
};

export const fetchControlNetModels = async () => {
    try {
        const response = await fetch(`${CONTROLNET_API_BASE_URL}/api/controlnet/models`);
        if (!response.ok) {
            throw new Error('Failed to fetch ControlNet models');
        }
        const data = await response.json();
        return data.models || [];
    } catch (error) {
        console.error('Error fetching ControlNet models:', error);
        throw error;
    }
};

export interface ModelInfo {
    id: string;
    name: string;
    filename: string;
    type: string;
    path?: string;
}

export const fetchAllModelTypes = async (): Promise<ModelInfo[]> => {
    try {
        const [checkpoints, loras, controlnets, upscalers] = await Promise.allSettled([
            fetchAvailableModels(),
            fetchLoraModels(),
            fetchControlNetModels(),
            fetchUpscalerModels()
        ]);

        const allModels: ModelInfo[] = [];

        if (checkpoints.status === 'fulfilled') {
            checkpoints.value.forEach((model: CheckpointModel) => {
                allModels.push({
                    ...model,
                    type: 'checkpoints',
                    path: `/models/checkpoints/${model.filename}`
                });
            });
        }

        if (loras.status === 'fulfilled') {
            loras.value.forEach((model: any) => {
                allModels.push({
                    id: model.id || model.filename,
                    name: model.name || model.filename.replace(/\.[^/.]+$/, ""),
                    filename: model.filename,
                    type: 'loras',
                    path: `/models/loras/${model.filename}`
                });
            });
        }

        if (controlnets.status === 'fulfilled') {
            controlnets.value.forEach((model: any) => {
                const filename = typeof model === 'string' ? model : model.filename;
                allModels.push({
                    id: filename,
                    name: filename.replace(/\.[^/.]+$/, ""),
                    filename: filename,
                    type: 'controlnet',
                    path: `/models/controlnet/${filename}`
                });
            });
        }

        if (upscalers.status === 'fulfilled') {
            upscalers.value.forEach((model: any) => {
                allModels.push({
                    id: model.id || model.filename,
                    name: model.name || model.filename.replace(/\.[^/.]+$/, ""),
                    filename: model.filename,
                    type: 'upscale_models',
                    path: `/models/upscale_models/${model.filename}`
                });
            });
        }

        return allModels;
    } catch (error) {
        console.error('Error fetching all model types:', error);
        throw error;
    }
};

export interface ModelRefreshEvent {
    model_type: string;
    filename: string;
    action: 'added' | 'removed';
    timestamp: number;
}

export interface WebSocketMessage {
    type: string;
    data: ModelRefreshEvent;
}

let wsConnection: WebSocket | null = null;
let wsReconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 2000;
const WS_URL = import.meta.env.VITE_COMFY_UI_WS_API_URL || 'ws://localhost:8188/ws';
const API_BASE_URL = import.meta.env.VITE_BACKEND_API_BASE_URL || 'http://localhost:5002';
const CONTROLNET_API_BASE_URL = import.meta.env.VITE_TXT_TO_IMG_API_BASE_URL || 'http://localhost:5001';

const generateClientId = (): string => {
    return 'dreamlayer_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
};

interface ModelRefreshListener {
    callback: () => void;
    modelType?: string;
}

const modelRefreshListeners: Set<ModelRefreshListener> = new Set();

export const addModelRefreshListener = (
    callback: () => void,
    modelType?: string
): (() => void) => {
    const listener: ModelRefreshListener = { callback, modelType };
    modelRefreshListeners.add(listener);

    return () => {
        modelRefreshListeners.delete(listener);
    };
};

const notifyModelRefreshListeners = (event?: ModelRefreshEvent) => {
    modelRefreshListeners.forEach(listener => {
        try {
            if (listener.modelType && event?.model_type && listener.modelType !== event.model_type) {
                return;
            }

            listener.callback();
        } catch (error) {
            console.error('Error in model refresh listener:', error);
        }
    });
};

const connectWebSocket = (): Promise<WebSocket> => {
    return new Promise((resolve, reject) => {
        try {
            const clientId = generateClientId();
            const wsUrl = `${WS_URL}?clientId=${clientId}`;

            console.log(`🔌 Connecting to ComfyUI WebSocket: ${wsUrl}`);

            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('✅ WebSocket connected to ComfyUI');
                wsReconnectAttempts = 0;
                resolve(ws);
            };

            const service = this;

            ws.onmessage = (event) => {
                if (event.data instanceof Blob) {
                    return;
                }
                try {
                    const data = JSON.parse(event.data);
                    service.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error, 'Data:', event.data);
                }
            };

            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                reject(error);
            };

            ws.onclose = (event) => {
                console.log('🔌 WebSocket connection closed:', event.code, event.reason);
                wsConnection = null;

                if (event.code !== 1000 && wsReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    wsReconnectAttempts++;
                    console.log(`🔄 Attempting to reconnect WebSocket (${wsReconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);

                    setTimeout(() => {
                        setupModelRefreshWebSocket().catch(error => {
                            console.error('Failed to reconnect WebSocket:', error);
                        });
                    }, RECONNECT_DELAY * wsReconnectAttempts);
                }
            };

        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            reject(error);
        }
    });
};

export const setupModelRefreshWebSocket = async (): Promise<void> => {
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
        console.log('WebSocket already connected');
        return;
    }

    try {
        wsConnection = await connectWebSocket();
    } catch (error) {
        console.error('Failed to setup WebSocket connection:', error);
        throw error;
    }
};

export const closeModelRefreshWebSocket = (): void => {
    if (wsConnection) {
        console.log('🔌 Closing WebSocket connection');
        wsConnection.close(1000, 'Client disconnecting');
        wsConnection = null;
    }

    modelRefreshListeners.clear();
};

let webSocketConnectionPromise: Promise<void> | null = null;

export const ensureWebSocketConnection = (): Promise<void> => {
    if (!webSocketConnectionPromise) {
        webSocketConnectionPromise = setupModelRefreshWebSocket().catch(error => {
            console.warn('Failed to setup WebSocket connection:', error);
            webSocketConnectionPromise = null;
            throw error;
        });
    }

    return webSocketConnectionPromise;
};