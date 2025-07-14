// No changes to imports
import React, { useState, useEffect } from 'react';
import ImageUploader from '@/components/ImageUploader';
import AdvancedSettings from '@/components/AdvancedSettings';
import ExternalExtensions from '@/components/ExternalExtensions';
import CheckpointBrowser from '@/components/checkpoint/CheckpointBrowser';
import LoraBrowser from '@/components/lora/LoraBrowser';
import CustomWorkflowBrowser from '@/components/custom-workflow/CustomWorkflowBrowser';
import PromptInput from '@/components/PromptInput';
import RenderSettings from '@/components/RenderSettings';
import SizingSettings from '@/components/SizingSettings';
import OutputQuantity from '@/components/OutputQuantity';
import GenerationID from '@/components/GenerationID';
import ImagePreview from '@/components/tabs/img2img/ImagePreview';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import useLoraStore from '@/stores/useLoraStore';
import useControlNetStore from '@/stores/useControlNetStore';
import { ControlNetRequest } from '@/types/controlnet';
import { prepareControlNetForAPI, validateControlNetConfig } from '@/utils/controlnetUtils';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useHotkeys } from "@/hooks/useHotkeys";

const API_URL = import.meta.env.VITE_API_URL;

interface Img2ImgPageProps {
  selectedModel: string;
  onTabChange: (tabId: string) => void;
}

type GeneratedImage = {
  url: string;
};

const Img2ImgPage: React.FC<Img2ImgPageProps> = ({ selectedModel, onTabChange }) => {
  const [activeSubTab, setActiveSubTab] = useState("generation");
  const [activeImg2ImgTool, setActiveImg2ImgTool] = useState("img2img");
  const [batchCount, setBatchCount] = useState(1);
  const [batchSize, setBatchSize] = useState(1);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const {
    inputImage,
    setLoading,
    addImages,
    clearImages,
    coreSettings,
    customWorkflow,
    setCustomWorkflow,
    handlePromptChange,
    handleSamplingSettingsChange,
    handleSizeSettingsChange,
    handleBatchSettingsChange,
    handleSeedChange,
    updateCoreSettings
  } = useImg2ImgGalleryStore();

  const selectedLora = useLoraStore(state => state.loraConfig);
  const { controlNetConfig, setControlNetConfig } = useControlNetStore();

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  const handleGenerateImage = async () => {
    if (isGenerating) {
      await fetch(`${API_URL}/api/img2img/interrupt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      setIsGenerating(false);
      setLoading(false);
      return;
    }

    if (!inputImage) {
      console.error('No input image selected');
      return;
    }

    setIsGenerating(true);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('image', inputImage.file);

      let preparedControlNet = null;
      if (controlNetConfig && validateControlNetConfig(controlNetConfig)) {
        try {
          preparedControlNet = await prepareControlNetForAPI(controlNetConfig);
        } catch (error) {
          console.error('Error preparing ControlNet for API:', error);
        }
      }

      const requestData = {
        ...coreSettings,
        model_name: selectedModel,
        custom_workflow: customWorkflow,
        lora: selectedLora,
        ...(preparedControlNet && { controlnet: preparedControlNet })
      };

      const response = await fetch(`${API_URL}/api/img2img`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();

      if (data.comfy_response?.generated_images) {
        const firstImageUrl = data.comfy_response.generated_images[0].url;
        const testImage = new Image();

        testImage.onload = () => {
          const images = data.comfy_response.generated_images.map((img: GeneratedImage) => ({
            id: `${Date.now()}-${Math.random()}`,
            url: img.url,
            prompt: requestData.prompt,
            negativePrompt: requestData.negative_prompt,
            timestamp: Date.now(),
            settings: requestData
          }));
          addImages(images);
          setLoading(false);
          setIsGenerating(false);
        };

        testImage.onerror = () => {
          setLoading(false);
          setIsGenerating(false);
          throw new Error('Failed to load generated image');
        };

        testImage.src = firstImageUrl;
      } else {
        setLoading(false);
        setIsGenerating(false);
        throw new Error('No images were generated');
      }
    } catch (error) {
      console.error('Error in handleGenerateImage:', error);
      setLoading(false);
      setIsGenerating(false);
    }
  };

  useHotkeys({ onGenerate: handleGenerateImage });

  const handleSubTabChange = (tabId: string) => {
    setActiveSubTab(tabId);
  };

  const handleImg2ImgToolChange = (toolId: string) => {
    setActiveImg2ImgTool(toolId);
  };

  const handleLocalBatchSettingsChange = (newBatchSize: number, newBatchCount: number) => {
    setBatchSize(newBatchSize);
    setBatchCount(newBatchCount);
    handleBatchSettingsChange(newBatchCount, newBatchSize);
  };

  const handleCopyPrompts = () => {
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your prompt here"]') as HTMLTextAreaElement;
    const negativePromptTextarea = document.querySelector('textarea[placeholder="Enter negative prompt here"]') as HTMLTextAreaElement;

    if (promptTextarea && negativePromptTextarea) {
      const combinedText = `Prompt: ${promptTextarea.value}\nNegative Prompt: ${negativePromptTextarea.value}`;
      navigator.clipboard.writeText(combinedText);
    }
  };

  const handleControlNetChange = (config: ControlNetRequest | null) => {
    setControlNetConfig(config?.enabled ? config : null);
  };

  const renderSection = () => {
    if (activeSubTab === "checkpoints") {
      return <CustomWorkflowBrowser onWorkflowChange={setCustomWorkflow} currentWorkflow={customWorkflow} />;
    } else if (activeSubTab === "lora") {
      return <LoraBrowser />;
    } else {
      return (
        <>
          <ImageUploader activeImg2ImgTool={activeImg2ImgTool} />

          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-bold text-primary">1. Prompt Input</h4>
            <Button onClick={handleCopyPrompts} variant="outline" size="sm" className="text-xs px-2 py-1 h-auto flex items-center gap-1">
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
            sampler={coreSettings.sampler_name}
            scheduler={coreSettings.scheduler}
            steps={coreSettings.steps}
            cfg={coreSettings.cfg_scale}
            onChange={handleSamplingSettingsChange}
          />

          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">3. Sizing</h4>
          <SizingSettings
            width={coreSettings.width}
            height={coreSettings.height}
            onChange={handleSizeSettingsChange}
          />

          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">
            4. Output Quantity: {batchCount * batchSize}
          </h4>
          <OutputQuantity
            batchCount={batchCount}
            batchSize={batchSize}
            onChange={handleLocalBatchSettingsChange}
          />

          <h4 className="mb-2 mt-6 text-sm font-bold text-[#2563EB]">5. Seed Settings</h4>
          <GenerationID
            seed={coreSettings.seed}
            random={coreSettings.random_seed}
            onChange={handleSeedChange}
          />
        </>
      );
    }
  };

  const Img2ImgToolsNavigation = () => {
    const tools = [
      { id: "img2img", label: "Img2Img", active: activeImg2ImgTool === "img2img" }
    ];

    return (
      <div className="mb-4">
        <div className="shrink-0 bg-border h-[1px] w-full mt-2 mb-4" />
        <div className="flex items-center gap-4 mb-4">
          <span className="text-sm font-medium text-foreground">Img2Img Tools:</span>
          <div className="flex flex-wrap gap-2">
            {tools.map(tool => (
              <div
                key={tool.id}
                onClick={() => handleImg2ImgToolChange(tool.id)}
                className={cn(
                  "flex items-center gap-2 p-2 rounded-full border transition-colors cursor-pointer",
                  tool.active
                    ? "border-primary bg-primary/10"
                    : "border-border hover:border-primary/50"
                )}
              >
                <span className="text-xs cursor-pointer truncate font-medium">{tool.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="shrink-0 bg-border h-[1px] w-full mb-2" />
      </div>
    );
  };

  const SubTabNavigation = ({ tabs, onTabChange }) => (
    <div className="flex flex-wrap gap-3">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
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

  if (!isLoaded) {
    return (
      <div className="p-8 bg-background text-foreground border border-border rounded-md">
        <p>Loading Img2Img interface...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-4">
      <div className="flex-1 space-y-4">
        <div className="flex flex-col">
          <div className="mb-[18px] flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <h3 className="text-base font-medium text-foreground">Image to Image Generation</h3>
            <div className="flex space-x-2">
              <Button
                title="Ctrl + Enter → Generate Image"
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                onClick={handleGenerateImage}
                disabled={!inputImage}
              >
                {isGenerating ? 'Interrupt' : 'Generate Image'}
              </Button>
            </div>
          </div>

          <div className="mb-[18px]">
            <SubTabNavigation
              tabs={[
                { id: "generation", label: "Generation", active: activeSubTab === "generation" },
                { id: "checkpoints", label: "Custom Workflow", active: activeSubTab === "checkpoints" },
                { id: "lora", label: "LoRA", active: activeSubTab === "lora" }
              ]}
              onTabChange={handleSubTabChange}
            />
          </div>

          {activeSubTab === "generation" && <Img2ImgToolsNavigation />}
          {renderSection()}
        </div>
      </div>
      <div className="w-full lg:w-[512px] space-y-4">
        <ImagePreview onTabChange={onTabChange} />
      </div>
    </div>
  );
};

export default Img2ImgPage;
