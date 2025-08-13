import { create } from 'zustand';
import { RunConfig, RunRegistryState, RunRegistryActions } from '@/types/runRegistry';

interface RunRegistryStore extends RunRegistryState, RunRegistryActions {}

const API_BASE_URL = 'http://localhost:5005/api';

export const useRunRegistryStore = create<RunRegistryStore>((set, get) => ({
  // Initial state
  runs: [],
  loading: false,
  error: null,
  selectedRun: null,

  // Actions
  fetchRuns: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE_URL}/runs`);
      const data = await response.json();
      
      if (data.status === 'success' && data.runs) {
        const normalizedRuns = data.runs.map((run: any) => ({ ...run, loras: run.loras || [], controlnets: run.controlnets || [] }));
        set({ runs: normalizedRuns, loading: false });
      } else {
        set({ error: data.message || 'Failed to fetch runs', loading: false });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch runs', 
        loading: false 
      });
    }
  },

  fetchRun: async (runId: string) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}`);
      const data = await response.json();
      
      if (data.status === 'success' && data.run) {
        set({ selectedRun: data.run, loading: false });
      } else {
        set({ error: data.message || 'Failed to fetch run', loading: false });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch run', 
        loading: false 
      });
    }
  },

  deleteRun: async (runId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        // Remove the run from the local state
        const { runs } = get();
        const updatedRuns = runs.filter(run => run.run_id !== runId);
        set({ runs: updatedRuns });
      } else {
        set({ error: data.message || 'Failed to delete run' });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to delete run'
      });
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setSelectedRun: (run: RunConfig | null) => {
    set({ selectedRun: run });
  },
})); 