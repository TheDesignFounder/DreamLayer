import { render, screen, waitFor } from '@testing-library/react';
import { SWRConfig } from 'swr';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { ProgressBar } from '../ProgressBar';
import { fetcher } from '../../utils/api';
import { ProgressData } from '../../types/queue';

// Mock the progress endpoint
const server = setupServer(
  http.get('/queue/progress', () => {
    return HttpResponse.json({
      percent: 75,
      status: 'running',
      queue_running: [{ id: '1', prompt: {}, number: 1, prompt_id: 'test-1' }],
      queue_pending: []
    } as ProgressData);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  // Use a new cache for each test
  const cache = new Map();
  return (
    <SWRConfig value={{ fetcher, provider: () => cache }}>
      {children}
    </SWRConfig>
  );
};

describe('ProgressBar', () => {
  it('should show progress bar when there are tasks in queue', async () => {
    render(
      <TestWrapper>
        <ProgressBar />
      </TestWrapper>
    );
    await waitFor(() => {
      const progressBar = screen.getByRole('progressbar', { hidden: true });
      expect(progressBar).toBeInTheDocument();
    });
  });

  it('should hide progress bar when no tasks in queue', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json({
          percent: 100,
          status: 'complete',
          queue_running: [],
          queue_pending: []
        } as ProgressData);
      })
    );
    render(
      <TestWrapper>
        <ProgressBar />
      </TestWrapper>
    );
    // Wait for the bar to disappear
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('should update progress when endpoint returns different values', async () => {
    let callCount = 0;
    server.use(
      http.get('/queue/progress', () => {
        callCount++;
        if (callCount === 1) {
          return HttpResponse.json({
            percent: 25,
            status: 'running',
            queue_running: [{ id: '1', prompt: {}, number: 1, prompt_id: 'test-1' }],
            queue_pending: []
          } as ProgressData);
        } else {
          return HttpResponse.json({
            percent: 75,
            status: 'running',
            queue_running: [{ id: '1', prompt: {}, number: 1, prompt_id: 'test-1' }],
            queue_pending: []
          } as ProgressData);
        }
      })
    );
    render(
      <TestWrapper>
        <ProgressBar />
      </TestWrapper>
    );
    
    // Wait for initial render with 25% progress
    await waitFor(() => {
      expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '25%' });
    });
    
    // Wait for the progress to update to 75% (SWR will poll every 500ms)
    await waitFor(() => {
      expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '75%' });
    }, { timeout: 2000 });
  });

  it('should handle API errors gracefully', async () => {
    server.use(
      http.get('/queue/progress', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );
    render(
      <TestWrapper>
        <ProgressBar />
      </TestWrapper>
    );
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });
}); 