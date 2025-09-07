import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { fetchRandomPrompt } from "@/services/modelService";
import { useToast } from "@/hooks/use-toast";
import { useRef, useState } from "react";

interface PromptInputProps {
  label: string;
  maxLength?: number;
  placeholder?: string;
  negative?: boolean;
  showAddRandom?: boolean;
  showBatchPrompts?: boolean;
  value: string;
  onChange: (value: string) => void;
  onBatchPromptsLoaded?: (prompts: string[]) => void;
}

const PromptInput: React.FC<PromptInputProps> = ({
  label,
  maxLength = 500,
  placeholder = "",
  negative = false,
  showAddRandom = true,
  showBatchPrompts = false,
  value,
  onChange,
  onBatchPromptsLoaded
}) => {
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAddRandom = async () => {
    try {
      const promptType = negative ? 'negative' : 'positive';
      console.log(`🎲 Frontend: Add Random clicked for ${promptType} prompt`);
      
      const randomPrompt = await fetchRandomPrompt(promptType);
      console.log(`📝 Frontend: Got prompt: ${randomPrompt}`);
      
      // Replace existing value with random prompt
      onChange(randomPrompt);
    } catch (error) {
      console.error('❌ Frontend: Failed to fetch random prompt:', error);
    }
  };

  const handleBatchPrompts = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.txt')) {
      toast({
        title: "Invalid file type",
        description: "Please select a .txt file",
        variant: "destructive"
      });
      return;
    }

    try {
      setIsProcessing(true);
      const fileContent = await file.text();
      const prompts = fileContent.split('\n')
        .map(line => line.trim())
        .filter(line => line && !line.startsWith('#'));

      if (prompts.length === 0) {
        toast({
          title: "No prompts found",
          description: "The file contains no valid prompts",
          variant: "destructive"
        });
        return;
      }

      if (onBatchPromptsLoaded) {
        onBatchPromptsLoaded(prompts);
      }

      toast({
        title: "Prompts loaded",
        description: `Loaded ${prompts.length} prompts. Click Generate to start batch processing.`
      });
    } catch (error) {
      toast({
        title: "Error reading file",
        description: "Failed to read the selected file",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <div className="flex gap-2">
          {showAddRandom && (
            <button 
              onClick={handleAddRandom}
              className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground"
            >
              Add Random
            </button>
          )}
          {showBatchPrompts && (
            <>
              <button 
                onClick={handleBatchPrompts}
                disabled={isProcessing}
                className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
              >
                {isProcessing ? "Loading..." : "Load Batch"}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt"
                onChange={handleFileSelect}
                className="hidden"
              />
            </>
          )}
        </div>
      </div>
      <textarea
        className={`w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
          negative ? 'text-red-500' : ''
        }`}
        rows={3}
        maxLength={maxLength}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
};

export default PromptInput;
