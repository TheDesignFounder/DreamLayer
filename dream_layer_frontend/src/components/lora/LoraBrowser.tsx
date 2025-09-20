import React, { useState, useCallback } from 'react';
import { Search, Grid, List, ArrowUp, ArrowDown, RefreshCw, Loader2 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import LoraCard from './LoraCard';
import { LoraModel } from '@/types/lora';
import { useModelRefresh } from '@/hooks/useModelRefresh';

const LoraBrowser = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loraModels, setLoraModels] = useState<LoraModel[]>([]);

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
    let comparison = 0;
    switch (sortBy) {
      case 'name':
        comparison = a.name.localeCompare(b.name);
        break;
      case 'filename':
        comparison = a.filename.localeCompare(b.filename);
        break;
      default:
        return 0;
    }
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
      {/* Search and Controls */}
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
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Sort by..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="name">Sort by Name</SelectItem>
              <SelectItem value="filename">Sort by Filename</SelectItem>
            </SelectContent>
          </Select>
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
          <div className="flex border border-input rounded-md">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 ${viewMode === 'grid' ? 'bg-accent' : ''}`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 ${viewMode === 'list' ? 'bg-accent' : ''}`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-muted-foreground -mb-4">
        {sortedModels.length} model{sortedModels.length !== 1 ? 's' : ''} found
      </div>

      {/* Models grid/list */}
      <div className={viewMode === 'grid' 
        ? "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3" 
        : "space-y-2"
      }>
        {sortedModels.map(model => (
          <LoraCard
            key={model.id}
            model={model}
            viewMode={viewMode}
          />
        ))}
      </div>

      {sortedModels.length === 0 && (
        <div className="text-left pt-4 pb-8 text-muted-foreground mt-0">
          <div className="text-lg font-medium mb-1 text-foreground">No LoRA models found</div>
          <div className="text-sm mb-6">Looks like your LoRA folder is empty.</div>
          <div className="text-sm mb-1">Add LoRA files to one of the following directories:</div>
          <div className="text-sm font-mono bg-muted p-2 rounded-md mb-1 max-w-md">
            ComfyUI/models/loras
          </div>
          <div className="text-sm">
            Need models? Browse LoRAs on{' '}
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
        </div>
      )}
    </div>
  );
};

export default LoraBrowser;
