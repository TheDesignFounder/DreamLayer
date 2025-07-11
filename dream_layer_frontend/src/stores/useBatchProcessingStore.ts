import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { BatchJob, BatchQueueItem, BatchProcessingStats } from '@/types/batchProcessing';

interface BatchProcessingState {
  jobs: BatchJob[];
  queue: BatchQueueItem[];
  isProcessing: boolean;
  currentJob: BatchJob | null;
  maxConcurrentJobs: number;
  
  // Actions
  addJob: (job: Omit<BatchJob, 'id' | 'createdAt' | 'status' | 'progress' | 'results' | 'completedImages'>) => string;
  updateJob: (id: string, updates: Partial<BatchJob>) => void;
  removeJob: (id: string) => void;
  cancelJob: (id: string) => void;
  
  // Queue management
  addToQueue: (job: BatchJob, promptVariations?: string[], settingsVariations?: Record<string, any>[]) => void;
  removeFromQueue: (jobId: string) => void;
  clearQueue: () => void;
  processNext: () => Promise<void>;
  
  // Processing control
  startProcessing: () => void;
  stopProcessing: () => void;
  pauseProcessing: () => void;
  resumeProcessing: () => void;
  
  // Settings
  setMaxConcurrentJobs: (max: number) => void;
  
  // Getters
  getJob: (id: string) => BatchJob | undefined;
  getJobsByStatus: (status: BatchJob['status']) => BatchJob[];
  getStats: () => BatchProcessingStats;
  getPendingJobs: () => BatchJob[];
  getCompletedJobs: () => BatchJob[];
  
  // Cleanup
  clearCompletedJobs: () => void;
  clearAllJobs: () => void;
}

export const useBatchProcessingStore = create<BatchProcessingState>()(
  persist(
    (set, get) => ({
      jobs: [],
      queue: [],
      isProcessing: false,
      currentJob: null,
      maxConcurrentJobs: 1,
      
      addJob: (jobData) => {
        const job: BatchJob = {
          ...jobData,
          id: `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          createdAt: Date.now(),
          status: 'pending',
          progress: 0,
          results: [],
          completedImages: 0
        };
        
        set((state) => ({
          jobs: [job, ...state.jobs]
        }));
        
        return job.id;
      },
      
      updateJob: (id, updates) => {
        set((state) => ({
          jobs: state.jobs.map(job =>
            job.id === id ? { ...job, ...updates } : job
          ),
          currentJob: state.currentJob?.id === id 
            ? { ...state.currentJob, ...updates }
            : state.currentJob
        }));
      },
      
      removeJob: (id) => {
        set((state) => ({
          jobs: state.jobs.filter(job => job.id !== id),
          queue: state.queue.filter(item => item.job.id !== id),
          currentJob: state.currentJob?.id === id ? null : state.currentJob
        }));
      },
      
      cancelJob: (id) => {
        const { updateJob } = get();
        updateJob(id, { 
          status: 'cancelled', 
          completedAt: Date.now(),
          progress: 0 
        });
        
        set((state) => ({
          queue: state.queue.filter(item => item.job.id !== id),
          currentJob: state.currentJob?.id === id ? null : state.currentJob
        }));
      },
      
      addToQueue: (job, promptVariations, settingsVariations) => {
        set((state) => ({
          queue: [...state.queue, {
            job,
            promptVariations,
            settingsVariations
          }]
        }));
      },
      
      removeFromQueue: (jobId) => {
        set((state) => ({
          queue: state.queue.filter(item => item.job.id !== jobId)
        }));
      },
      
      clearQueue: () => {
        set({ queue: [] });
      },
      
      processNext: async () => {
        const { queue, isProcessing, updateJob } = get();
        
        if (!isProcessing || queue.length === 0) return;
        
        const nextItem = queue[0];
        const job = nextItem.job;
        
        // Remove from queue and set as current
        set((state) => ({
          queue: state.queue.slice(1),
          currentJob: job
        }));
        
        // Update job status
        updateJob(job.id, {
          status: 'running',
          startedAt: Date.now(),
          progress: 0
        });
        
        try {
          // Simulate batch processing logic
          await simulateBatchProcessing(job, nextItem.promptVariations, nextItem.settingsVariations, get());
          
          updateJob(job.id, {
            status: 'completed',
            completedAt: Date.now(),
            progress: 100
          });
        } catch (error) {
          updateJob(job.id, {
            status: 'failed',
            completedAt: Date.now(),
            error: error instanceof Error ? error.message : 'Unknown error'
          });
        }
        
        // Clear current job and process next
        set({ currentJob: null });
        
        // Continue processing if there are more jobs
        if (get().queue.length > 0 && get().isProcessing) {
          setTimeout(() => get().processNext(), 1000);
        } else {
          set({ isProcessing: false });
        }
      },
      
      startProcessing: () => {
        set({ isProcessing: true });
        get().processNext();
      },
      
      stopProcessing: () => {
        set({ isProcessing: false, currentJob: null });
      },
      
      pauseProcessing: () => {
        set({ isProcessing: false });
      },
      
      resumeProcessing: () => {
        set({ isProcessing: true });
        get().processNext();
      },
      
      setMaxConcurrentJobs: (max) => {
        set({ maxConcurrentJobs: Math.max(1, Math.min(5, max)) });
      },
      
      getJob: (id) => {
        return get().jobs.find(job => job.id === id);
      },
      
      getJobsByStatus: (status) => {
        return get().jobs.filter(job => job.status === status);
      },
      
      getStats: () => {
        const { jobs } = get();
        const completed = jobs.filter(j => j.status === 'completed');
        const failed = jobs.filter(j => j.status === 'failed');
        const totalImages = jobs.reduce((sum, job) => sum + job.completedImages, 0);
        
        const processingTimes = completed
          .filter(job => job.startedAt && job.completedAt)
          .map(job => job.completedAt! - job.startedAt!);
        
        const avgProcessingTime = processingTimes.length > 0
          ? processingTimes.reduce((sum, time) => sum + time, 0) / processingTimes.length
          : 0;
        
        return {
          totalJobs: jobs.length,
          completedJobs: completed.length,
          failedJobs: failed.length,
          totalImages,
          processingTime: avgProcessingTime,
          queueSize: get().queue.length
        };
      },
      
      getPendingJobs: () => {
        return get().jobs.filter(job => job.status === 'pending');
      },
      
      getCompletedJobs: () => {
        return get().jobs.filter(job => job.status === 'completed');
      },
      
      clearCompletedJobs: () => {
        set((state) => ({
          jobs: state.jobs.filter(job => job.status !== 'completed')
        }));
      },
      
      clearAllJobs: () => {
        set({
          jobs: [],
          queue: [],
          currentJob: null,
          isProcessing: false
        });
      }
    }),
    {
      name: 'batch-processing-storage',
      version: 1,
      partialize: (state) => ({
        jobs: state.jobs.filter(job => job.status !== 'running'), // Don't persist running jobs
        maxConcurrentJobs: state.maxConcurrentJobs
      })
    }
  )
);

// Simulate batch processing for demonstration
async function simulateBatchProcessing(
  job: BatchJob, 
  promptVariations: string[] = [],
  settingsVariations: Record<string, any>[] = [],
  store: any
) {
  const totalImages = job.totalImages;
  const variations = Math.max(promptVariations.length, settingsVariations.length, 1);
  const imagesPerVariation = Math.ceil(totalImages / variations);
  
  for (let i = 0; i < variations; i++) {
    for (let j = 0; j < imagesPerVariation && (i * imagesPerVariation + j) < totalImages; j++) {
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));
      
      const completedImages = i * imagesPerVariation + j + 1;
      const progress = Math.round((completedImages / totalImages) * 100);
      
      // Simulate generated image URL
      const imageUrl = `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
      
      store.updateJob(job.id, {
        progress,
        completedImages,
        results: [...job.results, imageUrl]
      });
      
      // Check if job was cancelled
      const currentJob = store.getJob(job.id);
      if (currentJob?.status === 'cancelled') {
        throw new Error('Job was cancelled');
      }
    }
  }
}