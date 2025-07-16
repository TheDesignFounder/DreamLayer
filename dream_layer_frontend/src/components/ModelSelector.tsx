import { CirclePlus, RefreshCw, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import ApiBasedModelForm from "@/components/AliasKeyInputs";
import { useEffect, useState } from "react";
import PopupBox from "@/components/ui/pop-up"
import { CheckpointModel, fetchAvailableModels } from "@/services/modelService";

interface ModelSelectorProps {
  onModelSelect: (modelName: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelSelect }) => {
  const [models, setModels] = useState<CheckpointModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false)

  const loadModels = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const availableModels = await fetchAvailableModels();
      setModels(availableModels);
      
      // If we have models and no selection, select the first one
      if (availableModels.length > 0 && !selectedModel) {
        setSelectedModel(availableModels[0].filename);
        onModelSelect(availableModels[0].filename);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load models');
      console.error('Error loading models:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const handleModelChange = (value: string) => {
    setSelectedModel(value);
    onModelSelect(value);
  };

  return (
    <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0">
      <div className="flex flex-col flex-1">
      <PopupBox isOpen={open} onClose={() => setOpen(false)} title="API-Based Model"> <ApiBasedModelForm></ApiBasedModelForm>
      </PopupBox>
        <label htmlFor="model" className="mb-1 text-sm font-medium">
          Select Stable Diffusion Checkpoint:
        </label>
        <Select value={selectedModel} onValueChange={handleModelChange}>
          <SelectTrigger 
            id="model" 
            className="w-full bg-white dark:bg-[#0F172A] text-foreground dark:text-white border-input dark:border-slate-700"
          >
            <SelectValue placeholder="Select a model" />
          </SelectTrigger>
          <SelectContent className="bg-white dark:bg-[#0F172A] border-input dark:border-slate-700">
            {models.map((model) => (
              <SelectItem key={model.id} value={model.filename}>
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
      </div>
      <div className="flex flex-1 space-x-2 sm:justify-end">
        <Button 
          variant="outline" 
          className="flex items-center space-x-2 mr-5 dark:bg-[#0F172A] dark:border-slate-700 dark:text-white dark:hover:bg-slate-800"
          onClick={()=>setOpen(true)}
          disabled={isLoading}
        >
          <CirclePlus className={`h-5 w-5`} />
          <span>Add API KEY</span>
        </Button>
        <Button 
          variant="outline" 
          className="flex items-center space-x-2 dark:bg-[#0F172A] dark:border-slate-700 dark:text-white dark:hover:bg-slate-800"
          onClick={loadModels}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'Loading...' : 'Refresh Models'}</span>
        </Button>
        {false && <Button variant="outline" className="dark:bg-[#0F172A] dark:border-slate-700 dark:text-white dark:hover:bg-slate-800">
          <Save className="h-4 w-4 mr-2" />
          Saved Settings
        </Button>}
      </div>
    </div>
  );
};

export default ModelSelector;
