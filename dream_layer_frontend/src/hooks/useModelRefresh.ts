import { useEffect } from 'react';
import { addModelRefreshListener, ensureWebSocketConnection } from '@/services/modelService';

/**
 * Custom hook for automatic model refresh via WebSocket events
 * 
 * @param fetchFunction - Function to call when models need to be refreshed
 * @param modelType - Optional model type filter (e.g., 'loras', 'controlnet')
 * @param enabled - Whether the hook should be active (default: true)
 */
export const useModelRefresh = (
  fetchFunction: () => Promise<void> | void,
  modelType?: string,
  enabled: boolean = true
) => {
  useEffect(() => {
    if (!enabled) return;

    // Initial load
    fetchFunction();

    // Setup WebSocket connection
    ensureWebSocketConnection();

    // Subscribe to model refresh events with optional model type filtering
    return addModelRefreshListener(() => {
      const logPrefix = modelType ? `📡 ${modelType}` : '📡 Models';
      console.log(`${logPrefix}: Received WebSocket refresh event, reloading...`);
      fetchFunction();
    }, modelType);
  }, [fetchFunction, modelType, enabled]);
};

export default useModelRefresh;
