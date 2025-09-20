import React, { useState, useCallback } from "react";
import { RefreshCw } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { preprocessors } from "./controlnet-data";
import { useModelRefresh } from "@/hooks/useModelRefresh";

interface PreprocessorModelSelectorProps {
  unitIndex: number;
  selectedPreprocessor: string;
  setSelectedPreprocessor: (preprocessor: string) => void;
  selectedModel: string;
  setSelectedModel: (model: string) => void;
}

const PreprocessorModelSelector: React.FC<PreprocessorModelSelectorProps> = ({
  unitIndex,
  selectedPreprocessor,
  setSelectedPreprocessor,
  selectedModel,
  setSelectedModel,
}) => {
  const [models, setModels] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchModels = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5001/api/controlnet/models');
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success') {
          setModels(data.models);
        } else {
          console.error('Failed to fetch models:', data.message);
        }
      } else {
        console.error('Failed to fetch models:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching ControlNet models:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Use WebSocket auto-refresh hook for ControlNet models
  useModelRefresh(fetchModels, 'controlnet');

  const handleRefreshModels = () => {
    fetchModels();
  };

  return (
    <div className="grid grid-cols-2 gap-4 p-4 border-t border-input">
      <div>
        <Label htmlFor={`unit-${unitIndex}-preprocessor`} className="text-sm mb-1.5 block">Preprocessor</Label>
        <Select value={selectedPreprocessor} onValueChange={setSelectedPreprocessor}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select preprocessor" />
          </SelectTrigger>
          <SelectContent>
            {preprocessors.map((preprocessor) => (
              <SelectItem key={preprocessor.id} value={preprocessor.id}>
                {preprocessor.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <Label htmlFor={`unit-${unitIndex}-model`} className="text-sm mb-1.5 block">Model</Label>
        <div className="flex items-center gap-2">
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button 
            size="sm" 
            variant="outline" 
            className="w-[30px] h-[30px] p-0" 
            onClick={handleRefreshModels}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PreprocessorModelSelector;
