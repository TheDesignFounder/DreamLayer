// Zustand store for Pika frame generation state management
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  PikaFrameSettings, 
  PikaFrameResult, 
  defaultPikaFrameSettings,
  PikaResolution,
  PikaDuration 
} from '@/types/pika';

interface PikaFrameState {
  // Current settings
  settings: PikaFrameSettings;
  
  // Generation state
  isGenerating: boolean;
  progress: number;
  
  // Generated frames history
  frames: PikaFrameResult[];
  
  // Error state
  error: string | null;
  
  // Actions
  updateSettings: (updates: Partial<PikaFrameSettings>) => void;
  setPrompt: (prompt: string) => void;
  setNegativePrompt: (negativePrompt: string) => void;
  setSeed: (seed: number) => void;
  setResolution: (resolution: PikaResolution) => void;
  setAspectRatio: (aspectRatio: number) => void;
  setMotionStrength: (motionStrength: number) => void;
  
  // Generation actions
  setGenerating: (generating: boolean) => void;
  setProgress: (progress: number) => void;
  setError: (error: string | null) => void;
  
  // Frame management
  addFrame: (frame: PikaFrameResult) => void;
  removeFrame: (frameId: string) => void;
  clearFrames: () => void;
  
  // Utility actions
  generateRandomSeed: () => void;
  resetSettings: () => void;
}

export const usePikaStore = create<PikaFrameState>()(
  persist(
    (set, get) => ({
      // Initial state
      settings: { ...defaultPikaFrameSettings },
      isGenerating: false,
      progress: 0,
      frames: [],
      error: null,
      
      // Settings actions
      updateSettings: (updates) => set((state) => ({
        settings: { ...state.settings, ...updates }
      })),
      
      setPrompt: (prompt) => set((state) => ({
        settings: { ...state.settings, prompt_text: prompt }
      })),
      
      setNegativePrompt: (negativePrompt) => set((state) => ({
        settings: { ...state.settings, negative_prompt: negativePrompt }
      })),
      
      setSeed: (seed) => set((state) => ({
        settings: { ...state.settings, seed }
      })),
      
      setResolution: (resolution) => set((state) => ({
        settings: { ...state.settings, resolution }
      })),
      
      setAspectRatio: (aspectRatio) => set((state) => ({
        settings: { ...state.settings, aspect_ratio: aspectRatio }
      })),
      
      setMotionStrength: (motionStrength) => set((state) => ({
        settings: { ...state.settings, motion_strength: motionStrength }
      })),
      
      // Generation state actions
      setGenerating: (generating) => set({ isGenerating: generating }),
      
      setProgress: (progress) => set({ progress }),
      
      setError: (error) => set({ error }),
      
      // Frame management actions
      addFrame: (frame) => set((state) => ({
        frames: [frame, ...state.frames]
      })),
      
      removeFrame: (frameId) => set((state) => ({
        frames: state.frames.filter(frame => frame.id !== frameId)
      })),
      
      clearFrames: () => set({ frames: [] }),
      
      // Utility actions
      generateRandomSeed: () => set((state) => ({
        settings: { 
          ...state.settings, 
          seed: Math.floor(Math.random() * 1000000) 
        }
      })),
      
      resetSettings: () => set({
        settings: { ...defaultPikaFrameSettings }
      }),
    }),
    {
      name: 'pika-store', // localStorage key
      version: 1,
      // Only persist settings and frames, not generation state
      partialize: (state) => ({
        settings: state.settings,
        frames: state.frames.slice(0, 50), // Keep last 50 frames
      }),
    }
  )
);

// Selector hooks for performance optimization
export const usePikaSettings = () => usePikaStore((state) => state.settings);
export const usePikaGenerationState = () => usePikaStore((state) => ({
  isGenerating: state.isGenerating,
  progress: state.progress,
  error: state.error,
}));
export const usePikaFrames = () => usePikaStore((state) => state.frames);

// Action hooks
export const usePikaActions = () => usePikaStore((state) => ({
  updateSettings: state.updateSettings,
  setPrompt: state.setPrompt,
  setNegativePrompt: state.setNegativePrompt,
  setSeed: state.setSeed,
  setResolution: state.setResolution,
  setAspectRatio: state.setAspectRatio,
  setMotionStrength: state.setMotionStrength,
  setGenerating: state.setGenerating,
  setProgress: state.setProgress,
  setError: state.setError,
  addFrame: state.addFrame,
  removeFrame: state.removeFrame,
  clearFrames: state.clearFrames,
  generateRandomSeed: state.generateRandomSeed,
  resetSettings: state.resetSettings,
}));