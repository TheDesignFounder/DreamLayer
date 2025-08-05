import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Preset, PresetCreateRequest, PresetUpdateRequest, DEFAULT_PRESETS } from '../types/preset';
import { CoreGenerationSettings } from '../types/generationSettings';
import { ControlNetRequest } from '../types/controlnet';

interface PresetState {
  presets: Preset[];
  selectedPresetId: string | null;
  
  // Actions
  initializeDefaultPresets: () => void;
  createPreset: (presetData: PresetCreateRequest) => Preset;
  updatePreset: (id: string, updates: PresetUpdateRequest) => Preset | null;
  deletePreset: (id: string) => boolean;
  selectPreset: (id: string | null) => void;
  getSelectedPreset: () => Preset | null;
  getPresetById: (id: string) => Preset | null;
  generatePresetHash: (settings: CoreGenerationSettings, controlnet?: ControlNetRequest) => string;
  applyPresetToSettings: (preset: Preset) => { settings: CoreGenerationSettings; controlnet?: ControlNetRequest };
}

// Generate a hash for preset settings to ensure version pinning
const generateHash = (data: any): string => {
  const jsonString = JSON.stringify(data, Object.keys(data).sort());
  let hash = 0;
  for (let i = 0; i < jsonString.length; i++) {
    const char = jsonString.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
};

export const usePresetStore = create<PresetState>()(
  persist(
    (set, get) => ({
      presets: [],
      selectedPresetId: null,

      initializeDefaultPresets: () => {
        const { presets } = get();
        if (presets.length === 0) {
          const now = new Date().toISOString();
          const defaultPresets: Preset[] = DEFAULT_PRESETS.map((preset, index) => ({
            ...preset,
            id: `default-${index}`,
            hash: generateHash({ settings: preset.settings, controlnet: preset.controlnet }),
            created_at: now,
            updated_at: now,
            is_default: true
          }));
          set({ presets: defaultPresets });
        }
      },

      createPreset: (presetData: PresetCreateRequest) => {
        const { presets } = get();
        const now = new Date().toISOString();
        const hash = generateHash({ settings: presetData.settings, controlnet: presetData.controlnet });
        
        const newPreset: Preset = {
          id: `preset-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: presetData.name,
          description: presetData.description,
          version: '1.0.0',
          hash,
          settings: presetData.settings,
          controlnet: presetData.controlnet,
          created_at: now,
          updated_at: now,
          is_default: false
        };

        set({ presets: [...presets, newPreset] });
        return newPreset;
      },

      updatePreset: (id: string, updates: PresetUpdateRequest) => {
        const { presets } = get();
        const presetIndex = presets.findIndex(p => p.id === id);
        
        if (presetIndex === -1) return null;

        const updatedPreset = { ...presets[presetIndex] };
        
        if (updates.name) updatedPreset.name = updates.name;
        if (updates.description !== undefined) updatedPreset.description = updates.description;
        if (updates.settings) updatedPreset.settings = updates.settings;
        if (updates.controlnet !== undefined) updatedPreset.controlnet = updates.controlnet;
        
        // Regenerate hash if settings changed
        if (updates.settings || updates.controlnet !== undefined) {
          updatedPreset.hash = generateHash({ 
            settings: updatedPreset.settings, 
            controlnet: updatedPreset.controlnet 
          });
        }
        
        updatedPreset.updated_at = new Date().toISOString();
        
        const newPresets = [...presets];
        newPresets[presetIndex] = updatedPreset;
        set({ presets: newPresets });
        
        return updatedPreset;
      },

      deletePreset: (id: string) => {
        const { presets, selectedPresetId } = get();
        const filteredPresets = presets.filter(p => p.id !== id);
        
        // If deleting selected preset, clear selection
        let newSelectedId = selectedPresetId;
        if (selectedPresetId === id) {
          newSelectedId = null;
        }
        
        set({ presets: filteredPresets, selectedPresetId: newSelectedId });
        return true;
      },

      selectPreset: (id: string | null) => {
        set({ selectedPresetId: id });
      },

      getSelectedPreset: () => {
        const { presets, selectedPresetId } = get();
        return selectedPresetId ? presets.find(p => p.id === selectedPresetId) || null : null;
      },

      getPresetById: (id: string) => {
        const { presets } = get();
        return presets.find(p => p.id === id) || null;
      },

      generatePresetHash: (settings: CoreGenerationSettings, controlnet?: ControlNetRequest) => {
        return generateHash({ settings, controlnet });
      },

      applyPresetToSettings: (preset: Preset) => {
        return {
          settings: { ...preset.settings },
          controlnet: preset.controlnet ? { ...preset.controlnet } : undefined
        };
      }
    }),
    {
      name: 'dreamlayer-presets',
      partialize: (state) => ({ 
        presets: state.presets,
        selectedPresetId: state.selectedPresetId 
      })
    }
  )
); 