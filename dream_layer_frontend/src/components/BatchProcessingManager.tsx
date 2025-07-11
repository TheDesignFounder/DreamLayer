import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useBatchProcessingStore } from '@/stores/useBatchProcessingStore';
import { BatchJob } from '@/types/batchProcessing';
import { 
  Play, 
  Pause, 
  Square, 
  Trash2, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Plus,
  Settings,
  BarChart3,
  Image as ImageIcon
} from 'lucide-react';

interface BatchJobCardProps {
  job: BatchJob;
  onCancel: (id: string) => void;
  onRemove: (id: string) => void;
}

const BatchJobCard: React.FC<BatchJobCardProps> = ({ job, onCancel, onRemove }) => {
  const getStatusIcon = (status: BatchJob['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'running':
        return <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'cancelled':
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: BatchJob['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  const getProcessingTime = () => {
    if (job.startedAt && job.completedAt) {
      const duration = job.completedAt - job.startedAt;
      return `${Math.round(duration / 1000)}s`;
    }
    return 'N/A';
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon(job.status)}
            <CardTitle className="text-sm">{job.name}</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={`text-xs ${getStatusColor(job.status)}`}>
              {job.status}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {job.type}
            </Badge>
          </div>
        </div>
        <CardDescription className="text-xs">
          Created: {formatTime(job.createdAt)}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Progress */}
        {job.status === 'running' && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <Progress value={job.progress} className="h-2" />
          </div>
        )}
        
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-muted-foreground">Images:</span>
            <span className="ml-1 font-medium">
              {job.completedImages}/{job.totalImages}
            </span>
          </div>
          <div>
            <span className="text-muted-foreground">Time:</span>
            <span className="ml-1 font-medium">{getProcessingTime()}</span>
          </div>
        </div>
        
        {/* Error message */}
        {job.error && (
          <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
            Error: {job.error}
          </div>
        )}
        
        {/* Actions */}
        <div className="flex justify-end gap-2">
          {(job.status === 'pending' || job.status === 'running') && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onCancel(job.id)}
            >
              Cancel
            </Button>
          )}
          {job.status !== 'running' && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => onRemove(job.id)}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const BatchProcessingManager: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  const {
    jobs,
    queue,
    isProcessing,
    currentJob,
    startProcessing,
    stopProcessing,
    pauseProcessing,
    resumeProcessing,
    cancelJob,
    removeJob,
    clearCompletedJobs,
    clearAllJobs,
    getStats
  } = useBatchProcessingStore();

  const stats = getStats();
  const pendingJobs = jobs.filter(job => job.status === 'pending');
  const runningJobs = jobs.filter(job => job.status === 'running');
  const completedJobs = jobs.filter(job => job.status === 'completed');
  const failedJobs = jobs.filter(job => job.status === 'failed');

  const handleProcessingControl = () => {
    if (isProcessing) {
      pauseProcessing();
    } else if (queue.length > 0 || pendingJobs.length > 0) {
      if (queue.length === 0 && pendingJobs.length > 0) {
        // Add pending jobs to queue
        pendingJobs.forEach(job => {
          const { addToQueue } = useBatchProcessingStore.getState();
          addToQueue(job);
        });
      }
      resumeProcessing();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="relative">
          <BarChart3 className="h-4 w-4 mr-2" />
          Batch Manager
          {(queue.length > 0 || isProcessing) && (
            <Badge className="ml-2 h-5 w-5 p-0 text-xs">
              {queue.length + (currentJob ? 1 : 0)}
            </Badge>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Batch Processing Manager</span>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant={isProcessing ? "destructive" : "default"}
                onClick={handleProcessingControl}
                disabled={queue.length === 0 && pendingJobs.length === 0}
              >
                {isProcessing ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Start
                  </>
                )}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={stopProcessing}
                disabled={!isProcessing}
              >
                <Square className="h-4 w-4 mr-2" />
                Stop
              </Button>
            </div>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Stats Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Total Jobs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalJobs}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Queue Size</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.queueSize}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{stats.completedJobs}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Total Images</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalImages}</div>
              </CardContent>
            </Card>
          </div>
          
          {/* Current Job */}
          {currentJob && (
            <div>
              <h3 className="text-sm font-medium mb-2">Currently Processing</h3>
              <BatchJobCard
                job={currentJob}
                onCancel={cancelJob}
                onRemove={removeJob}
              />
            </div>
          )}
          
          {/* Job Lists */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">Job History</h3>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={clearCompletedJobs}
                  disabled={completedJobs.length === 0}
                >
                  Clear Completed
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={clearAllJobs}
                  disabled={jobs.length === 0}
                >
                  Clear All
                </Button>
              </div>
            </div>
            
            <ScrollArea className="h-[400px]">
              {jobs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No batch jobs yet</p>
                  <p className="text-sm">Create batch jobs to see them here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Running Jobs */}
                  {runningJobs.length > 0 && (
                    <div>
                      <h4 className="text-xs font-medium text-blue-600 mb-2">Running</h4>
                      <div className="space-y-2">
                        {runningJobs.map(job => (
                          <BatchJobCard
                            key={job.id}
                            job={job}
                            onCancel={cancelJob}
                            onRemove={removeJob}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Pending Jobs */}
                  {pendingJobs.length > 0 && (
                    <div>
                      <h4 className="text-xs font-medium text-yellow-600 mb-2">Pending</h4>
                      <div className="space-y-2">
                        {pendingJobs.map(job => (
                          <BatchJobCard
                            key={job.id}
                            job={job}
                            onCancel={cancelJob}
                            onRemove={removeJob}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Completed Jobs */}
                  {completedJobs.length > 0 && (
                    <div>
                      <h4 className="text-xs font-medium text-green-600 mb-2">Completed</h4>
                      <div className="space-y-2">
                        {completedJobs.slice(0, 5).map(job => (
                          <BatchJobCard
                            key={job.id}
                            job={job}
                            onCancel={cancelJob}
                            onRemove={removeJob}
                          />
                        ))}
                        {completedJobs.length > 5 && (
                          <p className="text-xs text-muted-foreground text-center">
                            +{completedJobs.length - 5} more completed jobs
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Failed Jobs */}
                  {failedJobs.length > 0 && (
                    <div>
                      <h4 className="text-xs font-medium text-red-600 mb-2">Failed</h4>
                      <div className="space-y-2">
                        {failedJobs.map(job => (
                          <BatchJobCard
                            key={job.id}
                            job={job}
                            onCancel={cancelJob}
                            onRemove={removeJob}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BatchProcessingManager;