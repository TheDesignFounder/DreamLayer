
import React from "react";
import { Label } from "@/components/ui/label";
import { preprocessorsWithThresholds } from "./controlnet-data";
import { Slider } from "@/components/ui/slider";
import { SliderTooltip } from "@/components/SliderTooltip";

interface ThresholdControlsProps {
  unitIndex: number;
  selectedPreprocessor: string;
  thresholdA: number;
  setThresholdA: (value: number) => void;
  thresholdB: number;
  setThresholdB: (value: number) => void;
}

const ThresholdControls: React.FC<ThresholdControlsProps> = ({
  unitIndex,
  selectedPreprocessor,
  thresholdA,
  setThresholdA,
  thresholdB,
  setThresholdB,
}) => {
  // Check if current preprocessor supports thresholds
  const showThresholds = () => {
    return preprocessorsWithThresholds.some(id => selectedPreprocessor.includes(id));
  };

  if (!showThresholds()) {
    return null;
  }

  return (
    <div className="p-4 border-t border-input">
      <div className="flex items-center justify-between mb-2">
        <Label className="text-sm font-medium">Preprocessor Parameters</Label>
      </div>
      
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium flex items-center gap-2">
            <span>Threshold A</span>
            <SliderTooltip tooltipKey="thresholdA" />
          </div>
          <div className="flex items-center text-xs">
            <span className="mr-1 text-muted-foreground">Min: 0</span>
            <span className="mx-1 text-muted-foreground">Max: 255</span>
            <input 
              type="number" 
              value={thresholdA} 
              onChange={(e) => setThresholdA(Number(e.target.value))}
              className="rounded-md border border-input bg-background px-2 py-1 text-right text-xs w-16"
              min={0}
              max={255}
              step={1}
            />
          </div>
        </div>
        <div className="py-2">
          <Slider
            min={0}
            max={255}
            step={1}
            value={[thresholdA]}
            onValueChange={(value) => setThresholdA(value[0])}
          />
        </div>
      </div>
      
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium flex items-center gap-2">
            <span>Threshold B</span>
            <SliderTooltip tooltipKey="thresholdB" />
          </div>
          <div className="flex items-center text-xs">
            <span className="mr-1 text-muted-foreground">Min: 0</span>
            <span className="mx-1 text-muted-foreground">Max: 255</span>
            <input 
              type="number" 
              value={thresholdB} 
              onChange={(e) => setThresholdB(Number(e.target.value))}
              className="rounded-md border border-input bg-background px-2 py-1 text-right text-xs w-16"
              min={0}
              max={255}
              step={1}
            />
          </div>
        </div>
        <div className="py-2">
          <Slider
            min={0}
            max={255}
            step={1}
            value={[thresholdB]}
            onValueChange={(value) => setThresholdB(value[0])}
          />
        </div>
      </div>
    </div>
  );
};

export default ThresholdControls;
