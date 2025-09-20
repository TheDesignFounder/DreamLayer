import React, { useState, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Upload, FileText, CheckCircle, AlertCircle, X } from "lucide-react";
import { toast } from "@/components/ui/sonner";

// Model types supported by the backend
export type ModelType = 'checkpoints' | 'loras' | 'controlnet' | 'upscale_models' | 'vae' | 'embeddings' | 'hypernetworks';

export interface UploadedModel {
  filename: string;
  originalFilename: string;
  displayName?: string;
  modelType: ModelType;
  filepath: string;
  size: number;
}

interface ModelDropZoneProps {
  onModelUploaded?: (model: UploadedModel) => void;
  acceptedTypes?: string[];
  modelType?: ModelType;
  className?: string;
}

const ModelDropZone: React.FC<ModelDropZoneProps> = ({
  onModelUploaded,
  acceptedTypes = ['.safetensors', '.ckpt', '.pth', '.pt', '.bin'],
  modelType = 'checkpoints',
  className = ""
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedModelType, setSelectedModelType] = useState<ModelType>(modelType);
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<UploadedModel | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Model type options with user-friendly descriptions
  const modelTypeOptions = [
    { value: 'checkpoints', label: 'Base Model (Checkpoint)', description: "The 'brain' that generates images" },
    { value: 'loras', label: 'Style Add-ons (LoRAs)', description: 'Modifies art style or subjects' },
    { value: 'vae', label: 'Image Enhancer (VAE)', description: 'Improves colors and quality' },
    { value: 'controlnet', label: 'Guided Generation (ControlNet)', description: 'Controls image composition' },
    { value: 'upscale_models', label: 'Resolution Enhancer (Upscalers)', description: 'Makes images larger and sharper' },
    { value: 'embeddings', label: 'Text Concepts (Embeddings)', description: 'Adds new words/concepts' },
    { value: 'hypernetworks', label: 'Style Modifiers (Hypernetworks)', description: 'Advanced style control' }
  ] as const;

  const validateFile = (file: File): string | null => {
    // Check file extension using regex to handle hidden files and multiple dots
    const match = file.name.match(/(\.[^.]+)$/);
    const fileExtension = match ? match[1].toLowerCase() : '';
    if (!acceptedTypes.includes(fileExtension)) {
      return `Invalid file type. Only ${acceptedTypes.join(', ')} files are supported.`;
    }

    return null;
  };

  const uploadFile = async (file: File): Promise<UploadedModel> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_type', selectedModelType);

    const apiBaseUrl = import.meta.env.VITE_BACKEND_API_BASE_URL || 'http://localhost:5002';
    const response = await fetch(`${apiBaseUrl}/api/upload-model`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `Upload failed: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status !== 'success') {
      throw new Error(result.message || 'Upload failed');
    }

    return {
      filename: result.filename,
      originalFilename: result.original_filename,
      displayName: result.display_name,
      modelType: result.model_type,
      filepath: result.filepath,
      size: result.size
    };
  };

  const handleFileUpload = async (file: File) => {
    // Race condition prevention: block if already uploading
    if (isUploading) {
      console.log('Upload already in progress, ignoring new upload request');
      return;
    }

    const validationError = validateFile(file);
    if (validationError) {
      toast.error(validationError);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadedFile(null);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const uploadedModel = await uploadFile(file);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setUploadedFile(uploadedModel);
      onModelUploaded?.(uploadedModel);

      const contextualMessage = getContextualSuccessMessage(uploadedModel.modelType);
      toast.success(contextualMessage);

      // Auto-dismiss success state after 5 seconds
      setTimeout(() => {
        setUploadedFile(null);
        setUploadProgress(0);
      }, 5000);
      
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error instanceof Error ? error.message : 'Upload failed');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleBrowseClick = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  const handleClear = () => {
    setUploadedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getContextualSuccessMessage = (modelType: ModelType): string => {
    const messages = {
      'checkpoints': 'Checkpoint uploaded! This model can now generate images.',
      'loras': 'LoRA uploaded! Use this to modify your image style.',
      'vae': 'VAE uploaded! This will improve your image colors and quality.',
      'controlnet': 'ControlNet uploaded! Use this for guided image generation.',
      'upscale_models': 'Upscaler uploaded! Use this to enhance image resolution.',
      'embeddings': 'Embedding uploaded! This adds new concepts to your prompts.',
      'hypernetworks': 'Hypernetwork uploaded! Use this for advanced style control.'
    };
    return messages[modelType] || 'Model uploaded successfully!';
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Model Type Selection */}
      <div className="space-y-2">
        <Label htmlFor="model-type" className="text-sm font-medium">
          Model Type
        </Label>
        <Select 
          value={selectedModelType} 
          onValueChange={(value: ModelType) => setSelectedModelType(value)}
          disabled={isUploading}
        >
          <SelectTrigger
            id="model-type"
            className="w-full"
          >
            <SelectValue placeholder="Select model type" />
          </SelectTrigger>
          <SelectContent>
            {modelTypeOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                <div className="flex flex-col">
                  <span>{option.label}</span>
                  <span className="text-xs text-muted-foreground">{option.description}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Success Message (if uploaded file exists) */}
      {uploadedFile && (
        <div className="mb-4 p-4 border-2 border-green-200 dark:border-green-800 rounded-lg bg-green-50 dark:bg-green-950/20">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-green-900 dark:text-green-100 text-sm">
                  Upload Successful
                </h4>
                <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                  {uploadedFile.originalFilename}
                </p>
                <div className="flex items-center space-x-3 mt-2">
                  <Badge variant="secondary" className="text-xs">
                    {uploadedFile.modelType}
                  </Badge>
                  <span className="text-xs text-green-600 dark:text-green-400">
                    {formatFileSize(uploadedFile.size)}
                  </span>
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="text-green-700 dark:text-green-300 hover:text-green-900 dark:hover:text-green-100"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Upload Area */}
      <div
          className={`
            relative p-8 border-2 border-dashed rounded-lg text-center transition-all duration-200
            ${dragActive 
              ? 'border-primary bg-primary/5 dark:bg-primary/10' 
              : 'border-border bg-card hover:bg-accent/50'
            }
            ${isUploading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}
          `}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={handleBrowseClick}
        >
          <div className="flex flex-col items-center space-y-4">
            {isUploading ? (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                <div className="space-y-2 w-full max-w-xs">
                  <p className="text-sm text-muted-foreground">Uploading model...</p>
                  <Progress value={uploadProgress} className="w-full" />
                  <p className="text-xs text-muted-foreground">{uploadProgress}%</p>
                </div>
              </>
            ) : (
              <>
                <Upload className="h-12 w-12 text-muted-foreground" />
                <div className="space-y-2">
                  <p className="text-lg font-medium text-foreground">
                    Drop your model file here
                  </p>
                  <p className="text-sm text-muted-foreground">
                    or <span className="text-primary font-medium">browse files</span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supports: {acceptedTypes.join(', ')}
                  </p>
                </div>
                <Button variant="secondary" size="sm" className="mt-4">
                  <FileText className="h-4 w-4 mr-2" />
                  Browse Files
                </Button>
              </>
            )}
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept={acceptedTypes.join(',')}
            onChange={handleFileInputChange}
            disabled={isUploading}
          />
        </div>
    </div>
  );
};

export default ModelDropZone;
