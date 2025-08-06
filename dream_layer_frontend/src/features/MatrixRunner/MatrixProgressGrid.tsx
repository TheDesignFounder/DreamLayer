import React from 'react';
import { useMatrixRunnerStore } from '@/stores/useMatrixRunnerStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Play,
  AlertCircle
} from 'lucide-react';

const MatrixProgressGrid: React.FC = () => {
  const { jobs, parameters } = useMatrixRunnerStore();

  if (jobs.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center text-muted-foreground">
            <AlertCircle className="w-12 h-12 mx-auto mb-4" />
            <p>No jobs generated yet. Go to Parameters tab to create jobs.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Group jobs by primary parameters for grid display
  const getGridDimensions = () => {
    const seeds = parameters.seeds?.values.length || 1;
    const samplers = parameters.samplers?.values.length || 1;
    const steps = parameters.steps?.values.length || 1;
    const cfgScales = parameters.cfg_scale?.values.length || 1;

    // Determine grid layout based on parameter combinations
    if (seeds > 1 && samplers > 1) {
      return { rows: seeds, cols: samplers, xAxis: 'samplers', yAxis: 'seeds' };
    } else if (steps > 1 && cfgScales > 1) {
      return { rows: steps, cols: cfgScales, xAxis: 'cfg_scale', yAxis: 'steps' };
    } else if (seeds > 1) {
      return { rows: Math.ceil(Math.sqrt(seeds)), cols: Math.ceil(seeds / Math.ceil(Math.sqrt(seeds))), xAxis: 'index', yAxis: 'seeds' };
    } else {
      return { rows: Math.ceil(Math.sqrt(jobs.length)), cols: Math.ceil(jobs.length / Math.ceil(Math.sqrt(jobs.length))), xAxis: 'index', yAxis: 'index' };
    }
  };

  const { rows, cols, xAxis, yAxis } = getGridDimensions();

  const getJobStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <Play className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'paused':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 border-green-200';
      case 'failed':
        return 'bg-red-100 border-red-200';
      case 'running':
        return 'bg-blue-100 border-blue-200';
      case 'paused':
        return 'bg-yellow-100 border-yellow-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const renderGridCell = (rowIndex: number, colIndex: number) => {
    const jobIndex = rowIndex * cols + colIndex;
    const job = jobs[jobIndex];

    if (!job) {
      return (
        <div key={`empty-${rowIndex}-${colIndex}`} className="w-16 h-16 border border-dashed border-gray-300 rounded-lg flex items-center justify-center">
          <span className="text-xs text-gray-400">-</span>
        </div>
      );
    }

    const getJobLabel = () => {
      if (xAxis === 'samplers' && yAxis === 'seeds') {
        return `${job.parameters.sampler_name}\n${job.parameters.seed}`;
      } else if (xAxis === 'cfg_scale' && yAxis === 'steps') {
        return `${job.parameters.cfg_scale}\n${job.parameters.steps}`;
      } else {
        return `Job ${jobIndex + 1}`;
      }
    };

    return (
      <div
        key={job.id}
        className={`w-16 h-16 border rounded-lg flex flex-col items-center justify-center p-1 cursor-pointer hover:shadow-md transition-all ${getJobStatusColor(job.status)}`}
        title={`${job.parameters.sampler_name} - ${job.parameters.steps} steps - CFG ${job.parameters.cfg_scale} - Seed ${job.parameters.seed}`}
      >
        {getJobStatusIcon(job.status)}
        <span className="text-xs text-center mt-1 leading-tight">
          {getJobLabel()}
        </span>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500 animate-pulse" />
            Live Progress Grid
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Legend */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Completed</span>
              </div>
              <div className="flex items-center gap-2">
                <Play className="w-4 h-4 text-blue-500" />
                <span>Running</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-500" />
                <span>Failed</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span>Pending</span>
              </div>
            </div>

            {/* Grid */}
            <div className="overflow-auto">
              <div 
                className="grid gap-2"
                style={{
                  gridTemplateColumns: `repeat(${cols}, 4rem)`,
                  gridTemplateRows: `repeat(${rows}, 4rem)`
                }}
              >
                {Array.from({ length: rows }, (_, rowIndex) =>
                  Array.from({ length: cols }, (_, colIndex) =>
                    renderGridCell(rowIndex, colIndex)
                  )
                ).flat()}
              </div>
            </div>

            {/* Statistics */}
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Total Jobs: {jobs.length}</span>
              <span>Grid: {rows} × {cols}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MatrixProgressGrid; 