import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { MatrixRunnerStore, MatrixJob, ParameterRange, MatrixParameters } from '@/types/matrixRunner';
import { Txt2ImgCoreSettings, defaultTxt2ImgSettings } from '@/types/generationSettings';
import { 
  generateJobs, 
  calculateETA, 
  updateAverageTimePerJob, 
  calculateTotalJobs,
  groupJobsForBatching
} from '@/utils/matrixUtils';

// IndexedDB storage adapter for Zustand
const createIndexedDBStorage = () => {
  const dbName = 'dreamlayer-matrix-runner';
  const storeName = 'matrix-runner-state';
  const version = 1;

  return {
    getItem: async (name: string): Promise<string | null> => {
      return new Promise((resolve) => {
        const request = indexedDB.open(dbName, version);
        
        request.onerror = () => resolve(null);
        request.onsuccess = () => {
          const db = request.result;
          const transaction = db.transaction([storeName], 'readonly');
          const store = transaction.objectStore(storeName);
          const getRequest = store.get(name);
          
          getRequest.onerror = () => resolve(null);
          getRequest.onsuccess = () => {
            resolve(getRequest.result || null);
          };
        };
        
        request.onupgradeneeded = () => {
          const db = request.result;
          if (!db.objectStoreNames.contains(storeName)) {
            db.createObjectStore(storeName);
          }
        };
      });
    },
    
    setItem: async (name: string, value: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, version);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
          const db = request.result;
          const transaction = db.transaction([storeName], 'readwrite');
          const store = transaction.objectStore(storeName);
          const putRequest = store.put(value, name);
          
          putRequest.onerror = () => reject(putRequest.error);
          putRequest.onsuccess = () => resolve();
        };
        
        request.onupgradeneeded = () => {
          const db = request.result;
          if (!db.objectStoreNames.contains(storeName)) {
            db.createObjectStore(storeName);
          }
        };
      });
    },
    
    removeItem: async (name: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName, version);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
          const db = request.result;
          const transaction = db.transaction([storeName], 'readwrite');
          const store = transaction.objectStore(storeName);
          const deleteRequest = store.delete(name);
          
          deleteRequest.onerror = () => reject(deleteRequest.error);
          deleteRequest.onsuccess = () => resolve();
        };
        
        request.onupgradeneeded = () => {
          const db = request.result;
          if (!db.objectStoreNames.contains(storeName)) {
            db.createObjectStore(storeName);
          }
        };
      });
    }
  };
};

export const useMatrixRunnerStore = create<MatrixRunnerStore>()(
  persist(
    (set, get) => ({
      // Initial state
      parameters: {},
      baseSettings: { ...defaultTxt2ImgSettings },
      jobs: [],
      currentJobIndex: 0,
      isRunning: false,
      isPaused: false,
      totalJobs: 0,
      completedJobs: 0,
      failedJobs: 0,
      pendingJobs: 0,
      showProgressGrid: false,
      autoBatch: true,

      // Parameter management
      setParameter: (param, range) => {
        set((state) => ({
          parameters: {
            ...state.parameters,
            [param]: range
          }
        }));
      },

      setBaseSettings: (settings) => {
        set((state) => ({
          baseSettings: {
            ...state.baseSettings,
            ...settings
          }
        }));
      },

      // Job management
      generateJobs: () => {
        const { parameters, baseSettings } = get();
        const jobs = generateJobs(parameters, baseSettings);
        const totalJobs = calculateTotalJobs(parameters);
        
        set({
          jobs,
          totalJobs,
          completedJobs: 0,
          failedJobs: 0,
          pendingJobs: totalJobs,
          currentJobIndex: 0
        });
      },

      startMatrix: async () => {
        const { jobs, isRunning, isPaused } = get();
        
        if (jobs.length === 0) {
          console.warn('No jobs to run');
          return;
        }

        if (isRunning && !isPaused) {
          console.warn('Matrix is already running');
          return;
        }

        set({
          isRunning: true,
          isPaused: false,
          startTime: Date.now()
        });

        // Start executing jobs
        await get().executeNextJob();
      },

      pauseMatrix: () => {
        set({
          isPaused: true,
          isRunning: false
        });
      },

      resumeMatrix: async () => {
        const { jobs, currentJobIndex, isPaused } = get();
        
        if (!isPaused || currentJobIndex >= jobs.length) {
          return;
        }

        set({
          isPaused: false,
          isRunning: true
        });

        // Resume executing jobs
        await get().executeNextJob();
      },

      stopMatrix: () => {
        set({
          isRunning: false,
          isPaused: false
        });
      },

      clearJobs: () => {
        set({
          jobs: [],
          currentJobIndex: 0,
          isRunning: false,
          isPaused: false,
          totalJobs: 0,
          completedJobs: 0,
          failedJobs: 0,
          pendingJobs: 0,
          startTime: undefined,
          estimatedTimeRemaining: undefined,
          averageTimePerJob: undefined
        });
      },

      // Job execution
      executeNextJob: async () => {
        const { jobs, currentJobIndex, isRunning, isPaused, autoBatch } = get();
        
        if (!isRunning || isPaused || currentJobIndex >= jobs.length) {
          return;
        }

        const currentJob = jobs[currentJobIndex];
        if (!currentJob || currentJob.status !== 'pending') {
          // Move to next job
          set({ currentJobIndex: currentJobIndex + 1 });
          await get().executeNextJob();
          return;
        }

        // Update job status to running
        get().updateJobStatus(currentJob.id, 'running');

        try {
          // Execute the job
          const startTime = Date.now();
          
          const response = await fetch('http://localhost:5001/api/txt2img', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentJob.parameters),
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const data = await response.json();
          const endTime = Date.now();
          const jobDuration = (endTime - startTime) / 1000; // Convert to seconds

          if (data.comfy_response?.generated_images) {
            const images = data.comfy_response.generated_images.map((img: any) => ({
              id: `${Date.now()}-${Math.random()}`,
              url: img.url,
              prompt: currentJob.parameters.prompt,
              negativePrompt: currentJob.parameters.negative_prompt,
              timestamp: Date.now(),
              settings: currentJob.parameters
            }));

            // Update job with success result
            get().updateJobStatus(currentJob.id, 'completed', { images }, undefined, jobDuration);
          } else {
            throw new Error('No images were generated');
          }
        } catch (error) {
          console.error('Job execution failed:', error);
          get().updateJobStatus(currentJob.id, 'failed', undefined, error instanceof Error ? error.message : 'Unknown error');
        }

        // Move to next job
        set({ currentJobIndex: currentJobIndex + 1 });

        // Continue with next job if still running
        if (get().isRunning && !get().isPaused) {
          // Add a small delay to prevent overwhelming the server
          setTimeout(() => {
            get().executeNextJob();
          }, 100);
        }
      },

      updateJobStatus: (jobId, status, result, error, duration) => {
        set((state) => {
          const updatedJobs = state.jobs.map(job => 
            job.id === jobId 
              ? {
                  ...job,
                  status,
                  ...(result && { result }),
                  ...(error && { error }),
                  ...(status === 'running' && { startedAt: Date.now() }),
                  ...(status === 'completed' && { completedAt: Date.now() }),
                  ...(status === 'failed' && { completedAt: Date.now() })
                }
              : job
          );

          // Calculate statistics
          const completedJobs = updatedJobs.filter(job => job.status === 'completed').length;
          const failedJobs = updatedJobs.filter(job => job.status === 'failed').length;
          const pendingJobs = updatedJobs.filter(job => job.status === 'pending').length;

          // Update average time per job if we have duration
          let averageTimePerJob = state.averageTimePerJob;
          if (duration && status === 'completed') {
            averageTimePerJob = updateAverageTimePerJob(
              averageTimePerJob || 0,
              duration,
              completedJobs
            );
          }

          // Calculate ETA
          const estimatedTimeRemaining = calculateETA(
            completedJobs,
            state.totalJobs,
            averageTimePerJob || 0,
            state.startTime
          );

          return {
            jobs: updatedJobs,
            completedJobs,
            failedJobs,
            pendingJobs,
            averageTimePerJob,
            estimatedTimeRemaining
          };
        });
      },

      // UI actions
      toggleProgressGrid: () => {
        set((state) => ({
          showProgressGrid: !state.showProgressGrid
        }));
      },

      toggleAutoBatch: () => {
        set((state) => ({
          autoBatch: !state.autoBatch
        }));
      },

      // Persistence (handled by Zustand persist middleware)
      saveToIndexedDB: async () => {
        // This is handled automatically by the persist middleware
        return Promise.resolve();
      },

      loadFromIndexedDB: async () => {
        // This is handled automatically by the persist middleware
        return Promise.resolve();
      }
    }),
    {
      name: 'matrix-runner-storage',
      storage: createJSONStorage(() => createIndexedDBStorage()),
      partialize: (state) => ({
        parameters: state.parameters,
        baseSettings: state.baseSettings,
        jobs: state.jobs,
        currentJobIndex: state.currentJobIndex,
        isRunning: state.isRunning,
        isPaused: state.isPaused,
        totalJobs: state.totalJobs,
        completedJobs: state.completedJobs,
        failedJobs: state.failedJobs,
        pendingJobs: state.pendingJobs,
        startTime: state.startTime,
        estimatedTimeRemaining: state.estimatedTimeRemaining,
        averageTimePerJob: state.averageTimePerJob,
        showProgressGrid: state.showProgressGrid,
        autoBatch: state.autoBatch
      })
    }
  )
); 