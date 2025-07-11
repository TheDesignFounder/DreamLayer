import React from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Keyboard } from 'lucide-react';

const KeyboardShortcutsHelp: React.FC = () => {
  const shortcuts = [
    {
      keys: ['Ctrl', 'Enter'],
      description: 'Generate Image',
      context: 'Works on txt2img and img2img tabs'
    },
    {
      keys: ['Shift', 'S'],
      description: 'Open Settings',
      context: 'Switch to configurations tab'
    },
    {
      keys: ['Esc'],
      description: 'Cancel Generation',
      context: 'Stop current image generation'
    }
  ];

  const renderKeys = (keys: string[]) => (
    <div className="flex items-center gap-1">
      {keys.map((key, index) => (
        <React.Fragment key={key}>
          {index > 0 && <span className="text-muted-foreground">+</span>}
          <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded-lg dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">
            {key}
          </kbd>
        </React.Fragment>
      ))}
    </div>
  );

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="flex items-center gap-2"
          title="View Keyboard Shortcuts"
        >
          <Keyboard className="h-4 w-4" />
          <span className="hidden sm:inline">Shortcuts</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5" />
            Keyboard Shortcuts
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          {shortcuts.map((shortcut, index) => (
            <div key={index} className="flex flex-col space-y-1">
              <div className="flex items-center justify-between">
                {renderKeys(shortcut.keys)}
                <span className="font-medium">{shortcut.description}</span>
              </div>
              <p className="text-sm text-muted-foreground ml-0">
                {shortcut.context}
              </p>
            </div>
          ))}
          <div className="pt-2 mt-4 border-t border-border">
            <p className="text-xs text-muted-foreground">
              💡 Tip: Keyboard shortcuts work when not typing in input fields
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default KeyboardShortcutsHelp;