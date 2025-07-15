import React, { createContext, useContext, useEffect, useRef } from 'react';

interface KeyboardShortcutsContextType {
  registerShortcut: (key: string, action: () => void) => void;
  unregisterShortcut: (key: string) => void;
}

const KeyboardShortcutsContext = createContext<KeyboardShortcutsContextType | null>(null);

interface KeyboardShortcutsProviderProps {
  children: React.ReactNode;
}

export const KeyboardShortcutsProvider: React.FC<KeyboardShortcutsProviderProps> = ({ children }) => {
  const shortcutsRef = useRef<Record<string, () => void>>({});

  const registerShortcut = (key: string, action: () => void) => {
    shortcutsRef.current[key] = action;
  };

  const unregisterShortcut = (key: string) => {
    delete shortcutsRef.current[key];
  };

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const combo = [
        e.ctrlKey ? 'Ctrl' : '',
        e.shiftKey ? 'Shift' : '',
        e.key === 'Enter' ? 'Enter' : e.key.toUpperCase()
      ].filter(Boolean).join('+');

      const action = shortcutsRef.current[combo];
      if (action) {
        e.preventDefault();
        action();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return (
    <KeyboardShortcutsContext.Provider value={{ registerShortcut, unregisterShortcut }}>
      {children}
    </KeyboardShortcutsContext.Provider>
  );
};

export const useKeyboardShortcuts = () => {
  const context = useContext(KeyboardShortcutsContext);
  if (!context) {
    throw new Error('useKeyboardShortcuts must be used within a KeyboardShortcutsProvider');
  }
  return context;
};
