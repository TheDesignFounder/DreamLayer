import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { MatrixJob } from '@/types/generationSettings';

interface MatrixState {
  jobs: MatrixJob[];
  currentJobIndex: number;
  isPaused: boolean;
  setInitialState: (jobs: MatrixJob[]) => void;
  advanceJob: () => void;
  setPaused: (isPaused: boolean) => void;
  updateJobStatus: (index: number, status: 'completed' | 'failed' | 'running', data?: any) => void;
  reset: () => void;
}

export const useMatrixStore = create<MatrixState>(
  persist(
    (set) => ({
      jobs: [],
      currentJobIndex: 0,
      isPaused: true,
      setInitialState: (jobs) => {
        set({ jobs, currentJobIndex: 0, isPaused: false });
      },
      advanceJob: () => {
        set(state => ({ currentJobIndex: state.currentJobIndex + 1 }));
      },
      setPaused: (isPaused) => {
        set({ isPaused });
      },
      updateJobStatus: (index, status, data) => {
        set(state => {
            const newJobs = [...state.jobs];
            const currentJob = newJobs[index];
            if (currentJob) {
                newJobs[index] = { ...currentJob, status, ...data };
            }
            return { jobs: newJobs };
        });
      },
      reset: () => {
        set({ jobs: [], currentJobIndex: 0, isPaused: true });
      },
    }),
    {
      name: 'matrix-generation-storage',
    }
  )
); 