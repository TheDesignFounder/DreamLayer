
import React from 'react';
import PromptInput from '@/components/PromptInput';
import RenderSettings from '@/components/RenderSettings';
import SizingSettings from '@/components/SizingSettings';
import OutputQuantity from '@/components/OutputQuantity';
import GenerationID from '@/components/GenerationID';
import CheckpointBrowser from '@/components/checkpoint/CheckpointBrowser';
import LoraBrowser from '@/components/lora/LoraBrowser';
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";

interface SubTabContentProps {
  activeSubTab: string;
  batchCount: number;
  setBatchCount: (count: number) => void;
  batchSize: number;
  setBatchSize: (size: number) => void;
  promptValue?: string;
  negativePromptValue?: string;
  onPromptChange?: (value: string) => void;
  onNegativePromptChange?: (value: string) => void;
  width?: number;
  height?: number;
  onSizeChange?: (width: number, height: number) => void;
  seed?: number;
  random?: boolean;
  onSeedChange?: (seed: number, random?: boolean) => void;
}

const SubTabContent: React.FC<SubTabContentProps> = ({ 
  activeSubTab, 
  batchCount, 
  setBatchCount, 
  batchSize, 
  setBatchSize,
  promptValue = "",
  negativePromptValue = "",
  onPromptChange = () => {},
  onNegativePromptChange = () => {},
  width = 512,
  height = 512,
  onSizeChange = () => {},
  seed = 123456789,
  random = false,
  onSeedChange = () => {}
}) => {
  const handleCopyPrompts = () => {
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your prompt here"]') as HTMLTextAreaElement;
    const negativePromptTextarea = document.querySelector('textarea[placeholder="Enter negative prompt here"]') as HTMLTextAreaElement;
    
    if (promptTextarea && negativePromptTextarea) {
      const combinedText = `Prompt: ${promptTextarea.value}\nNegative Prompt: ${negativePromptTextarea.value}`;
      navigator.clipboard.writeText(combinedText);
    }
  };
  
  switch (activeSubTab) {
    case "checkpoints":
      return <CheckpointBrowser />;
    case "lora":
      return <LoraBrowser />;
    default:
      // Default "generation" tab
      return (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-[#2563EB]">1. Prompt Input</h4>
            <Button 
              onClick={handleCopyPrompts}
              variant="outline"
              size="sm"
              className="text-xs px-2 py-1 h-auto flex items-center gap-1"
            >
              <Copy className="h-3.5 w-3.5" />
              Copy Prompts
            </Button>
          </div>
          <PromptInput 
            label="a) Prompt"
            maxLength={75}
            placeholder="Enter your prompt here"
            value={promptValue}
            onChange={onPromptChange}
          />
          <PromptInput 
            label="b) Negative Prompt"
            negative={true}
            placeholder="Enter negative prompt here"
            value={negativePromptValue}
            onChange={onNegativePromptChange}
          />
          
          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">3. Sizing</h4>
          <SizingSettings 
            width={width}
            height={height}
            onChange={onSizeChange}
          />
          
          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">
            4. Output Quantity: {batchCount * batchSize}
          </h4>
          <OutputQuantity 
            batchSize={batchSize}
            batchCount={batchCount}
            onChange={(newBatchSize, newBatchCount) => {
              setBatchSize(newBatchSize);
              setBatchCount(newBatchCount);
            }}
          />
          
          <div className="flex items-center justify-between mt-6 mb-2">
            <h4 className="text-sm font-bold text-[#2563EB]">5. Seed</h4>
            <div className="flex space-x-2">
              <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground">
                Randomize Seed
              </button>
              <button className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground">
                Reuse Past Seed
              </button>
            </div>
          </div>
          <GenerationID 
            seed={seed}
            random={random}
            onChange={onSeedChange}
          />
        </div>
      );
  }
};

export default SubTabContent;
