import React, { useState } from 'react';
import { useMatrixRunnerStore } from '@/stores/useMatrixRunnerStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Play,
  AlertCircle,
  Search,
  Filter,
  Download,
  Eye
} from 'lucide-react';
import { formatDuration } from '@/utils/matrixUtils';

const MatrixJobList: React.FC = () => {
  const { jobs } = useMatrixRunnerStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'createdAt' | 'status' | 'seed' | 'sampler'>('createdAt');

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

  const getStatusIcon = (status: string) => {
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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-500">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'running':
        return <Badge variant="default" className="bg-blue-500">Running</Badge>;
      case 'paused':
        return <Badge variant="secondary">Paused</Badge>;
      default:
        return <Badge variant="outline">Pending</Badge>;
    }
  };

  const getDuration = (job: any) => {
    if (job.startedAt && job.completedAt) {
      return formatDuration((job.completedAt - job.startedAt) / 1000);
    }
    return null;
  };

  const filteredJobs = jobs
    .filter(job => {
      const matchesSearch = 
        job.parameters.prompt.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.parameters.sampler_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.parameters.seed.toString().includes(searchTerm) ||
        job.id.includes(searchTerm);
      
      const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'createdAt':
          return b.createdAt - a.createdAt;
        case 'status':
          return a.status.localeCompare(b.status);
        case 'seed':
          return a.parameters.seed - b.parameters.seed;
        case 'sampler':
          return a.parameters.sampler_name.localeCompare(b.parameters.sampler_name);
        default:
          return 0;
      }
    });

  const exportJobs = () => {
    const csvData = [
      ['Job ID', 'Status', 'Seed', 'Sampler', 'Steps', 'CFG Scale', 'Width', 'Height', 'Prompt', 'Duration', 'Error'],
      ...filteredJobs.map(job => [
        job.id,
        job.status,
        job.parameters.seed,
        job.parameters.sampler_name,
        job.parameters.steps,
        job.parameters.cfg_scale,
        job.parameters.width,
        job.parameters.height,
        `"${job.parameters.prompt}"`,
        getDuration(job) || '',
        job.error || ''
      ])
    ];

    const csvContent = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `matrix-jobs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Job List ({filteredJobs.length} of {jobs.length})</span>
            <Button onClick={exportJobs} variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export CSV
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Search jobs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-input rounded-md text-sm"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="paused">Paused</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="px-3 py-2 border border-input rounded-md text-sm"
              >
                <option value="createdAt">Sort by Created</option>
                <option value="status">Sort by Status</option>
                <option value="seed">Sort by Seed</option>
                <option value="sampler">Sort by Sampler</option>
              </select>
            </div>
          </div>

          {/* Job List */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(job.status)}
                    <span className="font-mono text-sm text-muted-foreground">
                      {job.id.substring(0, 8)}...
                    </span>
                    {getStatusBadge(job.status)}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    {getDuration(job) && (
                      <span>Duration: {getDuration(job)}</span>
                    )}
                    <span>
                      {new Date(job.createdAt).toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Seed:</span>
                    <span className="ml-1 font-mono">{job.parameters.seed}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Sampler:</span>
                    <span className="ml-1">{job.parameters.sampler_name}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Steps:</span>
                    <span className="ml-1">{job.parameters.steps}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">CFG:</span>
                    <span className="ml-1">{job.parameters.cfg_scale}</span>
                  </div>
                </div>

                <div className="mt-2">
                  <span className="text-muted-foreground text-sm">Prompt:</span>
                  <p className="text-sm mt-1 line-clamp-2">
                    {job.parameters.prompt}
                  </p>
                </div>

                {job.error && (
                  <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    <span className="font-medium">Error:</span> {job.error}
                  </div>
                )}

                {job.result?.images && job.result.images.length > 0 && (
                  <div className="mt-2 flex items-center gap-2">
                    <Eye className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {job.result.images.length} image{job.result.images.length !== 1 ? 's' : ''} generated
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {filteredJobs.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No jobs match the current filters.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MatrixJobList; 