import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, Upload, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useSettingsStore } from "@/features/Configurations/useSettingsStore";
import { toast } from "sonner";

interface SettingsData {
  modelPath: string;
  enableLowVRAM: boolean;
  uiTheme: string;
  language: string;
  showQuickSettings: boolean;
  showProgressInTitle: boolean;
  computeDevice: string;
  vramUsageTarget: number;
  parallelProcessing: number;
  useXformers: boolean;
  optimizeMedVram: boolean;
  outputDirectory: string;
  modelsDirectory: string;
  controlNetModelsPath: string;
  upscalerModelsPath: string;
  vaeModelsPath: string;
  loraEmbeddingsPath: string;
  filenameFormat: string;
  saveMetadata: boolean;
  updateChannel: string;
  autoUpdate: boolean;
}

const SettingsManager: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const settingsStore = useSettingsStore();

  const exportSettings = () => {
    try {
      const settings: SettingsData = {
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

      const dataStr = JSON.stringify(settings, null, 2);
      const dataBlob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(dataBlob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `dreamlayer-settings-${
        new Date().toISOString().split("T")[0]
      }.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success("Settings exported successfully!");
    } catch (error) {
      console.error("Failed to export settings:", error);
      toast.error("Failed to export settings");
    }
  };

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".json")) {
      toast.error("Please select a JSON file");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const settings: SettingsData = JSON.parse(content);

        // Validate that the imported data has the expected structure
        const requiredFields = [
          "modelPath",
          "enableLowVRAM",
          "uiTheme",
          "language",
          "computeDevice",
        ];

        const missingFields = requiredFields.filter(
          (field) => !(field in settings)
        );

        if (missingFields.length > 0) {
          toast.error(
            `Invalid settings file. Missing fields: ${missingFields.join(", ")}`
          );
          return;
        }

        // Apply settings to store
        settingsStore.setModelPath(settings.modelPath);
        settingsStore.setEnableLowVRAM(settings.enableLowVRAM);
        settingsStore.setUiTheme(settings.uiTheme);
        settingsStore.setLanguage(settings.language);
        settingsStore.setShowQuickSettings(settings.showQuickSettings);
        settingsStore.setShowProgressInTitle(settings.showProgressInTitle);
        settingsStore.setComputeDevice(settings.computeDevice);
        settingsStore.setVramUsageTarget(settings.vramUsageTarget);
        settingsStore.setParallelProcessing(settings.parallelProcessing);
        settingsStore.setUseXformers(settings.useXformers);
        settingsStore.setOptimizeMedVram(settings.optimizeMedVram);
        settingsStore.setOutputDirectory(settings.outputDirectory);
        settingsStore.setModelsDirectory(settings.modelsDirectory);
        settingsStore.setControlNetModelsPath(settings.controlNetModelsPath);
        settingsStore.setUpscalerModelsPath(settings.upscalerModelsPath);
        settingsStore.setVaeModelsPath(settings.vaeModelsPath);
        settingsStore.setLoraEmbeddingsPath(settings.loraEmbeddingsPath);
        settingsStore.setFilenameFormat(settings.filenameFormat);
        settingsStore.setSaveMetadata(settings.saveMetadata);
        settingsStore.setUpdateChannel(settings.updateChannel);
        settingsStore.setAutoUpdate(settings.autoUpdate);

        toast.success("Settings imported successfully!");
      } catch (error) {
        console.error("Failed to import settings:", error);
        toast.error("Failed to parse settings file. Please check the format.");
      }
    };

    reader.readAsText(file);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <Button onClick={exportSettings} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export Settings
        </Button>

        <div className="relative">
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            Import Settings
          </Button>
          <Input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={importSettings}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </div>
      </div>

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Export your current settings as a JSON file or import previously saved
          settings. This includes all configuration options like model paths,
          performance settings, and UI preferences.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SettingsManager;
