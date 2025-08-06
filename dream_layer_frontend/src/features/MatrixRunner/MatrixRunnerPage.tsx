import React, { useState, useEffect } from 'react';
import { useMatrixRunnerStore } from '@/stores/useMatrixRunnerStore';
import { ParameterRange } from '@/types/matrixRunner';
import { parseParameter, calculateTotalJobs, formatDuration } from '@/utils/matrixUtils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Grid3X3, 
  Settings,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import MatrixParameterInput from './MatrixParameterInput';
import MatrixProgressGrid from './MatrixProgressGrid';
import MatrixJobList from './MatrixJobList';

interface MatrixRunnerPageProps {
  selectedModel: string;
  onTabChange: (tabId: string) => void;
}

const MatrixRunnerPage: React.FC<MatrixRunnerPageProps> = ({ selectedModel, onTabChange }) => {
  const {
    parameters,
    baseSettings,
    jobs,
    isRunning,
    isPaused,
    totalJobs,
    completedJobs,
    failedJobs,
    pendingJobs,
    estimatedTimeRemaining,
    averageTimePerJob,
    showProgressGrid,
    autoBatch,
    setParameter,
    setBaseSettings,
    generateJobs,
    startMatrix,
    pauseMatrix,
    resumeMatrix,
    stopMatrix,
    clearJobs,
    toggleProgressGrid,
    toggleAutoBatch
  } = useMatrixRunnerStore();

  const [activeTab, setActiveTab] = useState<'parameters' | 'progress' | 'jobs'>('parameters');

  // Update model when selectedModel prop changes
  useEffect(() => {
    setBaseSettings({ model_name: selectedModel });
  }, [selectedModel, setBaseSettings]);

  const handleParameterChange = (param: keyof typeof parameters, value: string) => {
    if (!value.trim()) {
      // Remove parameter if empty
      const newParams = { ...parameters };
      delete newParams[param];
      // We need to update the store differently since we can't directly modify parameters
      // This is a limitation of the current store structure
      return;
    }

    try {
      const parsed = parseParameter(value);
      setParameter(param, parsed);
    } catch (error) {
      toast.error(`Invalid parameter format: ${error}`);
    }
  };

  const handleGenerateJobs = () => {
    if (!baseSettings.prompt.trim()) {
      toast.error('Please enter a prompt before generating jobs');
      return;
    }

    generateJobs();
    const total = calculateTotalJobs(parameters);
    toast.success(`Generated ${total} jobs`);
  };

  const handleStartMatrix = async () => {
    if (jobs.length === 0) {
      toast.error('No jobs to run. Please generate jobs first.');
      return;
    }

    try {
      await startMatrix();
      toast.success('Matrix generation started');
    } catch (error) {
      toast.error('Failed to start matrix generation');
    }
  };

  const handlePauseResume = () => {
    if (isPaused) {
      resumeMatrix();
      toast.success('Matrix generation resumed');
    } else {
      pauseMatrix();
      toast.success('Matrix generation paused');
    }
  };

  const handleStop = () => {
    stopMatrix();
    toast.success('Matrix generation stopped');
  };

  const handleClear = () => {
    clearJobs();
    toast.success('Jobs cleared');
  };

  const progressPercentage = totalJobs > 0 ? (completedJobs / totalJobs) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header with status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Matrix Runner</h2>
          <p className="text-muted-foreground">
            Generate multiple images with different parameter combinations
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isRunning && (
            <Badge variant="default" className="bg-green-500">
              <CheckCircle className="w-3 h-3 mr-1" />
              Running
            </Badge>
          )}
          {isPaused && (
            <Badge variant="secondary">
              <Pause className="w-3 h-3 mr-1" />
              Paused
            </Badge>
          )}
          {!isRunning && !isPaused && jobs.length > 0 && (
            <Badge variant="outline">
              <AlertCircle className="w-3 h-3 mr-1" />
              Ready
            </Badge>
          )}
        </div>
      </div>

      {/* Progress Overview */}
      {totalJobs > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5" />
              Progress Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span>Progress</span>
              <span>{completedJobs} / {totalJobs} jobs completed</span>
            </div>
            <Progress value={progressPercentage} className="w-full" />
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{completedJobs}</div>
                <div className="text-xs text-muted-foreground">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{failedJobs}</div>
                <div className="text-xs text-muted-foreground">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{pendingJobs}</div>
                <div className="text-xs text-muted-foreground">Pending</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {averageTimePerJob ? formatDuration(averageTimePerJob) : '--'}
                </div>
                <div className="text-xs text-muted-foreground">Avg Time</div>
              </div>
            </div>

            {estimatedTimeRemaining && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                Estimated time remaining: {formatDuration(estimatedTimeRemaining)}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 border-b">
        <button
          onClick={() => setActiveTab('parameters')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
            activeTab === 'parameters'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          Parameters
        </button>
        <button
          onClick={() => setActiveTab('progress')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
            activeTab === 'progress'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          Progress Grid
        </button>
        <button
          onClick={() => setActiveTab('jobs')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
            activeTab === 'jobs'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          Job List
        </button>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'parameters' && (
          <div className="space-y-6">
            {/* Base Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Base Settings</CardTitle>
                <CardDescription>
                  Common settings applied to all jobs in the matrix
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="prompt">Prompt</Label>
                    <Input
                      id="prompt"
                      value={baseSettings.prompt}
                      onChange={(e) => setBaseSettings({ prompt: e.target.value })}
                      placeholder="Enter your prompt..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="negative-prompt">Negative Prompt</Label>
                    <Input
                      id="negative-prompt"
                      value={baseSettings.negative_prompt}
                      onChange={(e) => setBaseSettings({ negative_prompt: e.target.value })}
                      placeholder="Enter negative prompt..."
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Matrix Parameters */}
            <Card>
              <CardHeader>
                <CardTitle>Matrix Parameters</CardTitle>
                <CardDescription>
                  Define ranges or lists for parameters to generate combinations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <MatrixParameterInput
                    label="Seeds"
                    value={parameters.seeds?.original || ''}
                    onChange={(value) => handleParameterChange('seeds', value)}
                    placeholder="1-5,10,15"
                    description="Range: 1-5 or list: 1,2,3,10"
                  />
                  <MatrixParameterInput
                    label="Samplers"
                    value={parameters.samplers?.original || ''}
                    onChange={(value) => handleParameterChange('samplers', value)}
                    placeholder="euler,dpm++,ddim"
                    description="Comma-separated sampler names"
                  />
                  <MatrixParameterInput
                    label="Steps"
                    value={parameters.steps?.original || ''}
                    onChange={(value) => handleParameterChange('steps', value)}
                    placeholder="20,30,40"
                    description="Range: 20-30 or list: 20,30,40"
                  />
                  <MatrixParameterInput
                    label="CFG Scale"
                    value={parameters.cfg_scale?.original || ''}
                    onChange={(value) => handleParameterChange('cfg_scale', value)}
                    placeholder="7,8,9"
                    description="Range: 7-9 or list: 7,8,9"
                  />
                  <MatrixParameterInput
                    label="Width"
                    value={parameters.width?.original || ''}
                    onChange={(value) => handleParameterChange('width', value)}
                    placeholder="512,768"
                    description="Range: 512-768 or list: 512,768"
                  />
                  <MatrixParameterInput
                    label="Height"
                    value={parameters.height?.original || ''}
                    onChange={(value) => handleParameterChange('height', value)}
                    placeholder="512,768"
                    description="Range: 512-768 or list: 512,768"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Options */}
            <Card>
              <CardHeader>
                <CardTitle>Options</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Auto Batching</Label>
                    <p className="text-sm text-muted-foreground">
                      Group similar jobs to minimize GPU context switches
                    </p>
                  </div>
                  <Switch
                    checked={autoBatch}
                    onCheckedChange={toggleAutoBatch}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Show Progress Grid</Label>
                    <p className="text-sm text-muted-foreground">
                      Display real-time progress visualization
                    </p>
                  </div>
                  <Switch
                    checked={showProgressGrid}
                    onCheckedChange={toggleProgressGrid}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleGenerateJobs} disabled={isRunning}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Generate Jobs ({calculateTotalJobs(parameters)})
              </Button>
              <Button 
                onClick={handleStartMatrix} 
                disabled={jobs.length === 0 || isRunning}
                variant="default"
              >
                <Play className="w-4 h-4 mr-2" />
                Start Matrix
              </Button>
              <Button 
                onClick={handlePauseResume} 
                disabled={jobs.length === 0 || (!isRunning && !isPaused)}
                variant="secondary"
              >
                {isPaused ? (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Resume
                  </>
                ) : (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </>
                )}
              </Button>
              <Button 
                onClick={handleStop} 
                disabled={!isRunning && !isPaused}
                variant="destructive"
              >
                <Square className="w-4 h-4 mr-2" />
                Stop
              </Button>
              <Button 
                onClick={handleClear} 
                disabled={jobs.length === 0 || isRunning}
                variant="outline"
              >
                <XCircle className="w-4 h-4 mr-2" />
                Clear Jobs
              </Button>
            </div>
          </div>
        )}

        {activeTab === 'progress' && (
          <MatrixProgressGrid />
        )}

        {activeTab === 'jobs' && (
          <MatrixJobList />
        )}
      </div>
    </div>
  );
};

export default MatrixRunnerPage; 