import React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { fetchRandomPrompt } from "@/services/modelService";

interface PromptInputProps {
  label: string;
  maxLength?: number;
  placeholder?: string;
  negative?: boolean;
  showAddRandom?: boolean;
  value: string;
  onChange: (value: string) => void;
}

const PromptInput: React.FC<PromptInputProps> = ({
  label,
  maxLength = 500,
  placeholder = "",
  negative = false,
  showAddRandom = true,
  value,
  onChange
}) => {
  const handleAddRandom = async () => {
    try {
      const promptType = negative ? "negative" : "positive";
      console.log(`🎲 Add Random clicked for ${promptType} prompt`);

      const randomPrompt = await fetchRandomPrompt(promptType);
      console.log(`📝 Got random prompt: ${randomPrompt}`);

      onChange(randomPrompt);
    } catch (error) {
      console.error("❌ Failed to fetch random prompt:", error);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        {showAddRandom && (
          <Button
            onClick={handleAddRandom}
            variant="outline"
            size="sm"
            className="text-xs px-2 py-1 h-auto"
          >
            Add Random
          </Button>
        )}
      </div>
      <textarea
        className={cn(
          "w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          negative && "text-red-500"
        )}
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
