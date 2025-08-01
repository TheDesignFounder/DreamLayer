import { Preset, PresetCreateRequest, PresetUpdateRequest, PresetResponse } from '../types/preset';
import { CoreGenerationSettings } from '../types/generationSettings';
import { ControlNetRequest } from '../types/controlnet';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

export class PresetService {
  static async getAllPresets(): Promise<Preset[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets`);
      const data: PresetResponse = await response.json();
      
      if (data.status === 'success' && data.presets) {
        return data.presets;
      } else {
        throw new Error(data.message || 'Failed to fetch presets');
      }
    } catch (error) {
      console.error('Error fetching presets:', error);
      throw error;
    }
  }

  static async createPreset(presetData: PresetCreateRequest): Promise<Preset> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(presetData),
      });
      
      const data: PresetResponse = await response.json();
      
      if (data.status === 'success' && data.preset) {
        return data.preset;
      } else {
        throw new Error(data.message || 'Failed to create preset');
      }
    } catch (error) {
      console.error('Error creating preset:', error);
      throw error;
    }
  }

  static async updatePreset(presetId: string, updates: PresetUpdateRequest): Promise<Preset> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets/${presetId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });
      
      const data: PresetResponse = await response.json();
      
      if (data.status === 'success' && data.preset) {
        return data.preset;
      } else {
        throw new Error(data.message || 'Failed to update preset');
      }
    } catch (error) {
      console.error('Error updating preset:', error);
      throw error;
    }
  }

  static async deletePreset(presetId: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets/${presetId}`, {
        method: 'DELETE',
      });
      
      const data: PresetResponse = await response.json();
      
      if (data.status === 'success') {
        return true;
      } else {
        throw new Error(data.message || 'Failed to delete preset');
      }
    } catch (error) {
      console.error('Error deleting preset:', error);
      throw error;
    }
  }

  static async getPreset(presetId: string): Promise<Preset> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets/${presetId}`);
      const data: PresetResponse = await response.json();
      
      if (data.status === 'success' && data.preset) {
        return data.preset;
      } else {
        throw new Error(data.message || 'Failed to fetch preset');
      }
    } catch (error) {
      console.error('Error fetching preset:', error);
      throw error;
    }
  }

  static async validatePresetHash(
    presetId: string,
    settings: CoreGenerationSettings,
    controlnet?: ControlNetRequest
  ): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/presets/validate-hash`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          preset_id: presetId,
          settings,
          controlnet,
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        return data.is_valid;
      } else {
        throw new Error(data.message || 'Failed to validate preset hash');
      }
    } catch (error) {
      console.error('Error validating preset hash:', error);
      throw error;
    }
  }
} 