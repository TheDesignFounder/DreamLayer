import { create } from 'zustand';
import { ImageResult, CoreGenerationSettings, defaultCoreSettings } from '@/types/generationSettings';

interface InputImage {
  url: string;
  file: File;
}

interface Img2ImgGalleryState {
  images: ImageResult[];
  isLoading: boolean;
  inputImage: InputImage | null;
  maskFile: File | null; // NEW: mask file
  maskPreview: string | null; // NEW: mask preview
  coreSettings: CoreGenerationSettings;
  customWorkflow: any | null;
  addImages: (newImages: ImageResult[]) => void;
  clearImages: () => void;
  removeImage: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setInputImage: (image: InputImage | null) => void;
  setMaskFile: (file: File | null) => void; // NEW: set mask file
  setMaskPreview: (url: string | null) => void; // NEW: set mask preview
  setCustomWorkflow: (workflow: any | null) => void;
  updateCoreSettings: (updates: Partial<CoreGenerationSettings>) => void;
  handlePromptChange: (value: string, isNegative?: boolean) => void;
  handleSamplingSettingsChange: (sampler: string, scheduler: string, steps: number, cfg: number) => void;
  handleSizeSettingsChange: (width: number, height: number) => void;
  handleBatchSettingsChange: (batchCount: number, batchSize: number) => void;
  handleSeedChange: (seed: number, random?: boolean) => void;
  handleDenoisingStrengthChange: (strength: number) => void;
  handleAdvancedSettingsChange: (settings: Partial<CoreGenerationSettings>) => void;
}

export const useImg2ImgGalleryStore = create<Img2ImgGalleryState>((set) => ({
  images: [],
  isLoading: false,
  inputImage: null,
  maskFile: null, // NEW: mask file
  maskPreview: null, // NEW: mask preview
  coreSettings: defaultCoreSettings,
  customWorkflow: null,
  addImages: (newImages) => set((state) => ({
    images: [...newImages, ...state.images]
  })),
  clearImages: () => set((state) => ({
    images: [],
    isLoading: state.isLoading // Preserve the current loading state
  })),
  removeImage: (id) => set((state) => ({
    images: state.images.filter(img => img.id !== id)
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setInputImage: (image) => set((state) => {
    if (image) {
      // When setting a new input image, also update the input_image field in coreSettings
      const reader = new FileReader();
      reader.onload = () => {
        set((state) => ({
          coreSettings: {
            ...state.coreSettings,
            input_image: reader.result as string
          }
        }));
      };
      reader.readAsDataURL(image.file);
    }
    return { inputImage: image };
  }),
  setMaskFile: (file) => set({ maskFile: file }), // NEW: set mask file
  setMaskPreview: (url) => set({ maskPreview: url }), // NEW: set mask preview
  setCustomWorkflow: (workflow) => set({ customWorkflow: workflow }),
  updateCoreSettings: (updates) => set((state) => ({
    coreSettings: { ...state.coreSettings, ...updates }
  })),
  handlePromptChange: (value, isNegative = false) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      [isNegative ? 'negative_prompt' : 'prompt']: value
    }
  })),
  handleSamplingSettingsChange: (sampler, scheduler, steps, cfg) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      sampler_name: sampler,
      scheduler: scheduler,
      steps: steps,
      cfg_scale: cfg
    }
  })),
  handleSizeSettingsChange: (width, height) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      width,
      height
    }
  })),
  handleBatchSettingsChange: (batchCount, batchSize) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      batch_count: batchCount,
      batch_size: batchSize
    }
  })),
  handleSeedChange: (seed, random = true) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      seed,
      random_seed: random
    }
  })),
  handleDenoisingStrengthChange: (strength) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      denoising_strength: Math.max(0, Math.min(1, strength))
    }
  })),
  handleAdvancedSettingsChange: (settings) => set((state) => ({
    coreSettings: {
      ...state.coreSettings,
      ...settings
    }
  }))
}));
