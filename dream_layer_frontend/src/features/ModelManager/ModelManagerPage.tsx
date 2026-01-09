import React, { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Search,
  Upload,
  RefreshCw,
  Grid3X3,
  List,
  HardDrive,
  FileText,
  Eye,
  EyeOff,
  Brain,
  Palette,
  Rainbow,
  Target,
  TrendingUp,
  FileType,
  Settings
} from "lucide-react";
import ModelDropZone, { ModelType, UploadedModel } from '@/components/ModelDropZone';
import {
  fetchAllModelTypes,
  addModelRefreshListener,
  ensureWebSocketConnection,
  ModelInfo
} from '@/services/modelService';
import { toast } from "@/components/ui/sonner";

const ModelManagerPage = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [filteredModels, setFilteredModels] = useState<ModelInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedModelType, setSelectedModelType] = useState<ModelType | 'all'>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'name' | 'type'>('type');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showUploadZone, setShowUploadZone] = useState(true);

  // Model type options with user-friendly labels
  const modelTypes: { value: ModelType | 'all'; label: string; description: string }[] = [
    { value: 'all', label: 'All Models', description: 'Show all model types' },
    { value: 'checkpoints', label: 'Base Model (Checkpoint)', description: "The 'brain' that generates images" },
    { value: 'loras', label: 'Style Add-ons (LoRAs)', description: 'Modifies art style or subjects' },
    { value: 'vae', label: 'Image Enhancer (VAE)', description: 'Improves colors and quality' },
    { value: 'controlnet', label: 'Guided Generation (ControlNet)', description: 'Controls image composition' },
    { value: 'upscale_models', label: 'Resolution Enhancer (Upscalers)', description: 'Makes images larger and sharper' },
    { value: 'embeddings', label: 'Text Concepts (Embeddings)', description: 'Adds new words/concepts' },
    { value: 'hypernetworks', label: 'Style Modifiers (Hypernetworks)', description: 'Advanced style control' }
  ];

  const loadModels = async () => {
    try {
      setIsLoading(true);
      const allModels = await fetchAllModelTypes();
      setModels(allModels);
    } catch (error) {
      console.error('Error loading models:', error);
      toast.error('Failed to load models');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter and sort models
  useEffect(() => {
    let filtered = [...models]; // Create a copy to avoid mutating original array

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(model =>
        model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        model.filename.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by model type
    if (selectedModelType !== 'all') {
      filtered = filtered.filter(model => model.type === selectedModelType);
    }

    // Sort models
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'type':
          comparison = getModelTypePriority(a.type) - getModelTypePriority(b.type);
          break;
        default:
          comparison = 0;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredModels(filtered);
  }, [models, searchQuery, selectedModelType, sortBy, sortOrder]);

  // Setup WebSocket listener for auto-refresh
  useEffect(() => {
    loadModels();
    ensureWebSocketConnection();

    return addModelRefreshListener(() => {
      console.log('📡 ModelManager: Received model refresh event, reloading models...');
      loadModels();
      toast.success('Models refreshed automatically!');
    });
  }, []);

  const handleModelUploaded = (uploadedModel: UploadedModel) => {
    console.log('Model uploaded:', uploadedModel);
    // Add model optimistically, but prevent duplicates
    const newModel: ModelInfo = {
      id: uploadedModel.filename,
      name: uploadedModel.originalFilename.replace(/\.[^/.]+$/, ""), // Remove extension
      filename: uploadedModel.filename,
      type: uploadedModel.modelType,
      size: uploadedModel.size,
      dateAdded: new Date().toISOString(),
      path: uploadedModel.filepath
    };

    // Only add if not already present
    setModels(prev => {
      const exists = prev.some(m => m.filename === newModel.filename);
      return exists ? prev : [newModel, ...prev];
    });

    toast.success(`${uploadedModel.originalFilename} uploaded successfully!`);
  };



  const getModelTypeColor = (type: ModelType): string => {
    const colors = {
      checkpoints: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      loras: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      controlnet: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      upscale_models: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      vae: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      embeddings: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      hypernetworks: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  const getModelTypeIcon = (type: ModelType) => {
    const iconProps = { className: "h-3 w-3" };
    const icons = {
      checkpoints: <Brain {...iconProps} />,
      loras: <Palette {...iconProps} />,
      vae: <Rainbow {...iconProps} />,
      controlnet: <Target {...iconProps} />,
      upscale_models: <TrendingUp {...iconProps} />,
      embeddings: <FileType {...iconProps} />,
      hypernetworks: <Settings {...iconProps} />
    };
    return icons[type] || <HardDrive {...iconProps} />;
  };

  const getModelTypePriority = (type: ModelType): number => {
    const priorities = {
      checkpoints: 1,
      loras: 2,
      vae: 3,
      controlnet: 4,
      upscale_models: 5,
      embeddings: 6,
      hypernetworks: 7
    };
    return priorities[type] || 8;
  };

  const getModelTypeLabel = (type: ModelType): string => {
    const modelType = modelTypes.find(mt => mt.value === type);
    return modelType?.label || type;
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <h3 className="text-base font-medium">Model Manager</h3>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowUploadZone(!showUploadZone)}
            className="flex items-center space-x-2"
          >
            {showUploadZone ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            <span>{showUploadZone ? 'Hide' : 'Show'} Upload</span>
          </Button>

        </div>
      </div>

      {/* 2-Column Layout */}
      <div className={showUploadZone ? "grid grid-cols-1 lg:grid-cols-2 gap-4" : ""}>
        {/* Left Column - Upload Zone */}
        {showUploadZone && (
          <Card className="p-6">
            <div className="space-y-4">
              <h2 className="text-sm font-medium">Upload New Model</h2>
              <ModelDropZone onModelUploaded={handleModelUploaded} />
            </div>
          </Card>
        )}

        {/* Right Column - Filters, Controls, and Models Display */}
        <Card className="p-4">
          <div className="space-y-4">
            <h2 className="text-sm font-medium">Browse Models</h2>

            {/* Filters and Controls */}
            <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search models..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={showUploadZone ? "pl-10 w-64" : "pl-10 w-96"}
                />
              </div>

              {/* Model Type Filter */}
              <Select
                value={selectedModelType}
                onValueChange={(value) => {
                  if (value === 'all' || modelTypes.some(t => t.value === value)) {
                    setSelectedModelType(value as ModelType | 'all');
                  }
                }}
              >
                <SelectTrigger className={showUploadZone ? "w-48" : "w-72"}>
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  {modelTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* View Mode Toggle */}
              <div className="flex items-center space-x-1 border rounded-md">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="rounded-r-none"
                >
                  <Grid3X3 className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="rounded-l-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {filteredModels.length} of {models.length} models
              </p>
            </div>

            {/* Models Grid/List */}
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                <span className="ml-2 text-muted-foreground">Loading models...</span>
              </div>
            ) : filteredModels.length === 0 ? (
              <div className="p-12 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-sm font-medium mb-2">No models found</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {models.length === 0
                    ? "Upload a checkpoint model to get started with image generation"
                    : "Try adjusting your search or filters"
                  }
                </p>
                {models.length === 0 && (
                  <Button onClick={() => setShowUploadZone(true)}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Model
                  </Button>
                )}
              </div>
            ) : (
              <div className={viewMode === 'grid'
                ? "grid grid-cols-1 md:grid-cols-2 gap-4"
                : "space-y-2"
              }>
                {filteredModels.map((model) => (
                  <ModelCard
                    key={model.id}
                    model={model}
                    viewMode={viewMode}
                    getModelTypeColor={getModelTypeColor}
                    getModelTypeIcon={getModelTypeIcon}
                    getModelTypeLabel={getModelTypeLabel}
                  />
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

interface ModelCardProps {
  model: ModelInfo;
  viewMode: 'grid' | 'list';
  getModelTypeColor: (type: ModelType) => string;
  getModelTypeIcon: (type: ModelType) => React.ReactNode;
  getModelTypeLabel: (type: ModelType) => string;
}

const ModelCard: React.FC<ModelCardProps> = ({
  model,
  viewMode,
  getModelTypeColor,
  getModelTypeIcon,
  getModelTypeLabel
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      // Handle selection/activation - for now just focus the card
      (e.currentTarget as HTMLElement).focus();
    }
  };

  if (viewMode === 'list') {
    return (
      <Card className="p-4 hover:bg-accent/50 transition-colors focus:ring-2 focus:ring-primary focus:outline-none">
        <div
          className="flex items-center justify-between"
          tabIndex={0}
          onKeyDown={handleKeyDown}
          role="button"
          aria-label={`Model: ${model.name}, Type: ${getModelTypeLabel(model.type)}`}
        >
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            <div className="flex-1 min-w-0">
              <h3 className="font-medium truncate">{model.name}</h3>
              <p className="text-sm text-muted-foreground truncate">{model.filename}</p>
            </div>
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              <Badge className={getModelTypeColor(model.type)}>
                {getModelTypeIcon(model.type)}
                <span className="ml-1">{getModelTypeLabel(model.type)}</span>
              </Badge>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      className="p-4 hover:bg-accent/50 transition-colors focus:ring-2 focus:ring-primary focus:outline-none"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      role="button"
      aria-label={`Model: ${model.name}, Type: ${getModelTypeLabel(model.type)}`}
    >
      <div className="space-y-3">
        <div className="flex items-start justify-start">
          <Badge className={getModelTypeColor(model.type)}>
            {getModelTypeIcon(model.type)}
            <span className="ml-1">{getModelTypeLabel(model.type)}</span>
          </Badge>
        </div>
        <div>
          <h3 className="font-medium truncate" title={model.name}>
            {model.name}
          </h3>
          <p className="text-sm text-muted-foreground truncate" title={model.filename}>
            {model.filename}
          </p>
        </div>

      </div>
    </Card>
  );
};

export default ModelManagerPage;
