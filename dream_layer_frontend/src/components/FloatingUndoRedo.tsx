import React from 'react';
import { Button } from '@/components/ui/button';
import { Undo2, Redo2 } from 'lucide-react';

interface FloatingUndoRedoProps {
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

const FloatingUndoRedo: React.FC<FloatingUndoRedoProps> = ({
  onUndo,
  onRedo,
  canUndo,
  canRedo
}) => {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex gap-2">
      <Button
        onClick={onUndo}
        variant="outline"
        size="sm"
        disabled={!canUndo}
        className="bg-background/95 backdrop-blur-sm border-border shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2"
        title="Undo (Ctrl+Z)"
      >
        <Undo2 className="h-4 w-4" />
        <span className="hidden sm:inline">Undo</span>
      </Button>
      <Button
        onClick={onRedo}
        variant="outline"
        size="sm"
        disabled={!canRedo}
        className="bg-background/95 backdrop-blur-sm border-border shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-2"
        title="Redo (Ctrl+Y)"
      >
        <Redo2 className="h-4 w-4" />
        <span className="hidden sm:inline">Redo</span>
      </Button>
    </div>
  );
};

export default FloatingUndoRedo;