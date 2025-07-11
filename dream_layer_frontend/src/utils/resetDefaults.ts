// Reset defaults for different slider groups
// These values define what each slider group should reset to

export interface SliderGroupDefaults {
  // Core Generation Settings
  coreGeneration: {
    cfg_scale: number;
    steps: number;
    width: number;
    height: number;
    batch_size: number;
    batch_count: number;
  };
  
  // Advanced Settings
  advancedSettings: {
    codeformer_weight: number;
    gfpgan_weight: number;
    tile_size: number;
    tile_overlap: number;
    refiner_switch_at: number;
  };
  
  // Size settings
  sizingSettings: {
    width: number;
    height: number;
  };
  
  // Sampling settings
  samplingSettings: {
    cfg_scale: number;
    steps: number;
  };
}

// Default values for reset functionality
// Note: CFG reset target is 10 as specified in the challenge requirements
export const sliderGroupDefaults: SliderGroupDefaults = {
  coreGeneration: {
    cfg_scale: 10, // Challenge requirement: CFG reset → 10
    steps: 20,
    width: 512,
    height: 512,
    batch_size: 1,
    batch_count: 1,
  },
  
  advancedSettings: {
    codeformer_weight: 0.5,
    gfpgan_weight: 0.5,
    tile_size: 512,
    tile_overlap: 64,
    refiner_switch_at: 0.8,
  },
  
  sizingSettings: {
    width: 512,
    height: 512,
  },
  
  samplingSettings: {
    cfg_scale: 10, // Challenge requirement: CFG reset → 10
    steps: 20,
  },
};

// Type definitions for reset functions
export type ResetGroupType = keyof SliderGroupDefaults;

// Helper function to get defaults for a specific group
export const getGroupDefaults = (groupType: ResetGroupType) => {
  return sliderGroupDefaults[groupType];
};

// Individual reset functions for specific slider groups
export const resetFunctions = {
  // Reset core generation settings (within the main accordion)
  resetCoreGeneration: (updateSettings: (updates: any) => void) => {
    const defaults = sliderGroupDefaults.coreGeneration;
    updateSettings(defaults);
  },
  
  // Reset advanced settings accordion
  resetAdvancedSettings: (updateSettings: (updates: any) => void) => {
    const defaults = sliderGroupDefaults.advancedSettings;
    updateSettings(defaults);
  },
  
  // Reset sizing settings
  resetSizingSettings: (updateSettings: (updates: any) => void) => {
    const defaults = sliderGroupDefaults.sizingSettings;
    updateSettings(defaults);
  },
  
  // Reset sampling settings (CFG + Steps)
  resetSamplingSettings: (updateSettings: (updates: any) => void) => {
    const defaults = sliderGroupDefaults.samplingSettings;
    updateSettings(defaults);
  },
};