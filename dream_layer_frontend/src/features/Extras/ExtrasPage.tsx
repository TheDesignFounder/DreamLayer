import React, { useState, useEffect, useCallback } from 'react';
import Accordion from '@/components/Accordion';
import Slider from '@/components/Slider';
import SubTabNavigation from '@/components/SubTabNavigation';
import SizingSettings from '@/components/SizingSettings';
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import upscalingModels, { UpscalingModelData } from "@/components/advanced-settings/models/upscalingModels";
import { ExtrasRequest, ExtrasResponse } from './types';
import { toast } from 'sonner';
import ImageUploadButton from '@/components/ImageUploadButton';
import { fetchUpscalerModels } from "@/services/modelService";
import { useModelRefresh } from "@/hooks/useModelRefresh";

const ExtrasPage = () => {
  const [activeSubTab, setActiveSubTab] = useState("upscale");
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedImage, setProcessedImage] = useState<string | null>(null);
  const [availableUpscalers, setAvailableUpscalers] = useState([]);
  
  // New state for advanced upscaling options
  const [upscaleMethod, setUpscaleMethod] = useState("upscale-by");
  const [upscaleFactor, setUpscaleFactor] = useState(2.5);
  const [selectedUpscaler, setSelectedUpscaler] = useState("Real_ESRGAN_x4plus");
  const [selectedUpscaler2, setSelectedUpscaler2] = useState("4x-ultrasharp");
  const [resizeWidth, setResizeWidth] = useState(1024);
  const [resizeHeight, setResizeHeight] = useState(1024);
  
  // New state for the 4 sliders
  const [upscaler2Visibility, setUpscaler2Visibility] = useState(0.25);
  const [gfpganVisibility, setGfpganVisibility] = useState(0.8);
  const [codeformerVisibility, setCodeformerVisibility] = useState(0.7);
  const [codeformerWeight, setCodeformerWeight] = useState(0.2);

  const subtabs = [
    { id: "upscale", label: "Single Image", active: activeSubTab === "upscale" },
  ];

  const handleSubTabChange = (tabId: string) => {
    setActiveSubTab(tabId);
  };

  const loadUpscalerModels = useCallback(async () => {
    try {
      const models = await fetchUpscalerModels();
      setAvailableUpscalers(models);
    } catch (error) {
      console.error('Error fetching upscaler models:', error);
    }
  }, []);

  // Use WebSocket auto-refresh hook for upscaler models
  useModelRefresh(loadUpscalerModels, 'upscale_models');

  useEffect(() => {
    // Check for image from txt2img
    const extrasImageStr = window.sessionStorage.getItem('extrasImage');
    if (extrasImageStr) {
      try {
        const extrasImage = JSON.parse(extrasImageStr);
        setImagePreview(extrasImage.preview);

        // Create a new File object
        fetch(extrasImage.preview)
          .then(r => r.blob())
          .then(blob => {
            const file = new File([blob], extrasImage.file.name, {
              type: extrasImage.file.type
            });
            setSelectedImage(file);
          });

        // Clear the storage
        window.sessionStorage.removeItem('extrasImage');
      } catch (error) {
        console.error('Error loading image from storage:', error);
      }
    }
  }, []);

  // Get current upscaler information
  const currentUpscaler: UpscalingModelData = upscalingModels[selectedUpscaler] || upscalingModels["4x-ultrasharp"];
  const currentUpscaler2: UpscalingModelData = upscalingModels[selectedUpscaler2] || upscalingModels["4x-ultrasharp"];
  
  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setProcessedImage(null);
      // Create a URL for the image preview
      const url = URL.createObjectURL(file);
      setImagePreview(url);
    }
  };

  // Add cleanup for the image preview URL
  React.useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const handleGenerate = async () => {
    if (!selectedImage) {
      toast.error("Please select an image first");
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      
      // Create request params without the File object
      const params = {
        upscaler_model: selectedUpscaler,
        upscaler_visibility: 1,
        upscaler_model_2: selectedUpscaler2,
        upscaler_visibility_2: upscaler2Visibility,
        gfpgan_visibility: gfpganVisibility,
        codeformer_visibility: codeformerVisibility,
        codeformer_weight: codeformerWeight,
        output_format: 'PNG'
      };

      formData.append('params', JSON.stringify(params));

      const response = await fetch('http://localhost:5003/api/extras/upscale', {
        method: 'POST',
        body: formData
      });

      const result: ExtrasResponse = await response.json();

      if (result.status === 'success' && result.data) {
        setProcessedImage(result.data.output_image);
        toast.success("Image processed successfully!");
      } else {
        throw new Error(result.message || 'Failed to process image');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to process image');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderUpscalingOptions = () => {
    return (
      <div className="space-y-4 mb-4">
        {activeSubTab === "upscale" && (
          <div className="mb-4">
            {imagePreview ? (
              <div className="relative">
                <img 
                  src={imagePreview} 
                  alt="Selected image" 
                  className="rounded-md object-cover w-full aspect-square border border-border"
                />
                <div className="absolute bottom-2 right-2 flex gap-1">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="bg-background/80 backdrop-blur-sm border-border text-foreground hover:bg-accent"
                    onClick={() => {
                      setSelectedImage(null);
                      setImagePreview(null);
                    }}
                  >
                    Clear
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-4 border-2 border-dashed border-border rounded-md text-center flex flex-col items-center justify-center aspect-square bg-card">
                <p className="text-muted-foreground mb-2">Drag & drop an image here or click to browse</p>
                <p className="text-xs text-muted-foreground mb-4">PNG, JPG, WEBP or GIF up to 10MB</p>
                <ImageUploadButton onFileChange={handleImageUpload}>
                  Browse Files
                </ImageUploadButton>
              </div>
            )}
          </div>
        )}
        
        <div className="mt-4 mb-3">
          <div className="text-sm font-medium text-foreground mb-2">a) Set Upscale Size:</div>
          <RadioGroup 
            value={upscaleMethod} 
            onValueChange={setUpscaleMethod}
            className="grid grid-cols-2 gap-3"
          >
            <div className="relative">
              <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${upscaleMethod === "upscale-by" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                <RadioGroupItem id="upscale-by" value="upscale-by" className="h-4 w-4" />
                <label htmlFor="upscale-by" className="text-sm font-medium cursor-pointer w-full">Upscale by</label>
              </Card>
            </div>
            
            <div className="relative">
              <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${upscaleMethod === "resize-to" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                <RadioGroupItem id="resize-to" value="resize-to" className="h-4 w-4" />
                <label htmlFor="resize-to" className="text-sm font-medium cursor-pointer w-full">Resize to</label>
              </Card>
            </div>
          </RadioGroup>
        </div>
        
        {upscaleMethod === "upscale-by" ? (
          <div className="mb-6">
            <Slider
              min={1}
              max={10}
              step={0.1}
              defaultValue={upscaleFactor}
              label="Upscale"
              onChange={(value) => setUpscaleFactor(value)}
              inputWidth="w-16"
            />
          </div>
        ) : (
          <div className="my-6">
            <SizingSettings 
              widthValue={resizeWidth} 
              heightValue={resizeHeight}
              onWidthChange={setResizeWidth}
              onHeightChange={setResizeHeight}
            />
          </div>
        )}
        
        <div className="my-6">
          <div className="text-sm font-medium text-foreground mb-2">b) Upscaling Model #1</div>
          <Select 
            defaultValue={selectedUpscaler} 
            onValueChange={(value) => setSelectedUpscaler(value)}
          >
            <SelectTrigger className="w-full" id="upscaling-model">
              <SelectValue placeholder="Select an upscaling model" />
            </SelectTrigger>
            <SelectContent>
              {availableUpscalers.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="mt-4 mx-4 text-sm text-muted-foreground">
            <p className="mb-1">
              <span className="font-medium">About The Upscaler:</span> {currentUpscaler.description} Speed: {currentUpscaler.speed}.
            </p>
          </div>
        </div>

        <div className="my-6">
          <div className="text-sm font-medium text-foreground mb-2">c) Upscaling Model #2</div>
          <Select 
            defaultValue={selectedUpscaler2} 
            onValueChange={(value) => setSelectedUpscaler2(value)}
          >
            <SelectTrigger className="w-full" id="upscaling-model-2">
              <SelectValue placeholder="Select an upscaling model" />
            </SelectTrigger>
            <SelectContent>
              {availableUpscalers.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  {model.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="mt-4 mx-4 text-sm text-muted-foreground">
            <p className="mb-1">
              <span className="font-medium">About The Upscaler:</span> {currentUpscaler2.description} Speed: {currentUpscaler2.speed}.
            </p>
          </div>
        </div>
          
        <div className="mt-6">
          <Slider
            min={0}
            max={1}
            step={0.05}
            defaultValue={upscaler2Visibility}
            label={`d) Upscaler 2 visibility | <span style='color: #64748B;'>Optimal Level: 0.25</span>`}
            onChange={(value) => setUpscaler2Visibility(value)}
            inputWidth="w-16"
          />
        </div>
        
        <div className="mt-6">
          <Slider
            min={0}
            max={1}
            step={0.05}
            defaultValue={gfpganVisibility}
            label={`e) GFPGAN visibility | <span style='color: #64748B;'>Optimal Level: 0.8</span>`}
            onChange={(value) => setGfpganVisibility(value)}
            inputWidth="w-16"
          />
        </div>
        
        <div className="mt-6">
          <Slider
            min={0}
            max={1}
            step={0.05}
            defaultValue={codeformerVisibility}
            label={`f) CodeFormer visibility | <span style='color: #64748B;'>Optimal Level: 0.7</span>`}
            onChange={(value) => setCodeformerVisibility(value)}
            inputWidth="w-16"
          />
        </div>
        
        <div className="mt-6">
          <Slider
            min={0}
            max={1}
            step={0.05}
            defaultValue={codeformerWeight}
            label={`g) CodeFormer weight | <span style='color: #64748B;'>Optimal Level: 0.2</span>`}
            onChange={(value) => setCodeformerWeight(value)}
            inputWidth="w-16"
          />
        </div>
      </div>
    );
  };
  
  const renderSubTabContent = () => {
    switch (activeSubTab) {
      case "batch":
        return (
          <div className="space-y-4 mb-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="font-medium text-sm">Input Directory - Batch image processing</div>
                <Button 
                  size="sm" 
                  className="text-xs"
                  style={{ height: '34px' }}
                >
                  Browse Batch Files
                </Button>
              </div>
              <Textarea 
                placeholder="Specify a folder containing reference images"
                className="min-h-[100px]"
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="batchOperation" className="mb-1 block text-sm">Batch Operation:</label>
              <select id="batchOperation" className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                <option value="resize">Resize All</option>
                <option value="upscale">Upscale All</option>
                <option value="convert">Convert Format</option>
                <option value="enhance">Enhance All</option>
              </select>
            </div>
            
            {renderUpscalingOptions()}
          </div>
        );
      default:
        // "upscale" tab (default) - Single Image
        return renderUpscalingOptions();
    }
  };

  return (
    <div className="mb-4 grid gap-6 md:grid-cols-[2fr_1fr]">
      {/* Left Column - Controls */}
      <div className="space-y-4">
        <div className="flex flex-col">
          <div className="mb-[18px] flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <h3 className="text-base font-medium">Image Post-Processing</h3>
            <div className="flex space-x-2">
              <Button 
                onClick={handleGenerate}
                disabled={!selectedImage || isProcessing}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
              >
                {isProcessing ? 'Processing...' : 'Generate Image'}
              </Button>
            </div>
          </div>
          
          <SubTabNavigation 
            className="mb-[18px]"
            tabs={subtabs} 
            onTabChange={handleSubTabChange}
          />
          
          <Accordion title={activeSubTab === "upscale" ? "Upscaling Options" : "Batch Options"} 
                     number={activeSubTab === "upscale" ? "1" : "1"} 
                     defaultOpen={true}>
            {renderSubTabContent()}
          </Accordion>
        </div>
      </div>
      
      {/* Right Column - Preview */}
      <div>
        <div className="rounded-md border border-border p-4 h-[500px] flex items-center justify-center">
          {processedImage ? (
            <img 
              src={processedImage} 
              alt="Processed" 
              className="max-w-full max-h-full object-contain"
            />
          ) : (
            <div className="text-center">
              <p className="text-muted-foreground">
                {selectedImage ? 'Click Generate to process the image' : 'Processed image will display here'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExtrasPage;
