import React, { useState, useRef } from 'react';
import NavBar from '@/components/NavBar';
import ModelSelector from '@/components/ModelSelector';
import TabsNav from '@/components/Navigation/TabsNav';
import { Txt2ImgPage } from '@/features/Txt2Img';
import { Img2ImgPage } from '@/features/Img2Img';
import ExtrasPage from '@/features/Extras';
import { PNGInfoPage } from '@/features/PNGInfo';
import { ConfigurationsPage } from '@/features/Configurations';
import { useTxt2ImgGalleryStore } from '@/stores/useTxt2ImgGalleryStore';
import { useImg2ImgGalleryStore } from '@/stores/useImg2ImgGalleryStore';
import { useGlobalKeyboardShortcuts } from '@/hooks/useGlobalKeyboardShortcuts';

const Index = () => {
  const [activeTab, setActiveTab] = useState("txt2img");
  const [selectedModel, setSelectedModel] = useState<string>("v1-5-pruned-emaonly-fp16.safetensors");
  const clearTxt2ImgImages = useTxt2ImgGalleryStore(state => state.clearImages);
  const clearImg2ImgImages = useImg2ImgGalleryStore(state => state.clearImages);
  
  // Refs to access child component methods
  const txt2imgRef = useRef<{ handleGenerate: () => void; handleCancel: () => void; isGenerating: boolean }>(null);
  const img2imgRef = useRef<{ handleGenerate: () => void; handleCancel: () => void; isGenerating: boolean }>(null);

  const handleTabChange = (tabId: string) => {
    // Clear both stores when switching tabs
    clearTxt2ImgImages();
    clearImg2ImgImages();
    setActiveTab(tabId);
  };

  const handleModelSelect = (modelName: string) => {
    setSelectedModel(modelName);
  };

  // Keyboard shortcut handlers
  const handleGenerate = () => {
    if (activeTab === "txt2img" && txt2imgRef.current) {
      txt2imgRef.current.handleGenerate();
    } else if (activeTab === "img2img" && img2imgRef.current) {
      img2imgRef.current.handleGenerate();
    }
  };

  const handleOpenSettings = () => {
    handleTabChange("configurations");
  };

  const handleCancel = () => {
    if (activeTab === "txt2img" && txt2imgRef.current) {
      txt2imgRef.current.handleCancel();
    } else if (activeTab === "img2img" && img2imgRef.current) {
      img2imgRef.current.handleCancel();
    }
  };

  // Get current generation state
  const isGenerating = 
    (activeTab === "txt2img" && txt2imgRef.current?.isGenerating) ||
    (activeTab === "img2img" && img2imgRef.current?.isGenerating) ||
    false;

  // Register global keyboard shortcuts
  useGlobalKeyboardShortcuts({
    onGenerate: handleGenerate,
    onOpenSettings: handleOpenSettings,
    onCancel: handleCancel,
    isGenerating
  });

  const renderTabContent = () => {
    switch (activeTab) {
      case "txt2img":
        return <Txt2ImgPage ref={txt2imgRef} selectedModel={selectedModel} onTabChange={handleTabChange} />;
      case "img2img":
        return <Img2ImgPage ref={img2imgRef} selectedModel={selectedModel} onTabChange={handleTabChange} />;
      case "extras":
        return <ExtrasPage />;
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
