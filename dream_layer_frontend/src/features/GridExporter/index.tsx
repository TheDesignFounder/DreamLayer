"use client";

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  FolderOpen, Download, Settings, Info, CheckCircle, AlertCircle, 
  FileImage, Palette, Upload, Eye, Save, Loader2, Grid3X3, 
  Image as ImageIcon, FileText, Zap, Layers, Palette as PaletteIcon,
  Play, Pause, RotateCcw, Crop, Filter, Adjustments
} from 'lucide-react';
import { gridPresets, GridPreset, getPresetById } from './presets';

interface GridResult {
  status: string;
  message: string;
  output_path?: string;
  images_processed?: number;
  grid_dimensions?: string;
  canvas_size?: string;
  export_format?: string;
  grid_size?: string;
  file_size_bytes?: number;
  results?: any[];
  total_processed?: number;
}

interface PreviewResult {
  status: string;
  preview_image?: string;
  images_found?: number;
  images_in_preview?: number;
  grid_dimensions?: string;
  canvas_size?: string;
}

interface GridTemplate {
  name: string;
  rows: number;
  cols: number;
  cell_size: [number, number];
  margin: number;
  font_size: number;
}

const GridExporter: React.FC = () => {
  // Basic state
  const [inputDir, setInputDir] = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [csvPath, setCsvPath] = useState('');
  const [labelColumns, setLabelColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<number>(3);
  const [cols, setCols] = useState<number>(3);
  const [fontSize, setFontSize] = useState<number>(16);
  const [margin, setMargin] = useState<number>(10);
  
  // Enhanced state
  const [progress, setProgress] = useState<number>(0);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [lastResult, setLastResult] = useState<GridResult | null>(null);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [selectedPreset, setSelectedPreset] = useState<string>('default');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isPreviewLoading, setIsPreviewLoading] = useState<boolean>(false);
  
  // New features state
  const [exportFormat, setExportFormat] = useState<string>('png');
  const [backgroundColor, setBackgroundColor] = useState<[number, number, number]>([255, 255, 255]);
  const [cellSize, setCellSize] = useState<[number, number]>([256, 256]);
  const [batchDirs, setBatchDirs] = useState<string[]>([]);
  const [previewResult, setPreviewResult] = useState<PreviewResult | null>(null);
  const [templates, setTemplates] = useState<GridTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [customTemplateName, setCustomTemplateName] = useState<string>('');
  
  // Preprocessing state
  const [enablePreprocessing, setEnablePreprocessing] = useState<boolean>(false);
  const [resizeMode, setResizeMode] = useState<string>('fit');
  const [resizeWidth, setResizeWidth] = useState<number>(256);
  const [resizeHeight, setResizeHeight] = useState<number>(256);
  const [brightness, setBrightness] = useState<number>(1.0);
  const [contrast, setContrast] = useState<number>(1.0);
  const [saturation, setSaturation] = useState<number>(1.0);
  const [selectedFilter, setSelectedFilter] = useState<string>('none');
  const [filterStrength, setFilterStrength] = useState<number>(1.0);
  
  // Drag & drop state
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [droppedFiles, setDroppedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Animation state
  const [enableAnimation, setEnableAnimation] = useState<boolean>(false);
  const [animationDuration, setAnimationDuration] = useState<number>(500);
  const [animationLoop, setAnimationLoop] = useState<boolean>(true);

  // Load templates on component mount
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/grid-templates');
      const data = await response.json();
      if (data.status === 'success') {
        setTemplates(data.templates);
      }
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const simulateProgress = useCallback((duration: number = 2000) => {
    setProgress(0);
    setProgressMessage('Processing images...');
    
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setProgressMessage('Grid created successfully!');
          return 100;
        }
        return prev + 10;
      });
    }, duration / 10);
  }, []);

  const handleCreateGrid = async () => {
    if (!inputDir || !outputPath) {
      alert('Please provide input directory and output path');
      return;
    }

    setIsLoading(true);
    setProgress(0);
    setProgressMessage('Starting grid creation...');

    try {
      // Prepare preprocessing config
      const preprocessing = enablePreprocessing ? {
        resize: {
          size: [resizeWidth, resizeHeight],
          mode: resizeMode
        },
        brightness: brightness,
        contrast: contrast,
        saturation: saturation,
        filters: selectedFilter !== 'none' ? [{
          type: selectedFilter,
          strength: filterStrength
        }] : []
      } : undefined;

      const requestData = {
        input_dir: inputDir,
        output_path: outputPath,
        csv_path: csvPath || undefined,
        label_columns: labelColumns,
        rows: rows,
        cols: cols,
        font_size: fontSize,
        margin: margin,
        export_format: exportFormat,
        background_color: backgroundColor,
        cell_size: cellSize,
        preprocessing: preprocessing,
        batch_dirs: batchDirs.length > 0 ? batchDirs : undefined
      };

      simulateProgress();

      const response = await fetch('/api/create-labeled-grid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const result: GridResult = await response.json();
      setLastResult(result);

      if (result.status === 'success') {
        setProgress(100);
        setProgressMessage('Grid created successfully!');
      } else {
        setProgressMessage(`Error: ${result.message}`);
      }
    } catch (error) {
      console.error('Error creating grid:', error);
      setProgressMessage('Failed to create grid');
      setLastResult({
        status: 'error',
        message: 'Failed to create grid'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!inputDir) {
      alert('Please provide input directory');
      return;
    }

    setIsPreviewLoading(true);

    try {
      const preprocessing = enablePreprocessing ? {
        resize: {
          size: [resizeWidth, resizeHeight],
          mode: resizeMode
        },
        brightness: brightness,
        contrast: contrast,
        saturation: saturation,
        filters: selectedFilter !== 'none' ? [{
          type: selectedFilter,
          strength: filterStrength
        }] : []
      } : undefined;

      const requestData = {
        input_dir: inputDir,
        rows: rows,
        cols: cols,
        font_size: fontSize,
        margin: margin,
        cell_size: cellSize,
        label_columns: labelColumns,
        csv_path: csvPath || undefined,
        preprocessing: preprocessing,
        background_color: backgroundColor
      };

      const response = await fetch('/api/preview-grid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const result: PreviewResult = await response.json();
      setPreviewResult(result);
    } catch (error) {
      console.error('Error generating preview:', error);
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const handleDownloadResult = () => {
    if (lastResult?.output_path) {
      const link = document.createElement('a');
      link.href = `file://${lastResult.output_path}`;
      link.download = lastResult.output_path.split('/').pop() || 'grid.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const resetForm = () => {
    setInputDir('');
    setOutputPath('');
    setCsvPath('');
    setLabelColumns([]);
    setRows(3);
    setCols(3);
    setFontSize(16);
    setMargin(10);
    setExportFormat('png');
    setBackgroundColor([255, 255, 255]);
    setCellSize([256, 256]);
    setBatchDirs([]);
    setEnablePreprocessing(false);
    setSelectedPreset('default');
    setLastResult(null);
    setPreviewResult(null);
    setProgress(0);
    setProgressMessage('');
  };

  const applyPreset = (presetId: string) => {
    const preset = getPresetById(presetId);
    if (preset) {
      setSelectedPreset(presetId);
      if (preset.settings.rows) setRows(preset.settings.rows);
      if (preset.settings.cols) setCols(preset.settings.cols);
      if (preset.settings.fontSize) setFontSize(preset.settings.fontSize);
      if (preset.settings.margin) setMargin(preset.settings.margin);
      if (preset.settings.labelColumns) setLabelColumns(preset.settings.labelColumns);
    }
  };

  const applyTemplate = (template: GridTemplate) => {
    setRows(template.rows);
    setCols(template.cols);
    setCellSize(template.cell_size);
    setMargin(template.margin);
    setFontSize(template.font_size);
  };

  const saveTemplate = async () => {
    if (!customTemplateName) {
      alert('Please provide a template name');
      return;
    }

    const template = {
      name: customTemplateName,
      rows: rows,
      cols: cols,
      cell_size: cellSize,
      margin: margin,
      font_size: fontSize
    };

    try {
      const response = await fetch('/api/save-grid-template', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template: template,
          filename: customTemplateName
        }),
      });

      const result = await response.json();
      if (result.status === 'success') {
        alert('Template saved successfully!');
        loadTemplates();
      } else {
        alert(`Error saving template: ${result.message}`);
      }
    } catch (error) {
      console.error('Error saving template:', error);
      alert('Failed to save template');
    }
  };

  // Drag & drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const imageFiles = files.filter(file => 
      file.type.startsWith('image/') || 
      ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'].some(ext => 
        file.name.toLowerCase().endsWith(ext)
      )
    );
    
    setDroppedFiles(imageFiles);
    
    // Create a temporary directory path for the dropped files
    if (imageFiles.length > 0) {
      setInputDir(`dropped_files_${Date.now()}`);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setDroppedFiles(files);
    
    if (files.length > 0) {
      setInputDir(`selected_files_${Date.now()}`);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Grid3X3 className="h-8 w-8" />
            Enhanced Grid Exporter
          </h1>
          <p className="text-muted-foreground">
            Create labeled image grids with advanced features
          </p>
        </div>
        <Button onClick={resetForm} variant="outline" size="sm">
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </Button>
      </div>

      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic">Basic</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
          <TabsTrigger value="preprocessing">Preprocessing</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-6">
          {/* Drag & Drop Area */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Drag & Drop Images
              </CardTitle>
              <CardDescription>
                Drop image files here or click to select
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  isDragOver 
                    ? 'border-primary bg-primary/5' 
                    : 'border-muted-foreground/25 hover:border-primary/50'
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">
                  {isDragOver ? 'Drop files here' : 'Drag & drop images here'}
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  or click to browse files
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                {droppedFiles.length > 0 && (
                  <div className="mt-4">
                    <Badge variant="secondary">
                      {droppedFiles.length} file(s) selected
                    </Badge>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Basic Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FolderOpen className="h-5 w-5" />
                  Input Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="input-dir">Input Directory</Label>
                  <Input
                    id="input-dir"
                    value={inputDir}
                    onChange={(e) => setInputDir(e.target.value)}
                    placeholder="Path to image directory"
                  />
                </div>
                <div>
                  <Label htmlFor="csv-path">CSV Metadata (Optional)</Label>
                  <Input
                    id="csv-path"
                    value={csvPath}
                    onChange={(e) => setCsvPath(e.target.value)}
                    placeholder="Path to CSV file with metadata"
                  />
                </div>
                <div>
                  <Label htmlFor="label-columns">Label Columns</Label>
                  <Input
                    id="label-columns"
                    value={labelColumns.join(', ')}
                    onChange={(e) => setLabelColumns(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                    placeholder="Column names separated by commas"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileImage className="h-5 w-5" />
                  Output Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="output-path">Output Path</Label>
                  <Input
                    id="output-path"
                    value={outputPath}
                    onChange={(e) => setOutputPath(e.target.value)}
                    placeholder="Path for output grid image"
                  />
                </div>
                <div>
                  <Label htmlFor="export-format">Export Format</Label>
                  <Select value={exportFormat} onValueChange={setExportFormat}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="png">PNG</SelectItem>
                      <SelectItem value="jpg">JPEG</SelectItem>
                      <SelectItem value="webp">WebP</SelectItem>
                      <SelectItem value="tiff">TIFF</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="background-color">Background Color</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      min="0"
                      max="255"
                      value={backgroundColor[0]}
                      onChange={(e) => setBackgroundColor([parseInt(e.target.value), backgroundColor[1], backgroundColor[2]])}
                      placeholder="R"
                      className="w-20"
                    />
                    <Input
                      type="number"
                      min="0"
                      max="255"
                      value={backgroundColor[1]}
                      onChange={(e) => setBackgroundColor([backgroundColor[0], parseInt(e.target.value), backgroundColor[2]])}
                      placeholder="G"
                      className="w-20"
                    />
                    <Input
                      type="number"
                      min="0"
                      max="255"
                      value={backgroundColor[2]}
                      onChange={(e) => setBackgroundColor([backgroundColor[0], backgroundColor[1], parseInt(e.target.value)])}
                      placeholder="B"
                      className="w-20"
                    />
                    <div 
                      className="w-10 h-10 rounded border"
                      style={{ backgroundColor: `rgb(${backgroundColor.join(',')})` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Presets */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Quick Presets
              </CardTitle>
              <CardDescription>
                Choose from predefined grid layouts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {gridPresets.map((preset) => (
                  <Button
                    key={preset.id}
                    variant={selectedPreset === preset.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => applyPreset(preset.id)}
                    className="justify-start"
                  >
                    {preset.name}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Grid Layout */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Grid3X3 className="h-5 w-5" />
                  Grid Layout
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="rows">Rows</Label>
                    <Input
                      id="rows"
                      type="number"
                      min="1"
                      value={rows}
                      onChange={(e) => setRows(parseInt(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cols">Columns</Label>
                    <Input
                      id="cols"
                      type="number"
                      min="1"
                      value={cols}
                      onChange={(e) => setCols(parseInt(e.target.value))}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="cell-width">Cell Width</Label>
                    <Input
                      id="cell-width"
                      type="number"
                      min="50"
                      value={cellSize[0]}
                      onChange={(e) => setCellSize([parseInt(e.target.value), cellSize[1]])}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cell-height">Cell Height</Label>
                    <Input
                      id="cell-height"
                      type="number"
                      min="50"
                      value={cellSize[1]}
                      onChange={(e) => setCellSize([cellSize[0], parseInt(e.target.value)])}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="margin">Margin</Label>
                  <Slider
                    value={[margin]}
                    onValueChange={([value]) => setMargin(value)}
                    min={0}
                    max={50}
                    step={1}
                    className="w-full"
                  />
                  <span className="text-sm text-muted-foreground">{margin}px</span>
                </div>
                <div>
                  <Label htmlFor="font-size">Font Size</Label>
                  <Slider
                    value={[fontSize]}
                    onValueChange={([value]) => setFontSize(value)}
                    min={8}
                    max={32}
                    step={1}
                    className="w-full"
                  />
                  <span className="text-sm text-muted-foreground">{fontSize}px</span>
                </div>
              </CardContent>
            </Card>

            {/* Templates */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="h-5 w-5" />
                  Templates
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="template-select">Load Template</Label>
                  <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a template" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.map((template) => (
                        <SelectItem key={template.name} value={template.name}>
                          {template.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedTemplate && (
                    <Button
                      size="sm"
                      onClick={() => {
                        const template = templates.find(t => t.name === selectedTemplate);
                        if (template) applyTemplate(template);
                      }}
                      className="mt-2"
                    >
                      Apply Template
                    </Button>
                  )}
                </div>
                <Separator />
                <div>
                  <Label htmlFor="template-name">Save Current as Template</Label>
                  <div className="flex gap-2">
                    <Input
                      id="template-name"
                      value={customTemplateName}
                      onChange={(e) => setCustomTemplateName(e.target.value)}
                      placeholder="Template name"
                    />
                    <Button size="sm" onClick={saveTemplate}>
                      <Save className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Batch Processing */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Batch Processing
              </CardTitle>
              <CardDescription>
                Process multiple directories at once
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="batch-dirs">Batch Directories</Label>
                  <Textarea
                    id="batch-dirs"
                    value={batchDirs.join('\n')}
                    onChange={(e) => setBatchDirs(e.target.value.split('\n').filter(Boolean))}
                    placeholder="Enter directory paths, one per line"
                    rows={3}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  When batch directories are provided, the output path will be used as the base directory for all results.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preprocessing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Adjustments className="h-5 w-5" />
                Image Preprocessing
              </CardTitle>
              <CardDescription>
                Apply transformations to images before creating the grid
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center space-x-2">
                <Switch
                  checked={enablePreprocessing}
                  onCheckedChange={setEnablePreprocessing}
                />
                <Label>Enable preprocessing</Label>
              </div>

              {enablePreprocessing && (
                <div className="space-y-6">
                  {/* Resize */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center gap-2">
                      <Crop className="h-4 w-4" />
                      Resize
                    </h4>
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="resize-width">Width</Label>
                        <Input
                          id="resize-width"
                          type="number"
                          min="50"
                          value={resizeWidth}
                          onChange={(e) => setResizeWidth(parseInt(e.target.value))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="resize-height">Height</Label>
                        <Input
                          id="resize-height"
                          type="number"
                          min="50"
                          value={resizeHeight}
                          onChange={(e) => setResizeHeight(parseInt(e.target.value))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="resize-mode">Mode</Label>
                        <Select value={resizeMode} onValueChange={setResizeMode}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="fit">Fit</SelectItem>
                            <SelectItem value="fill">Fill</SelectItem>
                            <SelectItem value="stretch">Stretch</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Adjustments */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center gap-2">
                      <PaletteIcon className="h-4 w-4" />
                      Adjustments
                    </h4>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="brightness">Brightness</Label>
                        <Slider
                          value={[brightness]}
                          onValueChange={([value]) => setBrightness(value)}
                          min={0.1}
                          max={3.0}
                          step={0.1}
                          className="w-full"
                        />
                        <span className="text-sm text-muted-foreground">{brightness.toFixed(1)}x</span>
                      </div>
                      <div>
                        <Label htmlFor="contrast">Contrast</Label>
                        <Slider
                          value={[contrast]}
                          onValueChange={([value]) => setContrast(value)}
                          min={0.1}
                          max={3.0}
                          step={0.1}
                          className="w-full"
                        />
                        <span className="text-sm text-muted-foreground">{contrast.toFixed(1)}x</span>
                      </div>
                      <div>
                        <Label htmlFor="saturation">Saturation</Label>
                        <Slider
                          value={[saturation]}
                          onValueChange={([value]) => setSaturation(value)}
                          min={0.0}
                          max={3.0}
                          step={0.1}
                          className="w-full"
                        />
                        <span className="text-sm text-muted-foreground">{saturation.toFixed(1)}x</span>
                      </div>
                    </div>
                  </div>

                  <Separator />

                  {/* Filters */}
                  <div className="space-y-4">
                    <h4 className="font-medium flex items-center gap-2">
                      <Filter className="h-4 w-4" />
                      Filters
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="filter-type">Filter Type</Label>
                        <Select value={selectedFilter} onValueChange={setSelectedFilter}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="none">None</SelectItem>
                            <SelectItem value="blur">Blur</SelectItem>
                            <SelectItem value="sharpen">Sharpen</SelectItem>
                            <SelectItem value="emboss">Emboss</SelectItem>
                            <SelectItem value="edge_enhance">Edge Enhance</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="filter-strength">Strength</Label>
                        <Slider
                          value={[filterStrength]}
                          onValueChange={([value]) => setFilterStrength(value)}
                          min={0.1}
                          max={5.0}
                          step={0.1}
                          className="w-full"
                        />
                        <span className="text-sm text-muted-foreground">{filterStrength.toFixed(1)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="preview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Real-time Preview
              </CardTitle>
              <CardDescription>
                Preview the grid layout before generating
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={handlePreview} 
                disabled={!inputDir || isPreviewLoading}
                className="w-full"
              >
                {isPreviewLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating Preview...
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    Generate Preview
                  </>
                )}
              </Button>

              {previewResult && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Images Found:</span> {previewResult.images_found}
                    </div>
                    <div>
                      <span className="font-medium">Images in Preview:</span> {previewResult.images_in_preview}
                    </div>
                    <div>
                      <span className="font-medium">Grid Dimensions:</span> {previewResult.grid_dimensions}
                    </div>
                    <div>
                      <span className="font-medium">Canvas Size:</span> {previewResult.canvas_size}
                    </div>
                  </div>
                  
                  {previewResult.preview_image && (
                    <div className="border rounded-lg p-4">
                      <img 
                        src={previewResult.preview_image} 
                        alt="Grid Preview"
                        className="max-w-full h-auto mx-auto"
                      />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Progress and Results */}
      {(isLoading || progress > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              Processing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Progress value={progress} className="w-full" />
            <p className="text-sm text-muted-foreground">{progressMessage}</p>
          </CardContent>
        </Card>
      )}

      {lastResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {lastResult.status === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-500" />
              )}
              {lastResult.status === 'success' ? 'Success' : 'Error'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm">{lastResult.message}</p>
            
            {lastResult.status === 'success' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Images Processed:</span>
                    <br />
                    {lastResult.images_processed}
                  </div>
                  <div>
                    <span className="font-medium">Grid Dimensions:</span>
                    <br />
                    {lastResult.grid_dimensions}
                  </div>
                  <div>
                    <span className="font-medium">Canvas Size:</span>
                    <br />
                    {lastResult.canvas_size}
                  </div>
                  <div>
                    <span className="font-medium">File Size:</span>
                    <br />
                    {lastResult.file_size_bytes ? `${(lastResult.file_size_bytes / 1024).toFixed(1)} KB` : 'Unknown'}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button onClick={handleDownloadResult} className="flex-1">
                    <Download className="h-4 w-4 mr-2" />
                    Download Result
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Grid Button */}
      <div className="flex justify-center">
        <Button 
          onClick={handleCreateGrid} 
          disabled={!inputDir || !outputPath || isLoading}
          size="lg"
          className="px-8"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Creating Grid...
            </>
          ) : (
            <>
              <Grid3X3 className="h-5 w-5 mr-2" />
              Create Grid
            </>
          )}
        </Button>
      </div>

      {/* How to Use */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            How to Use
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium mb-2">Basic Usage</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Drag & drop images or select input directory</li>
                <li>• Set output path for the grid image</li>
                <li>• Choose export format (PNG, JPEG, WebP, TIFF)</li>
                <li>• Select a preset or customize grid layout</li>
                <li>• Click "Create Grid" to generate</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">Advanced Features</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Use CSV metadata for image labels</li>
                <li>• Apply image preprocessing (resize, filters, adjustments)</li>
                <li>• Batch process multiple directories</li>
                <li>• Save and load custom templates</li>
                <li>• Real-time preview before generation</li>
              </ul>
            </div>
          </div>
          
          <Separator />
          
          <div>
            <h4 className="font-medium mb-2">Tips</h4>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>• Use the preview feature to see how your grid will look</li>
              <li>• For large images, enable preprocessing to resize them</li>
              <li>• Save frequently used settings as templates</li>
              <li>• Use batch processing for multiple image sets</li>
              <li>• Experiment with different export formats for file size vs quality</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GridExporter; 