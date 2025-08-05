import React from "react";
import useSWR from "swr";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ProgressData {
  percent: number;
  status?: string;
  message?: string;
}

const fetcher = async (url: string): Promise<ProgressData> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch progress");
  }
  return response.json();
};

interface ProgressBarProps {
  className?: string;
  onComplete?: () => void;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ className, onComplete }) => {
  const { data, error, isLoading } = useSWR<ProgressData>(
    "/queue/progress",
    fetcher,
    {
      refreshInterval: 500,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      shouldRetryOnError: false,
    }
  );

  const progress = data?.percent || 0;
  const isComplete = progress >= 100;
  const shouldShow = !isLoading && !error && progress > 0 && !isComplete;

  React.useEffect(() => {
    if (isComplete && onComplete) {
      const timer = setTimeout(() => {
        onComplete();
      }, 1000); // Show complete state for 1 second before hiding

      return () => clearTimeout(timer);
    }
  }, [isComplete, onComplete]);

  if (!shouldShow && !isComplete) {
    return null;
  }

  return (
    <div
      className={cn(
        "fixed top-0 left-0 right-0 z-50 h-1 bg-background/80 backdrop-blur-sm transition-opacity duration-300",
        isComplete ? "opacity-0" : "opacity-100",
        className
      )}
    >
      <Progress value={progress} className="h-full rounded-none border-none" />
      {data?.message && (
        <div className="absolute top-1 left-4 text-xs text-muted-foreground">
          {data.message}
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
