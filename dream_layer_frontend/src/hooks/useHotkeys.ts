import { useHotkeys } from 'react-hotkeys-hook';

export interface HotkeyActions {
  onGenerate: () => void;
  onSaveSettings: () => void;
}

export const useAppHotkeys = (actions: HotkeyActions) => {
  // Ctrl + Enter for Generate Image
  useHotkeys('ctrl+enter', (event) => {
    event.preventDefault();
    actions.onGenerate();
  }, {
    enableOnFormTags: true, // Allow hotkeys to work in form elements
    enableOnContentEditable: true,
    preventDefault: true,
  });

  // Shift + S for Save Settings
  useHotkeys('shift+s', (event) => {
    event.preventDefault();
    actions.onSaveSettings();
  }, {
    enableOnFormTags: true,
    enableOnContentEditable: true,
    preventDefault: true,
  });
};

// Export keyboard shortcut labels for use in tooltips
export const HOTKEYS = {
  GENERATE: 'Ctrl+Enter',
  SAVE_SETTINGS: 'Shift+S',
} as const;
