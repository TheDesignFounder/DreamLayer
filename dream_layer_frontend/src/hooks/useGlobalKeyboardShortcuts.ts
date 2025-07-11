import { useKeyboardShortcuts, KeyboardShortcut } from './useKeyboardShortcuts';

interface GlobalKeyboardShortcutsProps {
  onGenerate?: () => void;
  onOpenSettings?: () => void;
  onCancel?: () => void;
  isGenerating?: boolean;
}

export const useGlobalKeyboardShortcuts = ({
  onGenerate,
  onOpenSettings, 
  onCancel,
  isGenerating = false
}: GlobalKeyboardShortcutsProps) => {
  const shortcuts: KeyboardShortcut[] = [
    // Ctrl+Enter: Generate Image
    {
      key: 'Enter',
      ctrlKey: true,
      callback: () => {
        if (onGenerate) {
          onGenerate();
        }
      },
      description: 'Generate Image (Ctrl+Enter)'
    },
    // Shift+S: Open Settings
    {
      key: 'S',
      shiftKey: true,
      callback: () => {
        if (onOpenSettings) {
          onOpenSettings();
        }
      },
      description: 'Open Settings (Shift+S)'
    },
    // ESC: Cancel current operation
    {
      key: 'Escape',
      callback: () => {
        if (isGenerating && onCancel) {
          onCancel();
        }
      },
      description: 'Cancel Generation (ESC)'
    }
  ];

  useKeyboardShortcuts(shortcuts);

  return {
    shortcuts: shortcuts.filter(s => s.description) // Return shortcuts for documentation
  };
};