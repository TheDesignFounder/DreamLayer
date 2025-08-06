import React, { useEffect } from 'react';
import { useRunRegistryStore } from '@/stores/useRunRegistryStore';
import { RunConfig } from '@/types/runRegistry';
import { format } from 'date-fns';
import { Trash2, Eye, Clock, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

const RunRegistryPage: React.FC = () => {
  const { 
    runs, 
    loading, 
    error, 
    selectedRun, 
    fetchRuns, 
    deleteRun, 
    clearError, 
    setSelectedRun 
  } = useRunRegistryStore();

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  const handleDeleteRun = async (runId: string) => {
    if (confirm('Are you sure you want to delete this run?')) {
      await deleteRun(runId);
    }
  };

  const handleViewConfig = (run: RunConfig) => {
    setSelectedRun(run);
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return timestamp;
    }
  };

  const getGenerationTypeColor = (type: string) => {
    return type === 'txt2img' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Run Registry</h2>
        <div className="grid gap-4">
          {[...Array(5)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-3 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Run Registry</h2>
        <Alert variant="destructive">
          <AlertDescription>
            {error}
            <Button variant="link" onClick={clearError} className="ml-2 p-0 h-auto">
              Try again
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Run Registry</h2>
        <Button onClick={fetchRuns} variant="outline" size="sm">
          Refresh
        </Button>
      </div>

      {runs.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Clock className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No runs yet</h3>
            <p className="text-muted-foreground text-center">
              Completed generations will appear here with their frozen configurations.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {runs.map((run) => (
            <Card key={run.run_id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="font-mono text-xs">
                      {run.run_id.slice(0, 8)}...
                    </Badge>
                    <Badge className={getGenerationTypeColor(run.generation_type)}>
                      {run.generation_type.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewConfig(run)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View Config
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteRun(run.run_id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {formatTimestamp(run.timestamp)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="font-medium line-clamp-2">{run.prompt}</p>
                    {run.negative_prompt && (
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        Negative: {run.negative_prompt}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-4">
                      <span><strong>Model:</strong> {run.model}</span>
                      <span><strong>Sampler:</strong> {run.sampler}</span>
                      <span><strong>Steps:</strong> {run.steps}</span>
                      <span><strong>CFG:</strong> {run.cfg_scale}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <ImageIcon className="h-4 w-4" />
                      <span>{run.generated_images.length} image(s)</span>
                    </div>
                  </div>

                  {(run.loras.length > 0 || run.controlnets.length > 0) && (
                    <div className="flex flex-wrap gap-2">
                      {run.loras.map((lora, index) => (
                        <Badge key={`lora-${index}`} variant="secondary" className="text-xs">
                          LoRA: {lora.name}
                        </Badge>
                      ))}
                      {run.controlnets.map((controlnet, index) => (
                        <Badge key={`controlnet-${index}`} variant="secondary" className="text-xs">
                          ControlNet: {controlnet.model}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Frozen Config Modal */}
      <Dialog open={!!selectedRun} onOpenChange={() => setSelectedRun(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Frozen Configuration</DialogTitle>
          </DialogHeader>
          {selectedRun && (
            <ScrollArea className="max-h-[60vh]">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Basic Info</h4>
                    <div className="space-y-1 text-sm">
                      <p><strong>Run ID:</strong> {selectedRun.run_id}</p>
                      <p><strong>Timestamp:</strong> {formatTimestamp(selectedRun.timestamp)}</p>
                      <p><strong>Type:</strong> {selectedRun.generation_type}</p>
                      <p><strong>Version:</strong> {selectedRun.version}</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Generation Settings</h4>
                    <div className="space-y-1 text-sm">
                      <p><strong>Model:</strong> {selectedRun.model}</p>
                      <p><strong>VAE:</strong> {selectedRun.vae || 'Default'}</p>
                      <p><strong>Sampler:</strong> {selectedRun.sampler}</p>
                      <p><strong>Steps:</strong> {selectedRun.steps}</p>
                      <p><strong>CFG Scale:</strong> {selectedRun.cfg_scale}</p>
                      <p><strong>Seed:</strong> {selectedRun.seed}</p>
                    </div>
                  </div>
                </div>

                <Separator />

                <div>
                  <h4 className="font-semibold mb-2">Prompts</h4>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm font-medium">Positive Prompt:</p>
                      <p className="text-sm bg-muted p-2 rounded">{selectedRun.prompt}</p>
                    </div>
                    {selectedRun.negative_prompt && (
                      <div>
                        <p className="text-sm font-medium">Negative Prompt:</p>
                        <p className="text-sm bg-muted p-2 rounded">{selectedRun.negative_prompt}</p>
                      </div>
                    )}
                  </div>
                </div>

                <Separator />

                <div>
                  <h4 className="font-semibold mb-2">Image Settings</h4>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <p><strong>Width:</strong> {selectedRun.width}</p>
                    <p><strong>Height:</strong> {selectedRun.height}</p>
                    <p><strong>Batch Size:</strong> {selectedRun.batch_size}</p>
                    <p><strong>Batch Count:</strong> {selectedRun.batch_count}</p>
                  </div>
                </div>

                {selectedRun.loras.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-semibold mb-2">LoRAs</h4>
                      <div className="space-y-2">
                        {selectedRun.loras.map((lora, index) => (
                          <div key={index} className="text-sm">
                            <p><strong>Name:</strong> {lora.name}</p>
                            <p><strong>Strength:</strong> {lora.strength}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {selectedRun.controlnets.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-semibold mb-2">ControlNets</h4>
                      <div className="space-y-2">
                        {selectedRun.controlnets.map((controlnet, index) => (
                          <div key={index} className="text-sm">
                            <p><strong>Model:</strong> {controlnet.model}</p>
                            <p><strong>Strength:</strong> {controlnet.strength}</p>
                            <p><strong>Enabled:</strong> {controlnet.enabled ? 'Yes' : 'No'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                <Separator />

                <div>
                  <h4 className="font-semibold mb-2">Generated Images</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {selectedRun.generated_images.map((image, index) => (
                      <div key={index} className="text-sm">
                        <p className="font-mono text-xs">{image}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                <div>
                  <h4 className="font-semibold mb-2">Workflow (Serialized)</h4>
                  <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32">
                    {JSON.stringify(selectedRun.workflow, null, 2)}
                  </pre>
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RunRegistryPage; 