import { useCallback, useEffect, useRef } from 'react';
import useHistoryReducer, { UseHistoryReducerReturn } from './useHistoryReducer';
import { CoreGenerationSettings } from '@/types/generationSettings';

interface UseImg2ImgHistoryReturn extends UseHistoryReducerReturn<CoreGenerationSettings> {
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
  updateDenoisingStrength: (strength: number) => void;
  updateInputImage: (inputImage: string) => void;
  updateSettings: (updates: Partial<CoreGenerationSettings>) => void;
  resetToDefault: (defaultSettings: CoreGenerationSettings) => void;
}

export function useImg2ImgHistory(
  initialSettings: CoreGenerationSettings,
  enableKeyboardShortcuts: boolean = true
): UseImg2ImgHistoryReturn {
  const history = useHistoryReducer<CoreGenerationSettings>(
    initialSettings,
    enableKeyboardShortcuts
  );

  // Debounce rapid changes to prevent excessive history entries
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pendingUpdatesRef = useRef<Partial<CoreGenerationSettings>>({});

  const debouncedSetState = useCallback(
    (updates: Partial<CoreGenerationSettings>) => {
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

  const updateDenoisingStrength = useCallback((denoising_strength: number) => {
    debouncedSetState({ denoising_strength });
  }, [debouncedSetState]);

  const updateInputImage = useCallback((input_image: string) => {
    debouncedSetState({ input_image });
  }, [debouncedSetState]);

  const updateSettings = useCallback((updates: Partial<CoreGenerationSettings>) => {
    debouncedSetState(updates);
  }, [debouncedSetState]);

  const resetToDefault = useCallback((defaultSettings: CoreGenerationSettings) => {
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
    updateDenoisingStrength,
    updateInputImage,
    updateSettings,
    resetToDefault
  };
}

export default useImg2ImgHistory;
