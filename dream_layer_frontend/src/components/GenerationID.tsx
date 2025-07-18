import React, { useState } from "react";
import Slider from "./Slider";
import { Button } from "./ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { ChevronDown } from "lucide-react";

interface GenerationIDProps {
  seed: number;
  random: boolean;
  onChange: (seed: number, random?: boolean) => void;
}

const GenerationID: React.FC<GenerationIDProps> = ({
  seed,
  random,
  onChange,
}) => {
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [widthValue, setWidthValue] = useState(2500);
  const [heightValue, setHeightValue] = useState(2500);
  const [variationStrength, setVariationStrength] = useState(0.5);

  const getVariationStrengthLabel = () => {
    return "b) Variation Strength";
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium">Generation Seed</label>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-gray-300"
            checked={random}
            onChange={(e) => onChange(seed, e.target.checked)}
          />
          <span className="text-sm">Random</span>
        </div>
      </div>
      <input
        type="number"
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        value={seed}
        onChange={(e) => onChange(parseInt(e.target.value), random)}
        disabled={random}
      />
      
      {/* Advanced seed features collapsible */}
      <Collapsible
        open={isAdvancedOpen}
        onOpenChange={setIsAdvancedOpen}
        className="rounded-md"
      >
        <CollapsibleTrigger className="flex items-center justify-between w-full p-2 hover:bg-accent rounded-md text-left mb-2 hidden">
          <div className="flex items-center gap-2">
            <ChevronDown className={`h-4 w-4 transition-transform ${isAdvancedOpen ? "transform rotate-180" : ""}`} />
            <span className="font-medium text-xs">Advanced Seed Features</span>
          </div>
        </CollapsibleTrigger>
        
        <CollapsibleContent className="px-3 pb-3">
          <p className="mb-4 text-sm text-muted-foreground">
            Generate subtle image variations while keeping the core idea intact. Blend in 
            randomness with the alternative seed and strength, and use resize options to 
            stay consistent across different image sizes.
          </p>
          
          {/* Variation Seed section */}
          <div className="space-y-4 mb-6">
            <div>
              {/* Rearranged layout to align title with input and buttons horizontally */}
              <div className="flex items-center justify-between mb-3">
                <h5 className="font-medium text-sm text-[#020817]">a) Variation Seed</h5>
                <div className="flex space-x-2">
                  <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground">
                    Randomize
                  </button>
                  <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground">
                    Reuse
                  </button>
                </div>
              </div>
              <input
                type="text"
                defaultValue="1234567"
                placeholder="Enter variation seed"
                className="w-full rounded-md border border-input bg-background p-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            
            {/* Variation Strength slider - Updated to use the same format as Batch Size */}
            <Slider
              min={0}
              max={1}
              defaultValue={0.5}
              label={getVariationStrengthLabel()}
              step={0.1}
              onChange={setVariationStrength}
            />
          </div>
          
          {/* Resize Seed section - Updated to use the Slider component */}
          <div className="space-y-4">
            <h5 className="font-medium text-sm mb-2 text-[#020817]">c) Resize Seed for:</h5>
            
            {/* Width slider - Using the Slider component */}
            <Slider
              min={0}
              max={5000}
              defaultValue={2500}
              label="Width (px)"
              onChange={setWidthValue}
              inputWidth="w-24"
            />
            
            {/* Height slider - Using the Slider component */}
            <Slider
              min={0}
              max={5000}
              defaultValue={2500}
              label="Height (px)"
              onChange={setHeightValue}
              inputWidth="w-24"
            />
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
};

export default GenerationID;
