/**
 * Run Registry Page Component
 * Displays list of generation runs with ability to view detailed configurations
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RunService } from '@/services/runService';
import { Run, RunSummary } from '@/types/run';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'sonner';
import { Clock, Image, Settings, Trash2, Eye } from 'lucide-react';

export function RunRegistry() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [loadingRun, setLoadingRun] = useState(false);

  // Fetch runs on component mount
  useEffect(() => {
    fetchRuns();
  }, []);

  // Handle deep linking - open run if ID is in URL
  useEffect(() => {
    if (id) {
      fetchAndOpenRun(id);
    }
  }, [id]);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const fetchedRuns = await RunService.getRuns();
      setRuns(fetchedRuns);
    } catch (error) {
      toast.error('Failed to fetch runs');
      console.error('Error fetching runs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAndOpenRun = async (runId: string) => {
    try {
      setLoadingRun(true);
      const run = await RunService.getRun(runId);
      if (run) {
        setSelectedRun(run);
        setModalOpen(true);
      } else {
        toast.error('Run not found');
        navigate('/runs');
      }
    } catch (error) {
      toast.error('Failed to fetch run details');
      console.error('Error fetching run:', error);
    } finally {
      setLoadingRun(false);
    }
  };

  const handleViewRun = async (runId: string) => {
    navigate(`/runs/${runId}`);
    await fetchAndOpenRun(runId);
  };

  const handleDeleteRun = async (runId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this run?')) {
      return;
    }

    try {
      const success = await RunService.deleteRun(runId);
      if (success) {
        toast.success('Run deleted successfully');
        setRuns(runs.filter(run => run.id !== runId));
        if (selectedRun?.id === runId) {
          setSelectedRun(null);
          setModalOpen(false);
        }
      } else {
        toast.error('Failed to delete run');
      }
    } catch (error) {
      toast.error('Failed to delete run');
      console.error('Error deleting run:', error);
    }
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedRun(null);
    if (id) {
      navigate('/runs');
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const renderConfigValue = (value: any): string => {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const getRequiredConfigKeys = (): string[] => {
    return [
      'model',
      'vae',
      'prompt',
      'negative_prompt',
      'seed',
      'sampler',
      'steps',
      'cfg_scale',
      'workflow',
      'workflow_version',
      'loras',
      'controlnets'
    ];
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Run Registry</h1>
        <p className="text-muted-foreground">
          View and manage your generation history
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-3 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : runs.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Image className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No runs yet</h3>
            <p className="text-muted-foreground">
              Your generation runs will appear here
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {runs.map((run) => (
            <Card
              key={run.id}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => handleViewRun(run.id)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-1">
                      Run {run.id.slice(0, 8)}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-1 mt-1">
                      <Clock className="h-3 w-3" />
                      {formatDate(run.timestamp)}
                    </CardDescription>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => handleDeleteRun(run.id, e)}
                    className="h-8 w-8"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{run.generation_type}</Badge>
                    <Badge variant="outline">{run.model}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {run.prompt || 'No prompt'}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Run Details Modal */}
      <Dialog open={modalOpen} onOpenChange={handleCloseModal}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              View Frozen Config
            </DialogTitle>
            <DialogDescription>
              {selectedRun && (
                <span>
                  Run ID: {selectedRun.id} | {formatDate(selectedRun.timestamp)}
                </span>
              )}
            </DialogDescription>
          </DialogHeader>

          {loadingRun ? (
            <div className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-32 w-full" />
            </div>
          ) : selectedRun ? (
            <ScrollArea className="h-[60vh] pr-4">
              <div className="space-y-4">
                {/* Core Parameters */}
                <div>
                  <h3 className="font-semibold mb-2">Core Parameters</h3>
                  <div className="bg-muted p-4 rounded-lg space-y-2">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-medium">Model:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.model)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">VAE:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.vae)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Seed:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.seed)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Sampler:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.sampler)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Steps:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.steps)}
                        </p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">CFG Scale:</span>
                        <p className="text-sm text-muted-foreground">
                          {renderConfigValue(selectedRun.config.cfg_scale)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Prompts */}
                <div>
                  <h3 className="font-semibold mb-2">Prompts</h3>
                  <div className="bg-muted p-4 rounded-lg space-y-2">
                    <div>
                      <span className="text-sm font-medium">Positive Prompt:</span>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {renderConfigValue(selectedRun.config.prompt)}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm font-medium">Negative Prompt:</span>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {renderConfigValue(selectedRun.config.negative_prompt)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* LoRAs */}
                {selectedRun.config.loras && Object.keys(selectedRun.config.loras).length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">LoRAs</h3>
                    <div className="bg-muted p-4 rounded-lg">
                      <pre className="text-sm text-muted-foreground overflow-x-auto">
                        {renderConfigValue(selectedRun.config.loras)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* ControlNets */}
                {selectedRun.config.controlnets && Object.keys(selectedRun.config.controlnets).length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">ControlNets</h3>
                    <div className="bg-muted p-4 rounded-lg">
                      <pre className="text-sm text-muted-foreground overflow-x-auto">
                        {renderConfigValue(selectedRun.config.controlnets)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Workflow */}
                <div>
                  <h3 className="font-semibold mb-2">Workflow</h3>
                  <div className="bg-muted p-4 rounded-lg space-y-2">
                    <div>
                      <span className="text-sm font-medium">Version:</span>
                      <p className="text-sm text-muted-foreground">
                        {renderConfigValue(selectedRun.config.workflow_version)}
                      </p>
                    </div>
                    {selectedRun.config.workflow && Object.keys(selectedRun.config.workflow).length > 0 && (
                      <div>
                        <span className="text-sm font-medium">Workflow Data:</span>
                        <pre className="text-sm text-muted-foreground overflow-x-auto mt-2">
                          {renderConfigValue(selectedRun.config.workflow)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>

                {/* Full Configuration (Serialized) */}
                <div>
                  <h3 className="font-semibold mb-2">Full Configuration (Serialized)</h3>
                  <div className="bg-muted p-4 rounded-lg">
                    <pre className="text-sm text-muted-foreground overflow-x-auto">
                      {JSON.stringify(selectedRun.config, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            </ScrollArea>
          ) : null}

          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={handleCloseModal}>
              Close
            </Button>
            {selectedRun && (
              <Button
                variant="default"
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(selectedRun.config, null, 2));
                  toast.success('Configuration copied to clipboard');
                }}
              >
                Copy Config
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
