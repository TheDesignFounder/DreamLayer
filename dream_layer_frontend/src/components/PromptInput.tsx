import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { fetchRandomPrompt } from "@/services/modelService";
import { ChevronDown, Clock, X } from 'lucide-react';

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
  const [promptHistory, setPromptHistory] = useState<string[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoadingRandom, setIsLoadingRandom] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const lastSavedValue = useRef<string>('');

  // Create storage key based on prompt type (positive/negative)
  const storageKey = `promptHistory_${negative ? 'negative' : 'positive'}`;

  // Load prompt history from localStorage on component mount
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem(storageKey);
      if (savedHistory) {
        const parsed = JSON.parse(savedHistory);
        if (Array.isArray(parsed)) {
          setPromptHistory(parsed);
        }
      }
    } catch (error) {
      console.error('Error parsing prompt history from localStorage:', error);
    }
  }, [storageKey]);

  // Save prompt history to localStorage whenever it changes
  useEffect(() => {
    if (promptHistory.length > 0) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(promptHistory));
      } catch (error) {
        console.error('Error saving prompt history to localStorage:', error);
      }
    }
  }, [promptHistory, storageKey]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Add prompt to history (with deduplication)
  const addPromptToHistory = (prompt: string) => {
    if (!prompt.trim() || prompt.length < 3) return; // Don't save very short prompts

    const trimmedPrompt = prompt.trim();
    
    // Don't add if it's the same as the last saved value
    if (trimmedPrompt === lastSavedValue.current) return;
    
    setPromptHistory(prev => {
      // Remove the prompt if it already exists (deduplication)
      const filtered = prev.filter(p => p !== trimmedPrompt);
      
      // Add the new prompt to the beginning and keep only the last 10
      const newHistory = [trimmedPrompt, ...filtered].slice(0, 10);
      
      return newHistory;
    });
    
    lastSavedValue.current = trimmedPrompt;
  };

  const handleAddRandom = async () => {
    try {
      setIsLoadingRandom(true);
      const promptType = negative ? 'negative' : 'positive';
      console.log(`🎲 Frontend: Add Random clicked for ${promptType} prompt`);
      
      const randomPrompt = await fetchRandomPrompt(promptType);
      console.log(`📝 Frontend: Got prompt: ${randomPrompt}`);
      
      // Replace existing value with random prompt
      onChange(randomPrompt);
      
      // Add the random prompt to history
      addPromptToHistory(randomPrompt);
    } catch (error) {
      console.error('❌ Frontend: Failed to fetch random prompt:', error);
    } finally {
      setIsLoadingRandom(false);
    }
  };

  // Handle selecting a prompt from history
  const handlePromptSelect = (prompt: string) => {
    onChange(prompt);
    setIsDropdownOpen(false);
    
    // Move selected prompt to top of history
    addPromptToHistory(prompt);
  };

  // Clear history for this prompt type
  const clearHistory = () => {
    setPromptHistory([]);
    try {
      localStorage.removeItem(storageKey);
    } catch (error) {
      console.error('Error clearing prompt history:', error);
    }
    setIsDropdownOpen(false);
  };

  // Handle textarea changes
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  // Add to history when user finishes typing (on blur)
  const handleBlur = () => {
    if (value.trim() && value !== lastSavedValue.current) {
      addPromptToHistory(value);
    }
  };

  // Handle Enter key to save to history
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      // Ctrl/Cmd + Enter saves to history
      if (value.trim()) {
        addPromptToHistory(value);
      }
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <div className="flex items-center gap-2">
          {/* History dropdown button */}
          {promptHistory.length > 0 && (
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground flex items-center gap-1 transition-colors"
                title={`View ${promptHistory.length} saved ${negative ? 'negative' : 'positive'} prompts`}
              >
                <Clock className="w-3 h-3" />
                <span className="hidden sm:inline">History</span>
                <span className="sm:hidden">{promptHistory.length}</span>
                <ChevronDown className={`w-3 h-3 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown menu */}
              {isDropdownOpen && (
                <div className="absolute right-0 top-full mt-1 w-80 max-w-[90vw] bg-background border border-input rounded-md shadow-lg z-50 max-h-60 overflow-y-auto">
                  <div className="p-2 border-b border-input flex items-center justify-between bg-muted/50">
                    <span className="text-xs font-medium text-foreground">
                      {negative ? 'Negative' : 'Positive'} Prompts ({promptHistory.length})
                    </span>
                    <button
                      type="button"
                      onClick={clearHistory}
                      className="text-xs text-destructive hover:text-destructive/80 flex items-center gap-1 transition-colors"
                      title="Clear all history"
                    >
                      <X className="w-3 h-3" />
                      Clear
                    </button>
                  </div>
                  
                  {promptHistory.map((prompt, index) => (
                    <button
                      key={`${prompt}-${index}`}
                      type="button"
                      onClick={() => handlePromptSelect(prompt)}
                      className="w-full text-left p-2 hover:bg-accent hover:text-accent-foreground border-b border-input/20 last:border-b-0 transition-colors group"
                    >
                      <div className={cn(
                        "text-xs line-clamp-2 group-hover:line-clamp-none",
                        negative ? "text-destructive" : "text-foreground"
                      )} title={prompt}>
                        {prompt}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {index === 0 ? 'Most recent' : `${index + 1} prompts ago`}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Existing Add Random button */}
          {showAddRandom && (
            <button 
              onClick={handleAddRandom}
              disabled={isLoadingRandom}
              className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoadingRandom ? 'Loading...' : 'Add Random'}
            </button>
          )}
        </div>
      </div>
      
      <div className="relative">
        <textarea
          className={cn(
            "w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none",
            negative && "text-destructive"
          )}
          rows={3}
          maxLength={maxLength}
          placeholder={placeholder}
          value={value}
          onChange={handleTextChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
        />
        
        {/* Character count indicator */}
        {maxLength && value.length > maxLength * 0.8 && (
          <div className="absolute bottom-2 right-2 text-xs text-muted-foreground bg-background/80 px-1 rounded">
            {value.length}/{maxLength}
          </div>
        )}
      </div>
      
      {/* Keyboard shortcut hint */}
      {value.length > 0 && (
        <div className="text-xs text-muted-foreground">
          Press Ctrl+Enter to save to history, or click outside
        </div>
      )}
    </div>
  );
};

export default PromptInput;