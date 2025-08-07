import { create } from 'zustand';
import { Run, RunRegistryState } from '@/types/run';

interface RunRegistryStore extends RunRegistryState {
  // Actions
  setRuns: (runs: Run[]) => void;
  addRun: (run: Run) => void;
  selectRun: (run: Run | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  getRunById: (id: string) => Run | undefined;
}

export const useRunRegistryStore = create<RunRegistryStore>((set, get) => ({
  // Initial state
  runs: [],
  selectedRun: null,
  isLoading: false,
  error: null,

  // Actions
  setRuns: (runs) => set({ runs }),
  
  addRun: (run) => set((state) => ({
    runs: [run, ...state.runs] // Add new runs at the beginning
  })),
  
  selectRun: (run) => set({ selectedRun: run }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
  
  getRunById: (id) => {
    const state = get();
    return state.runs.find(run => run.id === id);
  }
})); 