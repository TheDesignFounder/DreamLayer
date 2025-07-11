
import React from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import Slider from "@/components/Slider";

interface FaceRestorationSettingsProps {
  faceRestorationModel: string;
  setFaceRestorationModel: (value: string) => void;
  codeformerWeight: number;
  setCodeformerWeight: (value: number) => void;
  gfpganWeight: number;
  setGfpganWeight: (value: number) => void;
}

const FaceRestorationSettings: React.FC<FaceRestorationSettingsProps> = ({
  faceRestorationModel,
  setFaceRestorationModel,
  codeformerWeight,
  setCodeformerWeight,
  gfpganWeight,
  setGfpganWeight,
}) => {
  return (
    <div className="mt-2">
      <div className="mb-2">
        <div className="text-sm font-medium text-foreground">a) Pick a Face Restoration Model</div>
      </div>
      <RadioGroup 
        value={faceRestorationModel} 
        onValueChange={setFaceRestorationModel}
        className="grid grid-cols-2 gap-3"
      >
        <div className="flex items-start gap-3 border border-gray-200 rounded-md p-3">
          <RadioGroupItem id="codeformer" value="codeformer" className="mt-1" />
          <div className="flex flex-col">
            <label htmlFor="codeformer" className="text-sm font-medium">CodeFormer</label>
            <p className="text-xs text-muted-foreground">For fixing artistic or stylized portraits where you want faces to look natural and balanced</p>
          </div>
        </div>
        
        <div className="flex items-start gap-3 border border-gray-200 rounded-md p-3">
          <RadioGroupItem id="gfpgan" value="gfpgan" className="mt-1" />
          <div className="flex flex-col">
            <label htmlFor="gfpgan" className="text-sm font-medium">GFPGAN</label>
            <p className="text-xs text-muted-foreground">For quickly fix distorted or low-quality faces in messy generations.</p>
          </div>
        </div>
      </RadioGroup>
      
      {faceRestorationModel === "codeformer" && (
        <div className="mt-4">
          <Slider
            min={0}
            max={1}
            defaultValue={codeformerWeight}
            step={0.01}
            label="b) CodeFormer Weight"
            onChange={(value) => setCodeformerWeight(value)}
            inputWidth="w-16"
            tooltipKey="codeformerWeight"
          />
        </div>
      )}

      {faceRestorationModel === "gfpgan" && (
        <div className="mt-4">
          <Slider
            min={0}
            max={1}
            defaultValue={gfpganWeight}
            step={0.01}
            label="b) GFPGAN Weight"
            onChange={(value) => setGfpganWeight(value)}
            inputWidth="w-16"
            tooltipKey="gfpganWeight"
          />
        </div>
      )}
      
      <div className="mt-2 flex items-center gap-2">
        <Checkbox id="save-face-model" />
        <label htmlFor="save-face-model" className="text-sm">
          Move face fixing model from VRAM into RAM after processing
        </label>
      </div>
    </div>
  );
};

export default FaceRestorationSettings;
