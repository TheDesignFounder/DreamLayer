/**
 * Unit tests for Run Registry UI components
 * Tests rendering, modal functionality, deep linking, and error handling
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { RunRegistry } from './RunRegistry';
import { runService } from '../services/runService';
import { toast } from 'sonner';

// Mock the services and external dependencies
jest.mock('../services/runService');
jest.mock('sonner');

// Mock useParams for deep linking tests
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: null }),
  useNavigate: () => mockNavigate,
}));

describe('RunRegistry Component', () => {
  const mockRuns = [
    {
      id: 'run-1',
      timestamp: '2024-01-01T10:00:00',
      prompt: 'A beautiful landscape with mountains',
      model: 'sdxl-base-1.0',
      generation_type: 'txt2img',
    },
    {
      id: 'run-2',
      timestamp: '2024-01-01T11:00:00',
      prompt: 'Portrait of a person',
      model: 'sdxl-turbo',
      generation_type: 'img2img',
    },
  ];

  const mockFullRun = {
    id: 'run-1',
    timestamp: '2024-01-01T10:00:00',
    prompt: 'A beautiful landscape with mountains',
    negative_prompt: 'ugly, blurry',
    model: 'sdxl-base-1.0',
    vae: 'sdxl-vae',
    loras: [
      { name: 'style-lora', strength: 0.8 },
      { name: 'detail-lora', strength: 0.5 },
    ],
    controlnet: {
      enabled: true,
      model: 'canny',
      weight: 0.7,
    },
    seed: 42,
    sampler: 'euler_a',
    steps: 20,
    cfg_scale: 7.5,
    generation_type: 'txt2img',
    workflow: { nodes: [] },
    workflow_version: '1.0.0',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (runService.fetchRuns as jest.Mock).mockResolvedValue(mockRuns);
    (runService.fetchRunById as jest.Mock).mockResolvedValue(mockFullRun);
  });

  describe('Required Keys Validation', () => {
    it('should display all required keys in the modal', async () => {
      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      // Wait for runs to load
      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      // Click on a run to open modal
      fireEvent.click(screen.getByText('Run-1'));

      // Wait for modal to open and data to load
      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Check all required keys are displayed
      const requiredKeys = [
        'Run ID',
        'Timestamp',
        'Prompt',
        'Negative Prompt',
        'Model',
        'VAE',
        'LoRAs',
        'ControlNet',
        'Seed',
        'Sampler',
        'Steps',
        'CFG Scale',
        'Generation Type',
        'Workflow Version',
      ];

      for (const key of requiredKeys) {
        expect(screen.getByText(new RegExp(key, 'i'))).toBeInTheDocument();
      }

      // Verify values are displayed
      expect(screen.getByText('run-1')).toBeInTheDocument();
      expect(screen.getByText('sdxl-base-1.0')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('euler_a')).toBeInTheDocument();
      expect(screen.getByText('20')).toBeInTheDocument();
      expect(screen.getByText('7.5')).toBeInTheDocument();
    });

    it('should assert that required keys exist in the run data', async () => {
      const requiredKeys = [
        'id',
        'timestamp',
        'prompt',
        'negative_prompt',
        'model',
        'vae',
        'loras',
        'controlnet',
        'seed',
        'sampler',
        'steps',
        'cfg_scale',
        'generation_type',
        'workflow',
        'workflow_version',
      ];

      // Verify the mock data has all required keys
      for (const key of requiredKeys) {
        expect(mockFullRun).toHaveProperty(key);
      }
    });
  });

  describe('Empty Values Handling', () => {
    it('should handle empty string values gracefully', async () => {
      const runWithEmptyValues = {
        ...mockFullRun,
        prompt: '',
        negative_prompt: '',
        model: '',
      };

      (runService.fetchRunById as jest.Mock).mockResolvedValue(runWithEmptyValues);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Should display "N/A" or empty values without crashing
      expect(screen.queryByText('N/A')).toBeInTheDocument();
    });

    it('should handle null values without crashing', async () => {
      const runWithNullValues = {
        ...mockFullRun,
        negative_prompt: null,
        vae: null,
        loras: null,
        controlnet: null,
      };

      (runService.fetchRunById as jest.Mock).mockResolvedValue(runWithNullValues);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Component should render without errors
      expect(screen.getByText('Run Details')).toBeInTheDocument();
    });

    it('should handle undefined values gracefully', async () => {
      const runWithUndefinedValues = {
        id: 'run-1',
        timestamp: '2024-01-01T10:00:00',
        prompt: 'Test prompt',
        generation_type: 'txt2img',
        // Other fields are undefined
      };

      (runService.fetchRunById as jest.Mock).mockResolvedValue(runWithUndefinedValues);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Should not crash and display appropriate defaults
      expect(screen.getByText('Run Details')).toBeInTheDocument();
    });

    it('should handle empty arrays gracefully', async () => {
      const runWithEmptyArrays = {
        ...mockFullRun,
        loras: [],
      };

      (runService.fetchRunById as jest.Mock).mockResolvedValue(runWithEmptyArrays);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Should display "None" or similar for empty arrays
      expect(screen.getByText(/None|N\/A/i)).toBeInTheDocument();
    });
  });

  describe('Deep Linking', () => {
    it('should open modal when accessing /runs/:id directly', async () => {
      // Mock useParams to return a specific ID
      jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ id: 'run-1' });

      render(
        <MemoryRouter initialEntries={['/runs/run-1']}>
          <RunRegistry />
        </MemoryRouter>
      );

      // Modal should open automatically
      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      expect(runService.fetchRunById).toHaveBeenCalledWith('run-1');
    });

    it('should handle invalid run ID in URL', async () => {
      jest.spyOn(require('react-router-dom'), 'useParams').mockReturnValue({ id: 'invalid-id' });
      (runService.fetchRunById as jest.Mock).mockRejectedValue(new Error('Run not found'));

      render(
        <MemoryRouter initialEntries={['/runs/invalid-id']}>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Failed to load run'));
      });
    });
  });

  describe('List View', () => {
    it('should display list of runs', async () => {
      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
        expect(screen.getByText('Run-2')).toBeInTheDocument();
      });

      // Check that run details are displayed
      expect(screen.getByText('sdxl-base-1.0')).toBeInTheDocument();
      expect(screen.getByText('sdxl-turbo')).toBeInTheDocument();
      expect(screen.getByText('txt2img')).toBeInTheDocument();
      expect(screen.getByText('img2img')).toBeInTheDocument();
    });

    it('should show loading state while fetching runs', () => {
      (runService.fetchRuns as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      // Should show loading skeletons
      expect(screen.getAllByTestId('skeleton-loader')).toHaveLength(6);
    });

    it('should show empty state when no runs exist', async () => {
      (runService.fetchRuns as jest.Mock).mockResolvedValue([]);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText(/No runs found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Modal Functionality', () => {
    it('should open modal when clicking on a run', async () => {
      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });
    });

    it('should close modal when clicking close button', async () => {
      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Click close button
      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText('Run Details')).not.toBeInTheDocument();
      });
    });

    it('should copy config to clipboard', async () => {
      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockResolvedValue(undefined),
        },
      });

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(screen.getByText('Run Details')).toBeInTheDocument();
      });

      // Click copy button
      const copyButton = screen.getByRole('button', { name: /copy/i });
      fireEvent.click(copyButton);

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(toast.success).toHaveBeenCalledWith('Configuration copied to clipboard');
    });
  });

  describe('Delete Functionality', () => {
    it('should delete a run with confirmation', async () => {
      (runService.deleteRun as jest.Mock).mockResolvedValue(undefined);
      window.confirm = jest.fn().mockReturnValue(true);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      // Find and click delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining('delete this run'));

      await waitFor(() => {
        expect(runService.deleteRun).toHaveBeenCalledWith('run-1');
        expect(toast.success).toHaveBeenCalledWith('Run deleted successfully');
      });
    });

    it('should not delete when confirmation is cancelled', async () => {
      window.confirm = jest.fn().mockReturnValue(false);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      expect(runService.deleteRun).not.toHaveBeenCalled();
    });

    it('should handle delete errors gracefully', async () => {
      (runService.deleteRun as jest.Mock).mockRejectedValue(new Error('Delete failed'));
      window.confirm = jest.fn().mockReturnValue(true);

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Failed to delete'));
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error when fetching runs fails', async () => {
      (runService.fetchRuns as jest.Mock).mockRejectedValue(new Error('Network error'));

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Failed to load runs'));
      });
    });

    it('should display error when fetching run details fails', async () => {
      (runService.fetchRunById as jest.Mock).mockRejectedValue(new Error('Not found'));

      render(
        <MemoryRouter>
          <RunRegistry />
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Run-1')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Run-1'));

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(expect.stringContaining('Failed to load run'));
      });
    });
  });
});
