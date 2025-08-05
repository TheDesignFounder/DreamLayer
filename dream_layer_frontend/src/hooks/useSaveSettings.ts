import { useSettingsStore } from '@/features/Configurations/useSettingsStore';
import { toast } from '@/hooks/use-toast';

export const useSaveSettings = () => {
  const settingsStore = useSettingsStore();

  const saveSettings = async () => {
    try {
      const pathSettings = {
        outputDirectory: settingsStore.outputDirectory,
        modelsDirectory: settingsStore.modelsDirectory,
        controlNetModelsPath: settingsStore.controlNetModelsPath,
        upscalerModelsPath: settingsStore.upscalerModelsPath,
        vaeModelsPath: settingsStore.vaeModelsPath,
        loraEmbeddingsPath: settingsStore.loraEmbeddingsPath,
        filenameFormat: settingsStore.filenameFormat,
        saveMetadata: settingsStore.saveMetadata
      };

      const response = await fetch('http://localhost:5002/api/settings/paths', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pathSettings),
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        // Add toast notification for success
        toast({
          title: "Settings Saved",
          description: "Your settings have been saved successfully.",
        });
        console.log('Settings saved successfully');
        return true;
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      // Add toast notification for error
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
