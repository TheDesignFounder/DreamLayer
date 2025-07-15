import React, { useState } from 'react';
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Card } from "@/components/ui/card";
import Slider from "./Slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface RenderStyleOption {
  id: string;
  label: string;
  description?: string;
  speed?: string;
  optimumStepsMin?: number;
  optimumStepsMax?: number;
  optimumCfgMin?: number;
  optimumCfgMax?: number;
}

interface RenderSettingsProps {
  showResizeMode?: boolean;
  sampler: string;
  scheduler: string;
  steps: number;
  cfg: number;
  onChange: (sampler: string, scheduler: string, steps: number, cfg: number) => void;
}

const renderStyles: RenderStyleOption[] = [
  {
    id: "dpm-sde-karras",
    label: "DPM++ SDE Karras",
    description: "Layers structured stochastic noise with Karras steps to create rich, poster-grade visuals. It's not made for quick iteration loops.",
    speed: "Slow",
    optimumStepsMin: 35,
    optimumStepsMax: 50,
    optimumCfgMin: 10,
    optimumCfgMax: 18,
  },
  { 
    id: "euler-a", 
    label: "Euler A",
    description: "Makes images super fast for quick drafts and abstract art, so you can explore ideas rapidly. It's not good for precise prompts or fine detail at high CFG.",
    speed: "Very Fast",
    optimumStepsMin: 20,
    optimumStepsMax: 30,
    optimumCfgMin: 6,
    optimumCfgMax: 9,
  },
  { 
    id: "euler", 
    label: "Euler",
    description: "Delivers fast, cleaner images with sharper edges, great for stylized portraits and rapid experiments. It's not ideal for extreme prompt accuracy at high CFG.",
    speed: "Fast",
    optimumStepsMin: 20,
    optimumStepsMax: 30,
    optimumCfgMin: 6,
    optimumCfgMax: 9,
  },
  { 
    id: "ddim", 
    label: "DDIM",
    description: "Generates consistent, soft-contrast images quickly, making batch outputs reliable. It struggles with detailed textures and sharp edges when you need crisp realism.",
    speed: "Fast",
    optimumStepsMin: 15,
    optimumStepsMax: 25,
    optimumCfgMin: 5,
    optimumCfgMax: 9,
  },
  { 
    id: "lms", 
    label: "LMS",
    description: "Offers balanced renders with moderate sharpness and stable textures, ideal for portraits and general scenes. It's not the best choice for ultra-sharp or very abstract art.",
    speed: "Moderate",
    optimumStepsMin: 20,
    optimumStepsMax: 30,
    optimumCfgMin: 8,
    optimumCfgMax: 13,
  },
  { 
    id: "heun", 
    label: "Heun",
    description: "Creates smooth gradients and accurate details, perfect for semi-realistic styles. It takes more time, so it's not suited to speed-critical applications.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 8,
    optimumCfgMax: 14,
  },
  { 
    id: "dpm2", 
    label: "DPM2",
    description: "Builds detailed, crisp images with natural lighting and depth, great for photorealism and structured scenes. It's weak on loose or abstract prompts.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 7,
    optimumCfgMax: 13,
  },
  { 
    id: "dpm2-a", 
    label: "DPM2 a",
    description: "Adds creative noise on top of DPM2's structure, so you get stylized, varied renders. It's less precise and can't match strict realism every time.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 7,
    optimumCfgMax: 12,
  },
  { 
    id: "dpm-2s-a", 
    label: "DPM++ 2S a",
    description: "Blends structure with noise for expressive, flexible images, ideal for imaginative art. It's not designed for photo-exact or strict realism.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 8,
    optimumCfgMax: 13,
  },
  { 
    id: "dpm-2m", 
    label: "DPM++ 2M",
    description: "Balances accuracy and texture for clean, high-fidelity portraits, characters, and general use. It's too slow for workflows that need quick iteration.",
    speed: "Medium",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 8,
    optimumCfgMax: 14,
  },
  { 
    id: "dpm-sde", 
    label: "DPM++ SDE",
    description: "Injects structured noise for vivid, deep details and strong prompt accuracy, perfect for final detailed renders. It's too slow for fast workflows or animations.",
    speed: "Slow",
    optimumStepsMin: 30,
    optimumStepsMax: 40,
    optimumCfgMin: 10,
    optimumCfgMax: 15,
  },
  { 
    id: "dpm-fast", 
    label: "DPM fast",
    description: "Prioritizes speed over precision, giving you rapid bulk generations and quick tests. It produces fuzzier, less refined results on complex prompts.",
    speed: "Very Fast",
    optimumStepsMin: 15,
    optimumStepsMax: 20,
    optimumCfgMin: 6,
    optimumCfgMax: 10,
  },
  { 
    id: "dpm-adaptive", 
    label: "DPM adaptive",
    description: "Smartly adjusts its steps based on scene complexity, giving efficient mixed-detail outputs. It's not ideal if you need full manual control or consistent style.",
    speed: "Fast",
    optimumStepsMin: 0, // Auto
    optimumStepsMax: 0, // Auto
    optimumCfgMin: 7,
    optimumCfgMax: 12,
  },
  { 
    id: "lms-karras", 
    label: "LMS Karras",
    description: "Uses Karras scheduling to smooth gradients and refine tones, great for portraits and subtle shading. It can't handle highly dynamic textures well.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 35,
    optimumCfgMin: 8,
    optimumCfgMax: 13,
  },
  { 
    id: "dpm2-karras", 
    label: "DPM2 Karras",
    description: "Enhance detail progression, perfect for realistic images with clean shading. It's not suited for tasks where speed is top priority.",
    speed: "Moderate",
    optimumStepsMin: 30,
    optimumStepsMax: 40,
    optimumCfgMin: 8,
    optimumCfgMax: 14,
  },
  { 
    id: "dpm2-a-karras", 
    label: "DPM2 a Karras",
    description: "Merges creative ancestral noise with Karras scheduling, delivering diverse stylized realism. It can't guarantee the same result every run.",
    speed: "Moderate",
    optimumStepsMin: 30,
    optimumStepsMax: 40,
    optimumCfgMin: 8,
    optimumCfgMax: 14,
  },
  { 
    id: "dpm-2s-a-karras", 
    label: "DPM++ 2S a Karras",
    description: "Combines expressive noise and Karras smoothing, making it ideal for creative illustrations. It lacks the consistency needed for extreme realism.",
    speed: "Moderate",
    optimumStepsMin: 30,
    optimumStepsMax: 40,
    optimumCfgMin: 8,
    optimumCfgMax: 14,
  },
  { 
    id: "dpm-2m-karras", 
    label: "DPM++ 2M Karras",
    description: "Fuses high-fidelity textures with Karras scheduling for sharp, photorealistic product and branding images. It's too slow for abstract or chaotic art.",
    speed: "Medium",
    optimumStepsMin: 30,
    optimumStepsMax: 40,
    optimumCfgMin: 9,
    optimumCfgMax: 15,
  },
  { 
    id: "plms", 
    label: "PLMS",
    description: "Uses a pseudo–linear multistep method to give coherent, general-purpose images at a steady pace. It can't match ultra-speed rough drafts or extreme detail.",
    speed: "Moderate",
    optimumStepsMin: 25,
    optimumStepsMax: 40,
    optimumCfgMin: 6,
    optimumCfgMax: 10,
  },
];

const RenderSettings: React.FC<RenderSettingsProps> = ({
  showResizeMode = true,
  sampler,
  scheduler,
  steps,
  cfg,
  onChange
}) => {
  const [selectedStyle, setSelectedStyle] = useState<RenderStyleOption>(
    renderStyles.find(style => style.id === sampler) || renderStyles[0]
  );
  const [resizeMode, setResizeMode] = useState("just-resize");

  const handleStyleChange = (value: string) => {
    const selected = renderStyles.find(style => style.id === value) || renderStyles[0];
    setSelectedStyle(selected);
    onChange(value, scheduler, steps, cfg);
  };

  const handleStepsChange = (value: number) => {
    onChange(sampler, scheduler, value, cfg);
  };

  const handleCfgChange = (value: number) => {
    onChange(sampler, scheduler, steps, value);
  };

  const getStepsLabel = () => {
    if (selectedStyle.id === "dpm-adaptive") {
      return "b) Sampling Steps | <span style='color: #64748B;'>Optimal Level: Auto</span>";
    }
    return `b) Sampling Steps | <span style='color: #64748B;'>Optimal Level: ${selectedStyle.optimumStepsMin}–${selectedStyle.optimumStepsMax}</span>`;
  };

  const getCfgLabel = () => {
    return `c) CFG Scale | <span style='color: #64748B;'>Optimal Level: ${selectedStyle.optimumCfgMin}–${selectedStyle.optimumCfgMax}</span>`;
  };

  return (
    <div className="space-y-4">
      {/* Sampling Settings Header */}
      <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">
        {showResizeMode ? "2. Sampling Settings" : "2. Sampling Settings"}
      </h4>

      {/* Sampling Method Section */}
      <div className="mb-4">
        <label htmlFor="renderStyle" className="mb-2 block text-sm font-medium">a) Sampling Method:</label>
        <Select value={sampler} onValueChange={handleStyleChange}>
          <SelectTrigger className="w-full" id="renderStyle">
            <SelectValue placeholder="Select a sampling method" />
          </SelectTrigger>
          <SelectContent>
            {renderStyles.map((style) => (
              <SelectItem key={style.id} value={style.id}>
                {style.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="mt-4 mb-4 text-sm text-muted-foreground mx-1">
          <span className="font-medium text-[#64748B]">About The Method:</span> {selectedStyle.description} Speed: {selectedStyle.speed}.
        </div>
      </div>
      
      <div className="mb-8">
        <Slider
          min={1}
          max={150}
          defaultValue={steps}
          label={getStepsLabel()}
          sublabel=""
          onChange={handleStepsChange}
        />
      </div>
      
      <div className="mb-4">
        <Slider
          min={1}
          max={30}
          defaultValue={cfg}
          label={getCfgLabel()}
          sublabel=""
          onChange={handleCfgChange}
        />
      </div>

      {/* Denoising Strength - only show in img2img tab */}
      {showResizeMode && (
        <div className="mb-4">
          <Slider
            min={0}
            max={1}
            step={0.01}
            defaultValue={0.55}
            label="d) Denoising Strength | <span style='color: #64748B;'>Optimal 0.4-0.7</span>"
            sublabel=""
          />
        </div>
      )}

      {/* Resize Mode Header and Section - moved to after sampling settings */}
      {showResizeMode && (
        <>
          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">3. Resize Mode</h4>

          {/* Resize Mode Section */}
          <div className="mb-4">
            <RadioGroup 
              value={resizeMode} 
              onValueChange={setResizeMode}
              className="grid grid-cols-4 gap-3"
            >
              <div className="relative">
                <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${resizeMode === "just-resize" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                  <RadioGroupItem id="just-resize" value="just-resize" className="h-4 w-4" />
                  <label htmlFor="just-resize" className="text-sm font-medium cursor-pointer w-full">Just Resize</label>
                </Card>
              </div>
              
              <div className="relative">
                <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${resizeMode === "crop-resize" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                  <RadioGroupItem id="crop-resize" value="crop-resize" className="h-4 w-4" />
                  <label htmlFor="crop-resize" className="text-sm font-medium cursor-pointer w-full">Crop & Resize</label>
                </Card>
              </div>
              
              <div className="relative">
                <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${resizeMode === "resize-fill" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                  <RadioGroupItem id="resize-fill" value="resize-fill" className="h-4 w-4" />
                  <label htmlFor="resize-fill" className="text-sm font-medium cursor-pointer w-full">Resize & Fill</label>
                </Card>
              </div>
              
              <div className="relative">
                <Card className={`flex items-center gap-3 p-3 cursor-pointer border ${resizeMode === "just-resize-latent" ? "border-blue-600 bg-blue-50/50" : "border-gray-200"}`}>
                  <RadioGroupItem id="just-resize-latent" value="just-resize-latent" className="h-4 w-4" />
                  <label htmlFor="just-resize-latent" className="text-sm font-medium cursor-pointer w-full">Just Resize (latent upscale)</label>
                </Card>
              </div>
            </RadioGroup>
          </div>
        </>
      )}
    </div>
  );
};

export default RenderSettings;

