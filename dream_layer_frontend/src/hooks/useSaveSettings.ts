import { useSettingsStore } from '@/features/Configurations/useSettingsStore';
import { toast } from '@/hooks/use-toast';

export const useSaveSettings = () => {
  const settingsStore = useSettingsStore();

  const saveSettings = async () => {
    try {
      // Convert settings to JSON
      const settingsData = {
        modelPath: settingsStore.modelPath,
        enableLowVRAM: settingsStore.enableLowVRAM,
        uiTheme: settingsStore.uiTheme,
        language: settingsStore.language,
        showQuickSettings: settingsStore.showQuickSettings,
        showProgressInTitle: settingsStore.showProgressInTitle,
        computeDevice: settingsStore.computeDevice,
        vramUsageTarget: settingsStore.vramUsageTarget,
        parallelProcessing: settingsStore.parallelProcessing,
        useXformers: settingsStore.useXformers,
        optimizeMedVram: settingsStore.optimizeMedVram,
        outputDirectory: settingsStore.outputDirectory,
        modelsDirectory: settingsStore.modelsDirectory,
        controlNetModelsPath: settingsStore.controlNetModelsPath,
        upscalerModelsPath: settingsStore.upscalerModelsPath,
        vaeModelsPath: settingsStore.vaeModelsPath,
        loraEmbeddingsPath: settingsStore.loraEmbeddingsPath,
        filenameFormat: settingsStore.filenameFormat,
        saveMetadata: settingsStore.saveMetadata,
        updateChannel: settingsStore.updateChannel,
        autoUpdate: settingsStore.autoUpdate,
      };

      // Save settings to localStorage for now
      // In a real app, you'd want to send this to a backend API
      localStorage.setItem('dreamLayerSettings', JSON.stringify(settingsData));
      
      // Show success toast
      toast({
        title: "Settings Saved",
        description: "Your settings have been saved successfully.",
      });
      
      return true;
    } catch (error) {
      console.error('Error saving settings:', error);
      toast({
        title: "Error",
        description: "Failed to save settings. Please try again.",
        variant: "destructive",
      });
      return false;
    }
  };

  return { saveSettings };
};
