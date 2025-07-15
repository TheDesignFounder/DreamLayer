import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import React, { useState, useEffect, useRef } from 'react';
import { fetchRandomPrompt } from "@/services/modelService";
import { usePromptHistory } from "./hooks/usePromptHistory";

interface PromptInputProps {
  label: string;
  maxLength?: number;
  placeholder?: string;
  negative?: boolean;
  showAddRandom?: boolean;
  value: string;
  onChange: (value: string) => void;
  historyKey?: string;
}

const PromptInput: React.FC<PromptInputProps> = ({
  label,
  maxLength = 500,
  placeholder = "",
  negative = false,
  showAddRandom = true,
  value,
  onChange,
  historyKey
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const { history, addPrompt, refreshHistory } = usePromptHistory(historyKey);

  useEffect(() => {
    refreshHistory();
  }, [value]);
  


  const handleAddRandom = async () => {
    try {
      const promptType = negative ? 'negative' : 'positive';
      console.log(`🎲 Frontend: Add Random clicked for ${promptType} prompt`);
      
      const randomPrompt = await fetchRandomPrompt(promptType);
      console.log(`📝 Frontend: Got prompt: ${randomPrompt}`);
      
      // Replace existing value with random prompt
      onChange(randomPrompt);
      addPrompt(randomPrompt)
    } catch (error) {
      console.error('❌ Frontend: Failed to fetch random prompt:', error);
    }
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        {showAddRandom && (
          <button 
            onClick={handleAddRandom}
            className="text-xs rounded-md border border-input bg-background px-2 py-1 hover:bg-accent hover:text-accent-foreground"
          >
            Add Random
          </button>
        )}
      </div>
      <div className="relative w-full">
      <textarea
        className={`w-full pr-10 rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${
          negative ? 'text-red-500' : ''
        }`}
        rows={3}
        maxLength={maxLength}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />

      {history?.length > 0 && (
          <button
            className="absolute top-2 right-2 text-gray-500 hover:text-black"
             onClick={() => setShowDropdown((prev) => !prev)}
           >
            ▼
          </button>
        )}
       </div>
      {showDropdown && history.length > 0 && (
      <div className="absolute z-10 mt-1 w-1/4 bg-background border border-input rounded-md shadow-md max-h-40 overflow-y-auto">
        {history.map((item, idx) => (
          <div
            key={idx}
            onClick={() => {
              onChange(item);
              setShowDropdown(false);
            }}
            className="cursor-pointer text-sm px-3 py-2 hover:bg-accent hover:text-accent-foreground truncate "
          >
            {item}
          </div>
        ))}
      </div>
    )}
    </div>
  );
};


export default PromptInput;
