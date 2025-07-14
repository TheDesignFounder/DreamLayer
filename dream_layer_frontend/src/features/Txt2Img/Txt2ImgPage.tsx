import React, { useState, useEffect } from 'react';
import Accordion from '@/components/Accordion';
import PromptInput from '@/components/PromptInput';
import RenderSettings from '@/components/RenderSettings';
import SizingSettings from '@/components/SizingSettings';
import OutputQuantity from '@/components/OutputQuantity';
import GenerationID from '@/components/GenerationID';
import AdvancedSettings from '@/components/AdvancedSettings';
import ExternalExtensions from '@/components/ExternalExtensions';
import ImagePreview from '@/components/tabs/txt2img/ImagePreview';
import CheckpointBrowser from '@/components/checkpoint/CheckpointBrowser';
import LoraBrowser from '@/components/lora/LoraBrowser';
import CustomWorkflowBrowser from '@/components/custom-workflow/CustomWorkflowBrowser';
import { useIsMobile } from '@/hooks/use-mobile';
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { Txt2ImgCoreSettings, defaultTxt2ImgSettings } from '@/types/generationSettings';
import useControlNetStore from '@/stores/useControlNetStore';
import { ControlNetRequest } from '@/types/controlnet';
import useLoraStore from '@/stores/useLoraStore';
import { LoraRequest } from '@/types/lora';

const API_URL = import.meta.env.VITE_API_URL;

interface Txt2ImgPageProps {
  selectedModel: string;
  onTabChange: (tabId: string) => void;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type CustomWorkflowType = any;

const Txt2ImgPage: React.FC<Txt2ImgPageProps> = ({ selectedModel, onTabChange }) => {
  const [activeSubTab, setActiveSubTab] = useState("generation");
  const [coreSettings, setCoreSettings] = useState<Txt2ImgCoreSettings>({
    ...defaultTxt2ImgSettings,
    model_name: selectedModel
  });
  const [customWorkflow, setCustomWorkflow] = useState<CustomWorkflowType | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const isMobile = useIsMobile();
  const addImages = useTxt2ImgGalleryStore(state => state.addImages);
  const setLoading = useTxt2ImgGalleryStore(state => state.setLoading);
  const controlNetConfig = useControlNetStore(state => state.controlNetConfig);
  const { setControlNetConfig } = useControlNetStore();
  const loraConfig = useLoraStore(state => state.loraConfig);

  useEffect(() => {
    updateCoreSettings({ model_name: selectedModel });
  }, [selectedModel]);

  const updateCoreSettings = (updates: Partial<Txt2ImgCoreSettings>) => {
    setCoreSettings(prev => ({ ...prev, ...updates }));
  };

  const handlePromptChange = (value: string, isNegative: boolean = false) => {
    updateCoreSettings(isNegative ? { negative_prompt: value } : { prompt: value });
  };

  const handleGenerateImage = async () => {
    if (isGenerating) {
      await fetch(`${API_URL}/api/txt2img/interrupt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      setIsGenerating(false);
      setLoading(false);
      return;
    }

    try {
      setIsGenerating(true);
      setLoading(true);

      const requestData = {
        ...coreSettings,
        custom_workflow: customWorkflow,
        ...(controlNetConfig && { controlnet: controlNetConfig }),
        ...(loraConfig?.enabled && { lora: loraConfig })
      };

      const response = await fetch(`${API_URL}/api/txt2img`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate image: ${errorText}`);
      }

      const data = await response.json();

      if (data.comfy_response?.generated_images) {
        const images = data.comfy_response.generated_images.map((img: { url: string }) => ({
          id: `${Date.now()}-${Math.random()}`,
          url: img.url,
          prompt: coreSettings.prompt,
          negativePrompt: coreSettings.negative_prompt,
          timestamp: Date.now(),
          settings: { ...coreSettings }
        }));

        addImages(images);
      } else {
        throw new Error('No images were generated');
      }
    } catch (error) {
      console.error('Error generating image:', error);
    } finally {
      setLoading(false);
      setIsGenerating(false);
    }
  };

  const getAccordionTitle = () => {
    switch (activeSubTab) {
      case "checkpoints":
        return "Custom Workflow Management";
      case "lora":
        return "LoRA Browser";
      default:
        return "Core Generation Settings";
    }
  };

  const ActionButtons = () => (
    <div className="flex space-x-2">
      <Button 
        className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        onClick={handleGenerateImage}
        disabled={false}
      >
        {isGenerating ? 'Generating...' : 'Generate Image'}
      </Button>
    </div>
  );

  const MobileImagePreview = () => (
    <div className="my-4 w-full">
      <ImagePreview onTabChange={onTabChange} />
    </div>
  );

  const SubTabNavigation = () => {
    const tabs = [
      { id: "generation", label: "Generation", active: activeSubTab === "generation" },
      { id: "checkpoints", label: "Custom Workflow", active: activeSubTab === "checkpoints" },
      { id: "lora", label: "Lora", active: activeSubTab === "lora" }
    ];

    return (
      <div className="flex flex-wrap gap-3">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              "px-6 py-2.5 rounded-full text-sm font-medium transition-all duration-200 border focus:outline-none focus:ring-2 focus:ring-offset-2",
              tab.active
                ? "bg-blue-600 text-white shadow-md hover:bg-blue-700 focus:ring-blue-500 border-blue-600"
                : "bg-transparent text-gray-600 hover:bg-gray-50 border-gray-200 hover:border-gray-300 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-800/50 dark:hover:border-gray-500"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
    );
  };

  const handleCopyPrompts = () => {
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your prompt here"]') as HTMLTextAreaElement;
    const negativePromptTextarea = document.querySelector('textarea[placeholder="Enter negative prompt here"]') as HTMLTextAreaElement;

    if (promptTextarea && negativePromptTextarea) {
      const combinedText = `Prompt: ${promptTextarea.value}\nNegative Prompt: ${negativePromptTextarea.value}`;
      navigator.clipboard.writeText(combinedText);
    }
  };

  const renderActiveSubTabContent = () => {
    switch (activeSubTab) {
      case "checkpoints":
        return (
          <CustomWorkflowBrowser
            onWorkflowChange={setCustomWorkflow}
            currentWorkflow={customWorkflow}
          />
        );
      case "lora":
        return <LoraBrowser />;
      default:
        return (
          <>
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
              maxLength={500}
              placeholder="Enter your prompt here"
              value={coreSettings.prompt}
              onChange={(value) => handlePromptChange(value)}
            />
            <PromptInput
              label="b) Negative Prompt"
              negative={true}
              maxLength={500}
              placeholder="Enter negative prompt here"
              value={coreSettings.negative_prompt}
              onChange={(value) => handlePromptChange(value, true)}
            />
            <RenderSettings
              showResizeMode={false}
              sampler={coreSettings.sampler_name}
              scheduler={coreSettings.scheduler}
              steps={coreSettings.steps}
              cfg={coreSettings.cfg_scale}
              onChange={(sampler, scheduler, steps, cfg) => {
                updateCoreSettings({
                  sampler_name: sampler,
                  scheduler,
                  steps,
                  cfg_scale: cfg
                });
              }}
            />
            <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">3. Sizing</h4>
            <SizingSettings
              width={coreSettings.width}
              height={coreSettings.height}
              onChange={(w, h) => updateCoreSettings({ width: w, height: h })}
            />
            <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">
              4. Output Quantity: {coreSettings.batch_count * coreSettings.batch_size}
            </h4>
            <OutputQuantity
              batchCount={coreSettings.batch_count}
              batchSize={coreSettings.batch_size}
              onChange={(count, size) => updateCoreSettings({ batch_count: count, batch_size: size })}
            />
            <div className="flex items-center justify-between mt-6 mb-2">
              <h4 className="text-sm font-bold text-[#2563EB]">5. Seed</h4>
              <div className="flex space-x-2">
                <button
                  className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground"
                  onClick={() => updateCoreSettings({ seed: -1, random_seed: true })}
                >
                  Randomize Seed
                </button>
                <button
                  className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground"
                  onClick={() => updateCoreSettings({ seed: coreSettings.seed, random_seed: false })}
                >
                  Reuse Past Seed
                </button>
              </div>
            </div>
            <GenerationID
              seed={coreSettings.seed}
              random={coreSettings.random_seed}
              onChange={(seed, random) => updateCoreSettings({ seed, random_seed: random })}
            />
          </>
        );
    }
  };

  return (
    <div className={`mb-4 ${isMobile ? 'grid grid-cols-1' : 'grid gap-6 md:grid-cols-[1.8fr_1fr]'}`}>
      <div className="space-y-4">
        <div className="flex flex-col">
          <div className="mb-[18px] flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <h3 className="text-base font-medium">Generation Settings</h3>
            <ActionButtons />
          </div>
          {isMobile && <MobileImagePreview />}
          <div className="mb-[18px]">
            <SubTabNavigation />
          </div>
          <Accordion title={getAccordionTitle()} number="1" defaultOpen={true}>
            {renderActiveSubTabContent()}
          </Accordion>
        </div>
      </div>
      {!isMobile && (
        <div>
          <ImagePreview onTabChange={onTabChange} />
        </div>
      )}
    </div>
  );
};

export default Txt2ImgPage;
