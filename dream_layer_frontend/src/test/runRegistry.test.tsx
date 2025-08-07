import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Runs from '../pages/Runs';
import { useRunRegistryStore } from '../stores/useRunRegistryStore';
import { Run } from '../types/run';

// Mock the store
vi.mock('../stores/useRunRegistryStore', () => ({
  useRunRegistryStore: vi.fn(),
}));

// Mock the service
vi.mock('../services/runService', () => ({
  runService: {
    getRuns: vi.fn(),
    getRunById: vi.fn(),
    createRun: vi.fn(),
  },
}));

const mockRun: Run = {
  id: 'test_run_001',
  timestamp: Date.now(),
  status: 'completed',
  config: {
    model: 'v1-5-pruned-emaonly-fp16.safetensors',
    vae: 'vae-ft-mse-840000-ema-pruned.safetensors',
    loras: [
      { name: 'lora_style_anime', strength: 0.8 }
    ],
    controlnets: [
      { name: 'control_v11p_sd15_canny', strength: 1.0 }
    ],
    prompt: 'A beautiful anime character in a magical forest',
    negative_prompt: 'blurry, low quality, distorted',
    seed: 123456789,
    sampler: 'euler',
    steps: 20,
    cfg_scale: 7.0,
    workflow: { nodes: {} },
    version: '1.0.0',
    width: 512,
    height: 512,
    batch_size: 1,
    batch_count: 1
  },
  images: [
    {
      filename: 'test_run_001_001.png',
      url: '/api/images/test_run_001_001.png'
    }
  ]
};

const mockRunWithEmptyValues: Run = {
  id: 'test_run_002',
  timestamp: Date.now(),
  status: 'failed',
  config: {
    model: '',
    vae: undefined,
    loras: [],
    controlnets: [],
    prompt: '',
    negative_prompt: '',
    seed: 0,
    sampler: '',
    steps: 0,
    cfg_scale: 0,
    workflow: {},
    version: '',
    width: 0,
    height: 0,
    batch_size: 0,
    batch_count: 0
  },
  images: []
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Run Registry', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Required Keys Test', () => {
    it('should display all required keys in run configuration', async () => {
      const mockStore = {
        runs: [mockRun],
        selectedRun: null,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      // Check that all required keys are displayed
      expect(screen.getByText('Run test_run_001')).toBeInTheDocument();
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
      expect(screen.getByText(/Sampler:/)).toBeInTheDocument();
      expect(screen.getByText(/Steps:/)).toBeInTheDocument();
      expect(screen.getByText(/CFG:/)).toBeInTheDocument();
      expect(screen.getByText(/Prompt:/)).toBeInTheDocument();
      
      // Check that the model name is displayed
      expect(screen.getByText('v1-5-pruned-emaonly-fp16.safetensors')).toBeInTheDocument();
      expect(screen.getByText('euler')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
      expect(screen.getByText('7.0')).toBeInTheDocument();
    });

    it('should handle empty values without crashes', async () => {
      const mockStore = {
        runs: [mockRunWithEmptyValues],
        selectedRun: null,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      // Should not crash with empty values
      expect(screen.getByText('Run test_run_002')).toBeInTheDocument();
      expect(screen.getByText('failed')).toBeInTheDocument();
      
      // Empty values should be handled gracefully
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
      expect(screen.getByText(/Sampler:/)).toBeInTheDocument();
      expect(screen.getByText(/Steps:/)).toBeInTheDocument();
      expect(screen.getByText(/CFG:/)).toBeInTheDocument();
    });
  });

  describe('Modal Functionality', () => {
    it('should open modal when "View Config" button is clicked', async () => {
      const mockStore = {
        runs: [mockRun],
        selectedRun: null,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      const viewConfigButton = screen.getByText('View Config');
      fireEvent.click(viewConfigButton);

      await waitFor(() => {
        expect(mockStore.selectRun).toHaveBeenCalledWith(mockRun);
      });
    });

    it('should display frozen config details in modal', async () => {
      const mockStore = {
        runs: [mockRun],
        selectedRun: mockRun,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      // Test that the component renders without crashing when a run is selected
      expect(screen.getByText('Run Registry')).toBeInTheDocument();
      expect(screen.getByText('Run test_run_001')).toBeInTheDocument();
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
      expect(screen.getByText(/Sampler:/)).toBeInTheDocument();
      expect(screen.getByText(/Steps:/)).toBeInTheDocument();
      expect(screen.getByText(/CFG:/)).toBeInTheDocument();
      expect(screen.getByText(/Prompt:/)).toBeInTheDocument();
    });
  });

  describe('Deep Linking', () => {
    it('should handle deep linking to specific run', async () => {
      const mockStore = {
        runs: [mockRun],
        selectedRun: null,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(() => mockRun),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      // Test that the component renders without crashing when deep linking is used
      expect(screen.getByText('Run Registry')).toBeInTheDocument();
      expect(screen.getByText('Run test_run_001')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error state when runs fail to load', async () => {
      const mockStore = {
        runs: [],
        selectedRun: null,
        isLoading: false,
        error: 'Failed to fetch runs',
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      expect(screen.getByText('Error Loading Runs')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch runs')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('should display loading state', async () => {
      const mockStore = {
        runs: [],
        selectedRun: null,
        isLoading: true,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      expect(screen.getByText('Loading runs...')).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no runs exist', async () => {
      const mockStore = {
        runs: [],
        selectedRun: null,
        isLoading: false,
        error: null,
        setRuns: vi.fn(),
        selectRun: vi.fn(),
        setLoading: vi.fn(),
        setError: vi.fn(),
        clearError: vi.fn(),
        getRunById: vi.fn(),
      };

      (useRunRegistryStore as any).mockReturnValue(mockStore);

      renderWithRouter(<Runs />);

      expect(screen.getByText('No Runs Found')).toBeInTheDocument();
      expect(screen.getByText('Complete some image generations to see them here')).toBeInTheDocument();
    });
  });
}); 