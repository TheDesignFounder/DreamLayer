
import { useState, useEffect } from "react";
import { Slider as ShadcnSlider } from "@/components/ui/slider";

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

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between">
        {label && (
          <div className="text-sm font-medium">
            <span dangerouslySetInnerHTML={{ __html: label }} />
            {sublabel && <span className="ml-1 text-xs text-muted-foreground">{sublabel}</span>}
          </div>
        )}
        {!hideInput && (
          <div className="flex items-center text-xs">
            <span className="mr-1 text-muted-foreground">Min: {min}</span>
            <span className="mx-1 text-muted-foreground">Max: {max}</span>
            <input
              type="number"
              className={`rounded-md border border-input bg-background px-2 py-1 text-right text-xs ${inputWidth}`}
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
