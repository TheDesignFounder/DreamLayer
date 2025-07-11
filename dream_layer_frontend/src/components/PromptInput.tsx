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
  required?: boolean; // New required prop
}

const PromptInput: React.FC<PromptInputProps> = ({
  label,
  maxLength = 500,
  placeholder = "",
  negative = false,
  showAddRandom = true,
  value,
  onChange,
  required = false
}) => {
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

  // Check if field is required and empty
  const isRequiredAndEmpty = required && (!value || value.trim() === '');

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </label>
        {showAddRandom && (
          <button 
            onClick={handleAddRandom}
            className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground"
          >
            Add Random
          </button>
        )}
      </div>
      <textarea
        className={cn(
          "w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          negative ? 'text-red-500' : '',
          isRequiredAndEmpty ? 'ring-2 ring-red-500' : ''
        )}
        rows={3}
        maxLength={maxLength}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
      />
    </div>
  );
};

export default PromptInput;
