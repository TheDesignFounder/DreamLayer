import { useState, useCallback, useRef, useEffect } from 'react';

interface ProgressState {
  isGenerating: boolean;
  progress: number;
  status: string;
  eta?: string;
  currentStep?: number;
  totalSteps?: number;
  startTime?: number;
}

interface UseProgressTrackingReturn {
  progressState: ProgressState;
  startProgress: () => void;
  updateProgress: (progress: number, status?: string, currentStep?: number, totalSteps?: number) => void;
  completeProgress: () => void;
  resetProgress: () => void;
}

export const useProgressTracking = (): UseProgressTrackingReturn => {
  const [progressState, setProgressState] = useState<ProgressState>({
    isGenerating: false,
    progress: 0,
    status: 'Ready',
  });

  const intervalRef = useRef<NodeJS.Timeout>();
  const startTimeRef = useRef<number>();

  const calculateETA = useCallback((progress: number, startTime: number) => {
    if (progress <= 0) return undefined;
    
    const elapsed = Date.now() - startTime;
    const totalEstimated = (elapsed / progress) * 100;
    const remaining = totalEstimated - elapsed;
    
    if (remaining <= 0) return '< 1s';
    
    const seconds = Math.ceil(remaining / 1000);
    if (seconds < 60) return `${seconds}s`;
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  }, []);

  const startProgress = useCallback(() => {
    const startTime = Date.now();
    startTimeRef.current = startTime;
    
    setProgressState({
      isGenerating: true,
      progress: 0,
      status: 'Initializing generation...',
      startTime,
    });

    // Simulate initial progress
    let currentProgress = 0;
    intervalRef.current = setInterval(() => {
      currentProgress += Math.random() * 3;
      if (currentProgress < 10) {
        setProgressState(prev => ({
          ...prev,
          progress: currentProgress,
          status: 'Setting up pipeline...',
          eta: calculateETA(currentProgress, startTime),
        }));
      } else {
        clearInterval(intervalRef.current);
        setProgressState(prev => ({
          ...prev,
          progress: 10,
          status: 'Processing...',
          eta: calculateETA(10, startTime),
        }));
      }
    }, 200);
  }, [calculateETA]);

  const updateProgress = useCallback((
    progress: number, 
    status?: string, 
    currentStep?: number, 
    totalSteps?: number
  ) => {
    setProgressState(prev => ({
      ...prev,
      progress: Math.min(progress, 100),
      status: status || prev.status,
      currentStep,
      totalSteps,
      eta: prev.startTime ? calculateETA(progress, prev.startTime) : undefined,
    }));
  }, [calculateETA]);

  const completeProgress = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    setProgressState(prev => ({
      ...prev,
      progress: 100,
      status: 'Generation complete!',
      eta: undefined,
    }));

    // Reset after delay
    setTimeout(() => {
      setProgressState({
        isGenerating: false,
        progress: 0,
        status: 'Ready',
      });
    }, 2000);
  }, []);

  const resetProgress = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    setProgressState({
      isGenerating: false,
      progress: 0,
      status: 'Ready',
    });
  }, []);

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    progressState,
    startProgress,
    updateProgress,
    completeProgress,
    resetProgress,
  };
};