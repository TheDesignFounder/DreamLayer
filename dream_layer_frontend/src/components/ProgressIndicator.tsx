import React from 'react';
import { Progress } from '@/components/ui/progress';

interface ProgressIndicatorProps {
  isGenerating: boolean;
  progress?: number;
  status?: string;
  eta?: string;
  currentStep?: number;
  totalSteps?: number;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  isGenerating,
  progress = 0,
  status = 'Initializing...',
  eta,
  currentStep,
  totalSteps
}) => {
  if (!isGenerating) return null;

  const getProgressColor = () => {
    if (progress < 25) return 'bg-red-500';
    if (progress < 50) return 'bg-orange-500';
    if (progress < 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="w-full space-y-3 p-4 border rounded-lg bg-muted/30">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
          <span className="text-sm font-medium">Generating Image</span>
        </div>
        {eta && (
          <span className="text-xs text-muted-foreground">
            ETA: {eta}
          </span>
        )}
      </div>
      
      <Progress 
        value={progress} 
        className="w-full h-2"
      />
      
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>{status}</span>
        <div className="flex items-center space-x-2">
          {currentStep && totalSteps && (
            <span>Step {currentStep}/{totalSteps}</span>
          )}
          <span>{Math.round(progress)}%</span>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;