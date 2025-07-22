
import React, { useState, useCallback } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import Slider from "@/components/Slider";
import { fetchUpscalerModels } from "@/services/modelService";
import { useModelRefresh } from "@/hooks/useModelRefresh";

const SDUpscalerSettings = () => {
  const [tileOverlap, setTileOverlap] = useState(32);
  const [scaleFactor, setScaleFactor] = useState(2.0);
  const [selectedModel, setSelectedModel] = useState("RealESRGAN_x4plus.pth");
  const [models, setModels] = useState([]);

  const loadUpscalerModels = useCallback(async () => {
    try {
      const models = await fetchUpscalerModels();
      setModels(models);
    } catch (error) {
      console.error('Error fetching upscaler models:', error);
    }
  }, []);

  // Use WebSocket auto-refresh hook for upscaler models
  useModelRefresh(loadUpscalerModels, 'upscale_models');

  const modelData = models.find(m => m.id === selectedModel);

  return (
    <div className="space-y-4 mt-2">
      <Slider
        min={0}
        max={64}
        defaultValue={tileOverlap}
        label="a) Tile Overlap | <span class='text-muted-foreground'>Optimal Level: 32-64</span>"
        onChange={setTileOverlap}
        step={1}
      />
      
      <Slider
        min={1}
        max={4}
        defaultValue={scaleFactor}
        label="b) Scale Factor | <span class='text-muted-foreground'>Optimal Level: 1.5-2</span>"
        onChange={setScaleFactor}
        step={0.1}
      />
      
      <div className="space-y-2">
        <label className="text-sm font-medium text-foreground">c) Upscaling Model</label>
        <Select value={selectedModel} onValueChange={setSelectedModel}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {models.map((model) => (
              <SelectItem key={model.id} value={model.id}>
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        {modelData && (
          <div className="mt-2 p-3 bg-card border border-border rounded-md">
            <p className="text-sm text-muted-foreground">
              <strong>Selected Model:</strong> {modelData.name}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SDUpscalerSettings;
