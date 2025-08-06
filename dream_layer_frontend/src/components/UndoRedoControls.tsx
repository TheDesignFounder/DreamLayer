import React from 'react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { RotateCcw, RotateCw, History } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UndoRedoControlsProps {
  canUndo: boolean;
  canRedo: boolean;
  onUndo: () => void;
  onRedo: () => void;
  historySize: number;
  className?: string;
}

export const UndoRedoControls: React.FC<UndoRedoControlsProps> = ({
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  historySize,
  className
}) => {
  return (
    <TooltipProvider>
      <div className={cn("flex items-center gap-2", className)}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={onUndo}
              disabled={!canUndo}
              className="flex items-center gap-1"
            >
              <RotateCcw className="h-4 w-4" />
              <span className="hidden sm:inline">Undo</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Undo (Ctrl+Z)</p>
          </TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={onRedo}
              disabled={!canRedo}
              className="flex items-center gap-1"
            >
              <RotateCw className="h-4 w-4" />
              <span className="hidden sm:inline">Redo</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Redo (Ctrl+Y)</p>
          </TooltipContent>
        </Tooltip>
        
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-1 text-xs text-muted-foreground px-2">
              <History className="h-3 w-3" />
              <span>{historySize}</span>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>History states (max 25)</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  );
};

export default UndoRedoControls;
