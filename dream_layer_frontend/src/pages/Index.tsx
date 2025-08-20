import React, { useState } from 'react';
import NavBar from '@/components/NavBar';
import ModelSelector from '@/components/ModelSelector';
import TabsNav from '@/components/Navigation/TabsNav';
import { Txt2ImgPage } from '@/features/Txt2Img';
import { Img2ImgPage } from '@/features/Img2Img';
import ExtrasPage from '@/features/Extras';
import { ModelManagerPage } from '@/features/ModelManager';
import { PNGInfoPage } from '@/features/PNGInfo';
import { ConfigurationsPage } from '@/features/Configurations';
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';

const Index = () => {
  const [activeTab, setActiveTab] = useState("txt2img");
  const [selectedModel, setSelectedModel] = useState<string>("v1-5-pruned-emaonly-fp16.safetensors");
  const clearTxt2ImgImages = useTxt2ImgGalleryStore(state => state.clearImages);
  const clearImg2ImgImages = useImg2ImgGalleryStore(state => state.clearImages);

  const handleTabChange = (tabId: string) => {
    // Clear both stores when switching tabs
    clearTxt2ImgImages();
    clearImg2ImgImages();
    setActiveTab(tabId);
  };

  const handleModelSelect = (modelName: string) => {
    setSelectedModel(modelName);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "txt2img":
        return <Txt2ImgPage selectedModel={selectedModel} onTabChange={handleTabChange} />;
      case "img2img":
        return <Img2ImgPage selectedModel={selectedModel} onTabChange={handleTabChange} />;
      case "extras":
        return <ExtrasPage />;
      case "models":
        return <ModelManagerPage />;
      case "pnginfo":
        return <PNGInfoPage />;
      case "configurations":
        return <ConfigurationsPage />;
      default:
        return <Txt2ImgPage selectedModel={selectedModel} onTabChange={handleTabChange} />;
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <NavBar />
      <div className="container mx-auto max-w-7xl px-4 py-6">
        <ModelSelector onModelSelect={handleModelSelect} />
        <h2 className="mb-2 mt-6 text-lg font-medium text-foreground">Generation Modules</h2>
        <div className="bg-card rounded-lg shadow-[0px_4px_24px_rgba(51,51,51,0.15)] p-6 border border-border">
          <TabsNav activeTab={activeTab} onTabChange={handleTabChange} />
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default Index;
