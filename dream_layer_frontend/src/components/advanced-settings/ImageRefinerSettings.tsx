
import React from "react";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Slider from "@/components/Slider";
import refinerModels, { RefinerModelData } from "./models/refinerModels";

interface ImageRefinerSettingsProps {
  selectedRefiner: string;
  setSelectedRefiner: (value: string) => void;
  refineSwitchAt: number;
  setRefineSwitchAt: (value: number) => void;
}

const ImageRefinerSettings: React.FC<ImageRefinerSettingsProps> = ({
  selectedRefiner,
  setSelectedRefiner,
  refineSwitchAt,
  setRefineSwitchAt,
}) => {
  // Get current refiner information
  const currentRefiner: RefinerModelData = refinerModels[selectedRefiner] || refinerModels["none"];
  
  // Get optimal switch at range label
  const getOptimalSwitchLabel = () => {
    return `b) Switch at | <span style='color: #64748B;'>Optimal Level: ${currentRefiner.optimalSwitchMin}–${currentRefiner.optimalSwitchMax}</span>`;
  };

  return (
    <>
      <div className="mt-2 mx-4 text-xs text-muted-foreground mb-4">
        <p className="mb-1">
          <span className="font-medium">How it works:</span> The Base Model builds the layout of the image (e.g, shapes, people, and background). Then, the Refiner Model takes over to polish the final details (e.g, sharpening faces, fixing textures, and improving realism).
        </p>
      </div>
      
      <div className="my-3">
        <label htmlFor="refiner-model" className="text-sm font-medium">a) Checkpoint - Refiner Model</label>
        <Select 
          defaultValue={selectedRefiner}
          onValueChange={(value) => setSelectedRefiner(value)}
        >
          <SelectTrigger className="w-full mt-1" id="refiner-model">
            <SelectValue placeholder="Select a refiner model" />
          </SelectTrigger>
          <SelectContent>
            {Object.values(refinerModels).map((model) => (
              <SelectItem key={model.id} value={model.id}>
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        {selectedRefiner !== "none" && (
          <div className="mt-4 mx-4 text-sm text-muted-foreground">
            <p className="mb-1">
              <span className="font-medium">About this Refiner:</span> {currentRefiner.description} <span className="font-medium">Speed:</span> {currentRefiner.speed}.
            </p>
          </div>
        )}
      </div>
      
      <div className="my-3 mt-5">
        <Slider
          min={0}
          max={1}
          step={0.05}
          defaultValue={refineSwitchAt}
          label={getOptimalSwitchLabel()}
          onChange={(value) => setRefineSwitchAt(value)}
          inputWidth="w-16"
          tooltipKey="refinerSwitchAt"
        />
        <div className="mt-0 ml-2 text-sm text-muted-foreground">
          Choose when the image generation switches from the Base Model to the Refiner Model.
        </div>
      </div>
    </>
  );
};

export default ImageRefinerSettings;
