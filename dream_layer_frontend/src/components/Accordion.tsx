
import { ChevronDown, RotateCcw } from "lucide-react";
import { useState } from "react";

interface AccordionProps {
  title: string;
  number?: string | number;
  defaultOpen?: boolean;
  children: React.ReactNode;
  onReset?: () => void; // Optional reset function
  showResetButton?: boolean; // Whether to show the reset button
}

const Accordion = ({ title, number, defaultOpen = false, children, onReset, showResetButton = false }: AccordionProps) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const handleReset = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent accordion from opening/closing
    if (onReset) {
      onReset();
    }
  };

  return (
    <div className="mb-4 overflow-hidden rounded-md border border-border">
      <button
        className="flex w-full items-center justify-between bg-background p-3 text-left font-medium"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="flex items-center">
          {number && <span className="mr-2 text-foreground">{number}.</span>}
          {title}
        </span>
        <div className="flex items-center gap-2">
          {showResetButton && onReset && (
            <button
              onClick={handleReset}
              className="flex items-center gap-1 rounded px-2 py-1 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              title="Reset to defaults"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </button>
          )}
          <ChevronDown
            className={`h-5 w-5 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
          />
        </div>
      </button>
      <div
        className={`bg-card px-4 transition-all ${
          isOpen ? "max-h-[2000px] py-4" : "max-h-0 py-0"
        }`}
      >
        {children}
      </div>
    </div>
  );
};

export default Accordion;
