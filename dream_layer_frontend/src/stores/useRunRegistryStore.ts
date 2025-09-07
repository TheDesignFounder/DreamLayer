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
      // Try consolidated enhanced API first (v2 with consolidated module)
      let response = await fetch(`${API_BASE_URL}/runs/enhanced/v2`);
      let data = await response.json();
      
      // Fallback to v1 enhanced API
      if (!response.ok || data.status !== 'success') {
        console.log('V2 enhanced API not available, trying V1...');
        response = await fetch(`${API_BASE_URL}/runs/enhanced`);
        data = await response.json();
      }
      
      // Final fallback to regular API
      if (!response.ok || data.status !== 'success') {
        console.log('Enhanced APIs not available, falling back to regular API');
        response = await fetch(`${API_BASE_URL}/runs`);
        data = await response.json();
      }
      
      if (data.status === 'success' && data.runs) {
        const normalizedRuns = data.runs.map((run: any) => ({ 
          ...run, 
          loras: run.loras || [], 
          controlnets: run.controlnets || [],
          // Ensure metrics are included (may be null for runs without them)
          clip_score_mean: run.clip_score_mean || null,
          fid_score: run.fid_score || null,
          // Composition metrics
          macro_precision: run.macro_precision || null,
          macro_recall: run.macro_recall || null,
          macro_f1: run.macro_f1 || null
        }));
        set({ runs: normalizedRuns, loading: false });
        
        // Log ClipScore availability for debugging
        const runsWithClipScore = normalizedRuns.filter(run => run.clip_score_mean !== null);
        const enhancementAvailable = data.enhancement_available || data.database_enabled;
        
        console.log(`✅ Loaded ${normalizedRuns.length} runs, ${runsWithClipScore.length} with ClipScore`);
        console.log(`📊 Enhancement available: ${enhancementAvailable}`);
        
        if (enhancementAvailable && runsWithClipScore.length > 0) {
          const avgClipScore = runsWithClipScore.reduce((sum, run) => sum + (run.clip_score_mean || 0), 0) / runsWithClipScore.length;
          console.log(`📈 Average ClipScore: ${avgClipScore.toFixed(4)}`);
        }
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
      // Try consolidated enhanced API first (v2)
      let response = await fetch(`${API_BASE_URL}/runs/${runId}/enhanced/v2`);
      let data = await response.json();
      
      // Fallback to v1 enhanced API
      if (!response.ok || data.status !== 'success') {
        response = await fetch(`${API_BASE_URL}/runs/${runId}/enhanced`);
        data = await response.json();
      }
      
      // Final fallback to regular API
      if (!response.ok || data.status !== 'success') {
        response = await fetch(`${API_BASE_URL}/runs/${runId}`);
        data = await response.json();
      }
      
      if (data.status === 'success' && data.run) {
        const normalizedRun = {
          ...data.run,
          loras: data.run.loras || [],
          controlnets: data.run.controlnets || [],
          clip_score_mean: data.run.clip_score_mean || null,
          fid_score: data.run.fid_score || null
        };
        set({ selectedRun: normalizedRun, loading: false });
        
        console.log(`✅ Loaded run ${runId} with ClipScore: ${normalizedRun.clip_score_mean || 'N/A'}`);
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
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE_URL}/runs/${runId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        const currentRuns = get().runs;
        set({ 
          runs: currentRuns.filter(run => run.run_id !== runId),
          loading: false 
        });
      } else {
        set({ error: data.message || 'Failed to delete run', loading: false });
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to delete run', 
        loading: false 
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
