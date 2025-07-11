
import React from "react";
import Slider from "@/components/Slider";

interface ControlParametersProps {
  unitIndex: number;
  weight: number;
  setWeight: (weight: number) => void;
  guidanceStart: number;
  setGuidanceStart: (guidanceStart: number) => void;
  guidanceEnd: number;
  setGuidanceEnd: (guidanceEnd: number) => void;
  resolution: number;
  setResolution: (resolution: number) => void;
}

const ControlParameters: React.FC<ControlParametersProps> = ({
  unitIndex,
  weight,
  setWeight,
  guidanceStart,
  setGuidanceStart,
  guidanceEnd,
  setGuidanceEnd,
  resolution,
  setResolution,
}) => {
  return (
    <div className="p-4 border-t border-input">
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm font-medium">
          Advanced Control Options
        </div>
      </div>
      
      {/* Weight Control */}
      <Slider
        min={0}
        max={2}
        step={0.05}
        defaultValue={weight}
        label="Control Weight"
        onChange={setWeight}
        inputWidth="w-16"
        tooltipKey="controlWeight"
      />
      
      {/* Guidance Start/End in a grid */}
      <div className="grid grid-cols-2 gap-4">
        <Slider
          min={0}
          max={1}
          step={0.05}
          defaultValue={guidanceStart}
          label="Starting Control Step"
          onChange={setGuidanceStart}
          inputWidth="w-16"
          tooltipKey="guidanceStart"
        />
        
        <Slider
          min={0}
          max={1}
          step={0.05}
          defaultValue={guidanceEnd}
          label="Ending Control Step"
          onChange={setGuidanceEnd}
          inputWidth="w-16"
          tooltipKey="guidanceEnd"
        />
      </div>
      
      {/* Resolution */}
      <Slider
        min={64}
        max={2048}
        step={64}
        defaultValue={resolution}
        label="Resolution"
        onChange={setResolution}
        inputWidth="w-16"
        tooltipKey="processorRes"
      />
    </div>
  );
};

export default ControlParameters;
