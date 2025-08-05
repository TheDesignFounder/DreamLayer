import { useEffect, useState } from 'react';
import useSWR, { mutate } from 'swr';
import { fetcher } from '../utils/api';
import { ProgressData } from '../types/queue';

export const ProgressBar = () => {
  const [isVisible, setIsVisible] = useState(false);
  
  const { data, error } = useSWR<ProgressData>(
    '/queue/progress',
    fetcher,
    {
      refreshInterval: 500, // Poll every 500ms
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  // Clear cache on component mount to handle page refreshes
  useEffect(() => {
    // Clear any stale cache data when component mounts
    mutate('/queue/progress', undefined, false);
  }, []);

  useEffect(() => {
    if (error) {
      setIsVisible(false);
      return;
    }

    if (data) {
      const isIdle = data.status === 'idle';
      const isComplete = data.status === 'complete';
      const hasTasks = data.queue_running.length > 0 || data.queue_pending.length > 0;

      // Hide if idle, or if no tasks and complete
      if (isIdle || (!hasTasks && isComplete)) {
        setIsVisible(false);
        setTimeout(() => {
          mutate('/queue/progress', undefined, false);
        }, 1000);
        return;
      }

      // Show the bar if there are tasks, even if percent is 0
      setIsVisible(hasTasks);
    }
  }, [data, error]);

  // Clear cache on component unmount
  useEffect(() => {
    return () => {
      mutate('/queue/progress', undefined, false);
    };
  }, []);

  if (!isVisible) {
    return null;
  }

  const progress = data?.percent || 0;

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <div 
        className="h-1 bg-gray-200"
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Queue progress"
      >
        <div
          className="h-full bg-blue-500 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
          data-testid="progress-bar-inner"
        />
      </div>
    </div>
  );
}; 