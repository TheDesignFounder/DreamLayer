
import { useState, useEffect } from "react";
import { Slider as ShadcnSlider } from "@/components/ui/slider";
import { SliderTooltip } from "@/components/SliderTooltip";
import { getTooltipContent } from "@/utils/tooltipDefinitions";

interface SliderProps {
  min: number;
  max: number;
  defaultValue: number;
  label: string;
  sublabel?: string;
  inputWidth?: string;
  onChange?: (value: number) => void;
  hideInput?: boolean;
  step?: number;
  tooltipKey?: string; // Key to look up tooltip content
}

const Slider = ({
  min,
  max,
  defaultValue,
  label,
  sublabel,
  inputWidth = "w-16",
  onChange,
  hideInput = false,
  step,
  tooltipKey,
}: SliderProps) => {
  const [value, setValue] = useState(defaultValue);

  const handleChange = (newValue: number[]) => {
    setValue(newValue[0]);
    if (onChange) {
      onChange(newValue[0]);
    }
  };
  
  useEffect(() => {
    // Call onChange with initial value
    if (onChange) {
      onChange(defaultValue);
    }
  }, []);

  // Update internal state when defaultValue prop changes (for reset functionality)
  useEffect(() => {
    setValue(defaultValue);
  }, [defaultValue]);

  // Get tooltip content if tooltipKey is provided
  const tooltipContent = tooltipKey ? getTooltipContent(tooltipKey as any) : null;

  return (
    <div className="mb-4 p-3 rounded-lg border border-border/50 bg-card/30 glass-morphism hover:shadow-sm transition-all duration-300">
      <div className="flex items-center justify-between mb-3">
        {label && (
          <div className="text-sm font-medium flex items-center">
            <span dangerouslySetInnerHTML={{ __html: label }} />
            {sublabel && <span className="ml-1 text-xs text-muted-foreground">{sublabel}</span>}
            {tooltipContent && <SliderTooltip content={tooltipContent} className="ml-2" />}
          </div>
        )}
        {!hideInput && (
          <div className="flex items-center gap-2">
            {/* Min/Max Container */}
            <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-muted/30 border border-border/50">
              <div className="flex flex-col items-center">
                <span className="text-[10px] text-muted-foreground leading-none">Min</span>
                <span className="text-xs font-medium text-foreground">{min}</span>
              </div>
              <div className="w-px h-6 bg-border mx-1"></div>
              <div className="flex flex-col items-center">
                <span className="text-[10px] text-muted-foreground leading-none">Max</span>
                <span className="text-xs font-medium text-foreground">{max}</span>
              </div>
            </div>
            
            {/* Value Input with Up/Down Controls */}
            <div className="relative flex items-center">
              <input
                type="number"
                className={`rounded-md border border-input bg-background px-2 py-1 text-center text-xs ${inputWidth} glass-morphism transition-all duration-300 hover:shadow-md focus:shadow-lg focus:ring-2 focus:ring-primary/50 focus:border-primary pr-6 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none`}
                min={min}
                max={max}
                step={step || (min < 1 ? 0.1 : 1)}
                value={value}
                onChange={(e) => {
                  const newValue = Number(e.target.value);
                  setValue(newValue);
                  if (onChange) {
                    onChange(newValue);
                  }
                }}
                onKeyDown={(e) => {
                  // Handle keyboard shortcuts
                  if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const stepValue = step || (min < 1 ? 0.1 : 1);
                    const newValue = Math.min(max, Number((value + stepValue).toFixed(min < 1 ? 1 : 0)));
                    setValue(newValue);
                    if (onChange) {
                      onChange(newValue);
                    }
                  } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const stepValue = step || (min < 1 ? 0.1 : 1);
                    const newValue = Math.max(min, Number((value - stepValue).toFixed(min < 1 ? 1 : 0)));
                    setValue(newValue);
                    if (onChange) {
                      onChange(newValue);
                    }
                  }
                }}
                onBlur={(e) => {
                  // Ensure value is within bounds when user finishes editing
                  let newValue = Number(e.target.value);
                  newValue = Math.max(min, Math.min(max, newValue));
                  setValue(newValue);
                  if (onChange) {
                    onChange(newValue);
                  }
                }}
              />
              
              {/* Custom Up/Down Buttons */}
              <div className="absolute right-1 flex flex-col">
                <button
                  type="button"
                  className="p-0.5 hover:bg-accent rounded transition-colors"
                  onClick={() => {
                    const stepValue = step || (min < 1 ? 0.1 : 1);
                    const newValue = Math.min(max, Number((value + stepValue).toFixed(min < 1 ? 1 : 0)));
                    setValue(newValue);
                    if (onChange) {
                      onChange(newValue);
                    }
                  }}
                >
                  <svg className="w-2.5 h-2.5 text-muted-foreground hover:text-foreground" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                </button>
                <button
                  type="button"
                  className="p-0.5 hover:bg-accent rounded transition-colors"
                  onClick={() => {
                    const stepValue = step || (min < 1 ? 0.1 : 1);
                    const newValue = Math.max(min, Number((value - stepValue).toFixed(min < 1 ? 1 : 0)));
                    setValue(newValue);
                    if (onChange) {
                      onChange(newValue);
                    }
                  }}
                >
                  <svg className="w-2.5 h-2.5 text-muted-foreground hover:text-foreground" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Current Value Display with Quick Presets */}
      <div className="flex items-center justify-center mb-3 gap-2">
        {/* Quick preset buttons for common values */}
        {(() => {
          const commonValues = [];
          const range = max - min;
          if (range > 10) {
            commonValues.push(min, Math.round(min + range * 0.25), Math.round(min + range * 0.5), Math.round(min + range * 0.75), max);
          } else if (range > 2) {
            commonValues.push(min, Math.round((min + max) / 2), max);
          }
          
          return commonValues.length > 0 && (
            <div className="flex items-center gap-1 mr-2">
              {commonValues.map((presetValue, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => {
                    setValue(presetValue);
                    if (onChange) {
                      onChange(presetValue);
                    }
                  }}
                  className={`px-2 py-0.5 text-xs rounded transition-all duration-200 ${
                    value === presetValue 
                      ? 'bg-primary text-primary-foreground shadow-sm' 
                      : 'bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  {presetValue}
                </button>
              ))}
            </div>
          );
        })()}
        
        {/* Current value display */}
        <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
          <span className="text-sm font-semibold text-primary">{value}</span>
        </div>
      </div>
      
      {/* Slider Track */}
      <div className="px-2">
        <ShadcnSlider
          min={min}
          max={max}
          step={step || (min < 1 ? 0.1 : 1)}
          value={[value]}
          onValueChange={handleChange}
        />
      </div>
    </div>
  );
};

export default Slider;
