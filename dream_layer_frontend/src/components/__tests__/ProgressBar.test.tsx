import { render, screen, waitFor } from '@testing-library/react';
import { SWRConfig } from 'swr';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { ProgressBar } from '../ProgressBar';

// Mock the progress endpoint
const server = setupServer(
  http.get('/queue/progress', () => {
    return HttpResponse.json({
      percent: 75,
      status: 'running',
      queue_running: [{ id: '1', prompt: {} }],
      queue_pending: []
    });
  })
);

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
afterAll(() => server.close());

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  // Use a new cache for each test
  const cache = new Map();
  return (
    <SWRConfig value={{ fetcher: (url: string) => fetch(url).then(res => res.json()), provider: () => cache }}>
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

    // Wait for the progress bar to appear
    await waitFor(() => {
      const progressBar = screen.getByRole('progressbar', { hidden: true });
      expect(progressBar).toBeInTheDocument();
    });
  });

  it('should hide progress bar when no tasks in queue', async () => {
    // Mock empty queue
    server.use(
      http.get('/queue/progress', () => {
        return HttpResponse.json({
          percent: 100,
          status: 'complete',
          queue_running: [],
          queue_pending: []
        });
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
            queue_running: [{ id: '1', prompt: {} }],
            queue_pending: []
          });
        } else {
          return HttpResponse.json({
            percent: 75,
            status: 'running',
            queue_running: [{ id: '1', prompt: {} }],
            queue_pending: []
          });
        }
      })
    );

    render(
      <TestWrapper>
        <ProgressBar />
      </TestWrapper>
    );

    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByTestId('progress-bar-inner')).toHaveStyle({ width: '25%' });
    });

    // Wait for the progress to update (SWR will poll every 500ms)
    await new Promise(res => setTimeout(res, 600));
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

    // Wait and check that no progress bar is rendered on error
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });
}); 