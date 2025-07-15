import { useEffect } from 'react';
import { useKeyboardShortcuts } from '@/contexts/KeyboardShortcutsContext';

interface HotkeyMap {
  [key: string]: () => void;
}

export const useHotkeys = (hotkeys: HotkeyMap) => {
  const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts();

  useEffect(() => {
    Object.entries(hotkeys).forEach(([key, action]) => {
      registerShortcut(key, action);
    });

    return () => {
      Object.keys(hotkeys).forEach(key => {
        unregisterShortcut(key);
      });
    };
  }, [hotkeys, registerShortcut, unregisterShortcut]);
};
