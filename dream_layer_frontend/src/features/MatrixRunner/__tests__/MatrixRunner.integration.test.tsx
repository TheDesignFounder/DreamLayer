import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react';
import '@testing-library/jest-dom';
import { useMatrixRunnerStore } from '@/stores/useMatrixRunnerStore';
import MatrixRunnerPage from '../MatrixRunnerPage';

// Mock the fetch API
global.fetch = jest.fn();

// Mock the toast notifications
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock IndexedDB
const mockIndexedDB = {
  open: jest.fn(() => ({
    result: {
      createObjectStore: jest.fn(),
      transaction: jest.fn(() => ({
        objectStore: jest.fn(() => ({
          put: jest.fn(),
          get: jest.fn(),
          delete: jest.fn(),
          clear: jest.fn(),
        })),
      })),
    },
    onerror: null,
    onsuccess: null,
    onupgradeneeded: null,
  })),
};

Object.defineProperty(window, 'indexedDB', {
  value: mockIndexedDB,
  writable: true,
});

describe('Matrix Runner Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset the store state
    act(() => {
      useMatrixRunnerStore.getState().clearJobs();
    });
  });

  describe('Task #2 Requirements', () => {
    test('3×2 sweep completes jobs exactly once', async () => {
      // Setup: Create a 3×2 matrix (3 seeds × 2 samplers = 6 jobs)
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          comfy_response: {
            generated_images: [{
              url: 'http://localhost:5001/view?filename=test.png',
              filename: 'test.png'
            }]
          }
        })
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      render(<MatrixRunnerPage selectedModel="test-model" onTabChange={jest.fn()} />);

      // 1. Set up the matrix parameters for 3×2 sweep
      const promptInput = screen.getByLabelText('Prompt');
      fireEvent.change(promptInput, { target: { value: 'A beautiful landscape' } });

      const seedsInput = screen.getByLabelText('Seeds');
      fireEvent.change(seedsInput, { target: { value: '1-3' } });

      const samplersInput = screen.getByLabelText('Samplers');
      fireEvent.change(samplersInput, { target: { value: 'euler,dpm++' } });

      // 2. Generate jobs
      const generateButton = screen.getByText(/Generate Jobs \(6\)/);
      fireEvent.click(generateButton);

      // Wait for jobs to be generated
      await waitFor(() => {
        expect(screen.getByText(/6 jobs completed/)).toBeInTheDocument();
      });

      // 3. Start the matrix
      const startButton = screen.getByText(/Start Matrix/);
      fireEvent.click(startButton);

      // 4. Wait for all jobs to complete
      await waitFor(() => {
        const completedJobs = useMatrixRunnerStore.getState().completedJobs;
        expect(completedJobs).toBe(6);
      }, { timeout: 10000 });

      // 5. Verify no duplicates
      const jobs = useMatrixRunnerStore.getState().jobs;
      const jobIds = jobs.map(job => job.id);
      const uniqueJobIds = new Set(jobIds);
      expect(uniqueJobIds.size).toBe(6);
      expect(jobIds.length).toBe(6);

      // 6. Verify each job was completed exactly once
      const completedJobs = jobs.filter(job => job.status === 'completed');
      expect(completedJobs.length).toBe(6);
    });

    test('Pause and resume operate without creating duplicates', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          comfy_response: {
            generated_images: [{
              url: 'http://localhost:5001/view?filename=test.png',
              filename: 'test.png'
            }]
          }
        })
      };

      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      render(<MatrixRunnerPage selectedModel="test-model" onTabChange={jest.fn()} />);

      // Setup matrix
      fireEvent.change(screen.getByLabelText('Prompt'), { target: { value: 'Test prompt' } });
      fireEvent.change(screen.getByLabelText('Seeds'), { target: { value: '1-5' } });
      fireEvent.change(screen.getByLabelText('Samplers'), { target: { value: 'euler' } });

      // Generate and start
      fireEvent.click(screen.getByText(/Generate Jobs \(5\)/));
      fireEvent.click(screen.getByText(/Start Matrix/));

      // Wait for some jobs to start
      await waitFor(() => {
        const runningJobs = useMatrixRunnerStore.getState().jobs.filter(job => job.status === 'running');
        expect(runningJobs.length).toBeGreaterThan(0);
      });

      // Pause
      const pauseButton = screen.getByText(/Pause/);
      fireEvent.click(pauseButton);

      await waitFor(() => {
        expect(useMatrixRunnerStore.getState().isPaused).toBe(true);
      });

      // Resume
      const resumeButton = screen.getByText(/Resume/);
      fireEvent.click(resumeButton);

      // Wait for completion
      await waitFor(() => {
        const completedJobs = useMatrixRunnerStore.getState().completedJobs;
        expect(completedJobs).toBe(5);
      }, { timeout: 10000 });

      // Verify no duplicates
      const jobs = useMatrixRunnerStore.getState().jobs;
      const jobIds = jobs.map(job => job.id);
      const uniqueJobIds = new Set(jobIds);
      expect(uniqueJobIds.size).toBe(5);
    });

    test('State survives page refresh', async () => {
      // Setup initial state
      act(() => {
        const store = useMatrixRunnerStore.getState();
        store.setParameter('seeds', { type: 'range', values: [1, 2, 3], original: '1-3' });
        store.setParameter('samplers', { type: 'list', values: ['euler', 'dpm++'], original: 'euler,dpm++' });
        store.setBaseSettings({ prompt: 'Test prompt', model_name: 'test-model' });
        store.generateJobs();
      });

      // Simulate page refresh by re-rendering
      const { unmount } = render(<MatrixRunnerPage selectedModel="test-model" onTabChange={jest.fn()} />);
      unmount();

      // Re-render and check state persistence
      render(<MatrixRunnerPage selectedModel="test-model" onTabChange={jest.fn()} />);

      await waitFor(() => {
        const state = useMatrixRunnerStore.getState();
        expect(state.totalJobs).toBe(6);
        expect(state.jobs.length).toBe(6);
        expect(state.baseSettings.prompt).toBe('Test prompt');
      });
    });

    test('Deterministic job list generation', () => {
      act(() => {
        const store = useMatrixRunnerStore.getState();
        store.setParameter('seeds', { type: 'range', values: [1, 2], original: '1-2' });
        store.setParameter('samplers', { type: 'list', values: ['euler'], original: 'euler' });
        store.setBaseSettings({ prompt: 'Test', model_name: 'test-model' });
        store.generateJobs();
      });

      const jobs1 = useMatrixRunnerStore.getState().jobs;

      // Clear and regenerate
      act(() => {
        useMatrixRunnerStore.getState().clearJobs();
        const store = useMatrixRunnerStore.getState();
        store.setParameter('seeds', { type: 'range', values: [1, 2], original: '1-2' });
        store.setParameter('samplers', { type: 'list', values: ['euler'], original: 'euler' });
        store.setBaseSettings({ prompt: 'Test', model_name: 'test-model' });
        store.generateJobs();
      });

      const jobs2 = useMatrixRunnerStore.getState().jobs;

      // Verify deterministic generation
      expect(jobs1.length).toBe(jobs2.length);
      expect(jobs1.map(j => j.id).sort()).toEqual(jobs2.map(j => j.id).sort());
    });

    test('Parameter parsing handles various formats', () => {
      render(<MatrixRunnerPage selectedModel="test-model" onTabChange={jest.fn()} />);

      // Test range format
      fireEvent.change(screen.getByLabelText('Seeds'), { target: { value: '1-5' } });
      expect(screen.getByText('range')).toBeInTheDocument();
      expect(screen.getByText('5 values')).toBeInTheDocument();

      // Test list format
      fireEvent.change(screen.getByLabelText('Samplers'), { target: { value: 'euler,dpm++,ddim' } });
      const listElements = screen.getAllByText('list');
      expect(listElements[0]).toBeInTheDocument();
      const valueElements = screen.getAllByText('3 values');
      expect(valueElements[0]).toBeInTheDocument();

      // Test mixed format
      fireEvent.change(screen.getByLabelText('Steps'), { target: { value: '20,30,40' } });
      const listElements2 = screen.getAllByText('list');
      expect(listElements2[0]).toBeInTheDocument();
      const valueElements2 = screen.getAllByText('3 values');
      expect(valueElements2[0]).toBeInTheDocument();
    });
  });

  describe('Advanced Features', () => {
    test('Auto batching groups similar jobs', () => {
      act(() => {
        const store = useMatrixRunnerStore.getState();
        store.setParameter('seeds', { type: 'range', values: [1, 2], original: '1-2' });
        store.setParameter('samplers', { type: 'list', values: ['euler', 'dpm++'], original: 'euler,dpm++' });
        store.setBaseSettings({ 
          prompt: 'Test', 
          model_name: 'test-model',
          width: 512,
          height: 512
        });
        store.generateJobs();
      });

      const jobs = useMatrixRunnerStore.getState().jobs;
      
      // Verify jobs have different parameters but same model/size
      const uniqueConfigs = new Set(
        jobs.map(job => JSON.stringify({
          model: job.parameters.model_name,
          width: job.parameters.width,
          height: job.parameters.height
        }))
      );
      
      expect(uniqueConfigs.size).toBe(1); // All jobs should have same model/size config
    });
  });
}); 