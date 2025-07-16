import { useCallback, useEffect, useRef } from 'react';
import useHistoryReducer, { UseHistoryReducerReturn } from './useHistoryReducer';
import { Txt2ImgCoreSettings } from '@/types/generationSettings';

interface UseGenerationHistoryReturn extends UseHistoryReducerReturn<Txt2ImgCoreSettings> {
  updatePrompt: (prompt: string) => void;
  updateNegativePrompt: (negativePrompt: string) => void;
  updateSampler: (sampler: string) => void;
  updateSteps: (steps: number) => void;
  updateCfgScale: (cfgScale: number) => void;
  updateWidth: (width: number) => void;
  updateHeight: (height: number) => void;
  updateSeed: (seed: number) => void;
  updateModel: (model: string) => void;
  updateBatchSize: (batchSize: number) => void;
  updateBatchCount: (batchCount: number) => void;
  updateScheduler: (scheduler: string) => void;
  updateRandomSeed: (randomSeed: boolean) => void;
  updateSettings: (updates: Partial<Txt2ImgCoreSettings>) => void;
  resetToDefault: (defaultSettings: Txt2ImgCoreSettings) => void;
}

export function useGenerationHistory(
  initialSettings: Txt2ImgCoreSettings,
  enableKeyboardShortcuts: boolean = true
): UseGenerationHistoryReturn {
  const history = useHistoryReducer<Txt2ImgCoreSettings>(
    initialSettings,
    enableKeyboardShortcuts
  );

  // Debounce rapid changes to prevent excessive history entries
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingUpdatesRef = useRef<Partial<Txt2ImgCoreSettings>>({});

  const debouncedSetState = useCallback(
    (updates: Partial<Txt2ImgCoreSettings>) => {
      // Clear any pending timeout
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }

      // Merge with pending updates
      pendingUpdatesRef.current = {
        ...pendingUpdatesRef.current,
        ...updates
      };

      // Set a new timeout
      debounceTimeoutRef.current = setTimeout(() => {
        const mergedUpdates = { ...pendingUpdatesRef.current };
        pendingUpdatesRef.current = {};
        
        const newState = {
          ...history.state,
          ...mergedUpdates
        };
        
        history.setState(newState);
      }, 150); // 150ms debounce
    },
    [history]
  );

  const updatePrompt = useCallback((prompt: string) => {
    debouncedSetState({ prompt });
  }, [debouncedSetState]);

  const updateNegativePrompt = useCallback((negative_prompt: string) => {
    debouncedSetState({ negative_prompt });
  }, [debouncedSetState]);

  const updateSampler = useCallback((sampler_name: string) => {
    debouncedSetState({ sampler_name });
  }, [debouncedSetState]);

  const updateSteps = useCallback((steps: number) => {
    debouncedSetState({ steps });
  }, [debouncedSetState]);

  const updateCfgScale = useCallback((cfg_scale: number) => {
    debouncedSetState({ cfg_scale });
  }, [debouncedSetState]);

  const updateWidth = useCallback((width: number) => {
    debouncedSetState({ width });
  }, [debouncedSetState]);

  const updateHeight = useCallback((height: number) => {
    debouncedSetState({ height });
  }, [debouncedSetState]);

  const updateSeed = useCallback((seed: number) => {
    debouncedSetState({ seed });
  }, [debouncedSetState]);

  const updateModel = useCallback((model_name: string) => {
    debouncedSetState({ model_name });
  }, [debouncedSetState]);

  const updateBatchSize = useCallback((batch_size: number) => {
    debouncedSetState({ batch_size });
  }, [debouncedSetState]);

  const updateBatchCount = useCallback((batch_count: number) => {
    debouncedSetState({ batch_count });
  }, [debouncedSetState]);

  const updateScheduler = useCallback((scheduler: string) => {
    debouncedSetState({ scheduler });
  }, [debouncedSetState]);

  const updateRandomSeed = useCallback((random_seed: boolean) => {
    debouncedSetState({ random_seed });
  }, [debouncedSetState]);

  const updateSettings = useCallback((updates: Partial<Txt2ImgCoreSettings>) => {
    debouncedSetState(updates);
  }, [debouncedSetState]);

  const resetToDefault = useCallback((defaultSettings: Txt2ImgCoreSettings) => {
    // Clear any pending debounced updates
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }
    pendingUpdatesRef.current = {};
    
    history.setState(defaultSettings);
  }, [history]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  return {
    ...history,
    updatePrompt,
    updateNegativePrompt,
    updateSampler,
    updateSteps,
    updateCfgScale,
    updateWidth,
    updateHeight,
    updateSeed,
    updateModel,
    updateBatchSize,
    updateBatchCount,
    updateScheduler,
    updateRandomSeed,
    updateSettings,
    resetToDefault
  };
}

export default useGenerationHistory;
