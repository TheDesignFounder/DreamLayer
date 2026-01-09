import React, { useState, useCallback } from 'react';
import { Search, ArrowUp, ArrowDown, RefreshCw, Loader2, Upload } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import LoraCard from './LoraCard';
import { LoraModel } from '@/types/lora';
import { useModelRefresh } from '@/hooks/useModelRefresh';
import { useToast } from '@/hooks/use-toast';

const LoraBrowser = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loraModels, setLoraModels] = useState<LoraModel[]>([]);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const fetchLoraModels = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:5002/api/lora-models');
      if (!response.ok) {
        throw new Error('Failed to fetch LoRA models');
      }
      const data = await response.json();
      if (data.status === 'success') {
        // Add default values for optional fields
        const modelsWithDefaults = data.models.map((model: LoraModel) => ({
          ...model,
          preview: model.preview || '/placeholder.svg',
          triggerWords: model.triggerWords || [],
          description: model.description || '',
          tags: model.tags || [],
          defaultWeight: model.defaultWeight || 1.0
        }));
        setLoraModels(modelsWithDefaults);
      } else {
        throw new Error(data.message || 'Failed to fetch LoRA models');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Use WebSocket auto-refresh hook for LoRA models
  useModelRefresh(fetchLoraModels, 'loras');

  const filteredModels = loraModels.filter(model => {
    const matchesSearch = model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         model.triggerWords?.some(word => word.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesSearch;
  });

  const sortedModels = [...filteredModels].sort((a, b) => {
    const comparison = a.name.localeCompare(b.name);
    return sortOrder === 'desc' ? -comparison : comparison;
  });

  const handleLoraApply = (model: LoraModel) => {
    const loraTag = `<lora:${model.filename.replace('.safetensors', '')}:${model.defaultWeight || 1.0}>`;
    console.log(`Applied LoRA: ${loraTag}`);
    // In a real implementation, this would add to the prompt
  };

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  const handleRefresh = () => {
    fetchLoraModels();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await fetch('http://localhost:5002/api/upload-lora', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload LoRA files');
      }

      const data = await response.json();

      toast({
        title: "Upload successful",
        description: `Uploaded ${files.length} file(s) to ComfyUI/models/loras`,
      });

      setUploadDialogOpen(false);
      fetchLoraModels();
    } catch (err) {
      toast({
        title: "Upload failed",
        description: err instanceof Error ? err.message : 'Failed to upload files',
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-left pt-4 pb-8 text-destructive">
        <div className="text-lg font-medium mb-1">Error loading LoRA models</div>
        <div className="text-sm">{error}</div>
        <button
          onClick={handleRefresh}
          className="mt-4 px-4 py-2 rounded-md bg-muted hover:bg-muted/80 text-sm font-medium flex items-center gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Search and Controls - Only show when models exist */}
      {loraModels.length > 0 && (
        <>
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search LoRA models..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background text-sm"
                />
              </div>
              <button
                onClick={toggleSortOrder}
                className="p-2 border border-input rounded-md hover:bg-accent transition-colors"
              >
                {sortOrder === 'asc' ? (
                  <ArrowUp className="h-4 w-4" />
                ) : (
                  <ArrowDown className="h-4 w-4" />
                )}
              </button>
              <button
                onClick={handleRefresh}
                className="p-2 border border-input rounded-md hover:bg-accent transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
              <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="flex items-center gap-2">
                    <Upload className="h-4 w-4" />
                    Add Lora
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Upload LoRA Files</DialogTitle>
                    <DialogDescription>
                      <div className="space-y-2 text-left">
                        <div className="mt-1">
                          <span className="font-medium">Step 1:</span> Browse LoRAs on{' '}
                          <a
                            href="https://civitai.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            CivitAI
                          </a>
                          {' '}or{' '}
                          <a
                            href="https://huggingface.co"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            Hugging Face
                          </a>
                          .
                        </div>
                        <div>
                          <span className="font-medium">Step 2:</span> Add LoRA files (.safetensors or .ckpt)
                        </div>
                      </div>
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
                      <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                      <input
                        type="file"
                        accept=".safetensors,.ckpt"
                        multiple
                        onChange={handleFileUpload}
                        disabled={isUploading}
                        className="hidden"
                        id="lora-file-upload"
                      />
                      <label
                        htmlFor="lora-file-upload"
                        className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                      >
                        {isUploading ? 'Uploading...' : 'Select Files'}
                      </label>
                      <p className="text-sm text-muted-foreground mt-2">
                        Supports .safetensors and .ckpt files
                      </p>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          {/* Results count */}
          <div className="text-sm text-muted-foreground -mb-4">
            {sortedModels.length} model{sortedModels.length !== 1 ? 's' : ''} found
          </div>
        </>
      )}

      {/* Models grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {sortedModels.map(model => (
          <LoraCard
            key={model.id}
            model={model}
            viewMode="grid"
          />
        ))}
      </div>

      {sortedModels.length === 0 && (
        <div className="text-left pt-4 pb-8 text-muted-foreground mt-0">
          <div className="text-lg font-medium mb-4 text-foreground">No LoRA models found</div>
          <div className="text-sm mb-1">
            <span className="font-medium">Step 1:</span> Browse LoRAs on{' '}
            <a
              href="https://civitai.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              CivitAI
            </a>
            {' '}or{' '}
            <a
              href="https://huggingface.co"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Hugging Face
            </a>
            .
          </div>
          <div className="text-sm mb-2 mt-4"><span className="font-medium">Step 2:</span> Add LoRA files to the following directory:</div>
          <div className="text-sm font-mono bg-muted p-2 rounded-md mb-1 max-w-md">
            ComfyUI/models/loras
          </div>
          <Button
            variant="outline"
            className="mt-4 flex items-center gap-2"
            onClick={() => setUploadDialogOpen(true)}
          >
            <Upload className="h-4 w-4" />
            Upload LoRA Files
          </Button>
        </div>
      )}
    </div>
  );
};

export default LoraBrowser;
