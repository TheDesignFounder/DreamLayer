
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
    <div className="mb-4">
      <div className="flex items-center justify-between">
        {label && (
          <div className="text-sm font-medium flex items-center">
            <span dangerouslySetInnerHTML={{ __html: label }} />
            {sublabel && <span className="ml-1 text-xs text-muted-foreground">{sublabel}</span>}
            {tooltipContent && <SliderTooltip content={tooltipContent} className="ml-2" />}
          </div>
        )}
        {!hideInput && (
          <div className="flex items-center text-xs">
            <span className="mr-1 text-muted-foreground">Min: {min}</span>
            <span className="mx-1 text-muted-foreground">Max: {max}</span>
            <input
              type="number"
              className={`rounded-md border border-input bg-background px-2 py-1 text-right text-xs ${inputWidth} glass-morphism transition-all duration-300 hover:shadow-md focus:shadow-lg`}
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
            />
          </div>
        )}
      </div>
      <div className="py-2">
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
