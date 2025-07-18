
import { useState, useEffect } from "react";
import { Slider as ShadcnSlider } from "@/components/ui/slider";

interface SliderProps {
  min: number;
  max: number;
  defaultValue?: number;
  value?: number;
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
  value: controlledValue,
  label,
  sublabel,
  inputWidth = "w-16",
  onChange,
  hideInput = false,
  step,
}: SliderProps) => {
  const [internalValue, setInternalValue] = useState(defaultValue || 0);
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;

  const handleChange = (newValue: number[]) => {
    if (!isControlled) {
      setInternalValue(newValue[0]);
    }
    if (onChange) {
      onChange(newValue[0]);
    }
  };
  
  useEffect(() => {
    // Call onChange with initial value only for uncontrolled component
    if (!isControlled && onChange && defaultValue !== undefined) {
      onChange(defaultValue);
    }
  }, []);

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
                if (!isControlled) {
                  setInternalValue(newValue);
                }
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
