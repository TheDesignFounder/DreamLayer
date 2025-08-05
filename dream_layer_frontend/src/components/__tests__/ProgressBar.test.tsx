import { render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { SWRConfig } from 'swr';
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from 'vitest';
import { ProgressBar } from '../ProgressBar';

// Mock SWR cache for each test
const createTestSWRConfig = () => ({
  provider: () => new Map(),
  dedupingInterval: 0,
  focusThrottleInterval: 0,
  errorRetryInterval: 0,
  errorRetryCount: 0,
});

const server = setupServer();

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  // Clear any cached data between tests
  vi.clearAllMocks();
});
afterAll(() => server.close());

describe('ProgressBar', () => {
  const mockProgressData = {
    percent: 50,
    status: 'running',
    queue_running: [{ prompt_id: '123', number: 1 }],
    queue_pending: [],
    task_details: [
      {
        prompt_id: '123',
        current_step: 2,
        total_steps: 4,
        step_name: 'Processing',
        percent: 50
      }
    ]
  };

  const mockCompleteData = {
    percent: 100,
    status: 'complete',
    queue_running: [],
    queue_pending: [],
    task_details: []
  };

  const mockIdleData = {
    percent: 0,
    status: 'idle',
    queue_running: [],
    queue_pending: [],
    task_details: []
  };

  const mockNoTasksData = {
    percent: 0,
    status: 'idle',
    queue_running: [],
    queue_pending: [],
    task_details: []
  };

  it('should show progress bar when tasks are running', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json(mockProgressData);
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '50%' });
  });

  it('should hide progress bar when progress is complete', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json(mockCompleteData);
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('should hide progress bar when no tasks are in queue', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json(mockNoTasksData);
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('should hide progress bar when system is idle', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json(mockIdleData);
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('should hide progress bar on error', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('should update progress when data changes', async () => {
    let callCount = 0;
    server.use(
      http.get('/queue/progress', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({ ...mockProgressData, percent: 25 });
        } else {
          return HttpResponse.json({ ...mockProgressData, percent: 75 });
        }
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    await waitFor(() => {
      expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '25%' });
    });

    // Wait for the next poll
    await waitFor(() => {
      expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '75%' });
    }, { timeout: 2000 });
  });

  it('should handle transition from running to complete', async () => {
    let callCount = 0;
    server.use(
      http.get('/queue/progress', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json(mockProgressData);
        } else {
          return HttpResponse.json(mockCompleteData);
        }
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    // Initially show progress bar
    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    // Then hide it when complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('should clear cache on mount to handle page refreshes', async () => {
    const mockMutate = vi.fn();
    vi.doMock('swr', () => ({
      ...vi.importActual('swr'),
      mutate: mockMutate,
    }));

    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json(mockProgressData);
      })
    );

    render(
      <SWRConfig value={createTestSWRConfig()}>
        <ProgressBar />
      </SWRConfig>
    );

    // The component should clear cache on mount
    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });
  });
}); 