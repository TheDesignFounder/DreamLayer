import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Eye, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useRunRegistryStore } from '@/stores/useRunRegistryStore';
import { runService } from '@/services/runService';
import RunConfigModal from '@/components/RunConfigModal';

const Runs: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { 
    runs, 
    selectedRun, 
    isLoading, 
    error,
    setRuns, 
    selectRun, 
    setLoading, 
    setError, 
    clearError,
    getRunById
  } = useRunRegistryStore();

  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchRuns = async () => {
      try {
        setLoading(true);
        clearError();
        const runsData = await runService.getRuns();
        setRuns(runsData);
        
        // If we have an ID in the URL, open the modal for that run
        if (id) {
          const run = runsData.find(r => r.id === id);
          if (run) {
            selectRun(run);
            setIsModalOpen(true);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch runs');
      } finally {
        setLoading(false);
      }
    };

    fetchRuns();
  }, [setRuns, setLoading, setError, clearError, id, selectRun]);

  const handleViewConfig = (run: any) => {
    selectRun(run);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    selectRun(null);
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInHours * 60);
      return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffInHours < 24) {
      const hours = Math.floor(diffInHours);
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffInHours / 24);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'running':
        return <AlertCircle className="w-4 h-4 text-blue-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading runs...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">Error Loading Runs</h3>
          <p className="text-muted-foreground">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Run Registry</h2>
        <p className="text-muted-foreground">
          View and manage your completed image generation runs
        </p>
      </div>

      {runs.length === 0 ? (
        <div className="text-center py-12">
          <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">No Runs Found</h3>
          <p className="text-muted-foreground">
            Complete some image generations to see them here
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {runs.map((run) => (
            <div
              key={run.id}
              className="bg-card border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    {getStatusIcon(run.status)}
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">
                        Run {run.id}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {formatTimestamp(run.timestamp)}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(run.status)}`}>
                      {run.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-muted-foreground">Model:</span>
                      <span className="ml-2 text-foreground">{run.config.model}</span>
                    </div>
                    <div>
                      <span className="font-medium text-muted-foreground">Sampler:</span>
                      <span className="ml-2 text-foreground">{run.config.sampler}</span>
                    </div>
                    <div>
                      <span className="font-medium text-muted-foreground">Steps:</span>
                      <span className="ml-2 text-foreground">{run.config.steps}</span>
                    </div>
                    <div>
                      <span className="font-medium text-muted-foreground">CFG:</span>
                      <span className="ml-2 text-foreground">{run.config.cfg_scale.toFixed(1)}</span>
                    </div>
                  </div>

                  {run.config.prompt && (
                    <div className="mt-3">
                      <span className="font-medium text-muted-foreground text-sm">Prompt:</span>
                      <p className="mt-1 text-sm text-foreground line-clamp-2">
                        {run.config.prompt}
                      </p>
                    </div>
                  )}

                  {run.images && run.images.length > 0 && (
                    <div className="mt-3">
                      <span className="font-medium text-muted-foreground text-sm">Images:</span>
                      <div className="flex gap-2 mt-1">
                        {run.images.map((image, index) => (
                          <img
                            key={index}
                            src={image.url}
                            alt={`Generated image ${index + 1}`}
                            className="w-12 h-12 object-cover rounded border"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleViewConfig(run)}
                  className="flex items-center gap-2 px-3 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors ml-4"
                >
                  <Eye className="w-4 h-4" />
                  View Config
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <RunConfigModal
        run={selectedRun}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default Runs; 