import { create } from "zustand";

type HotkeyAction = () => void;

interface HotkeyState {
  hotkeys: Map<string, HotkeyAction>;
  registerHotkey: (hotkey: string, callback: HotkeyAction) => void;
  unregisterHotkey: (hotkey: string) => void;
  getHotkey: (hotkey: string) => HotkeyAction | null;
}

const useHotkeyStore = create<HotkeyState>((set, get) => ({
  hotkeys: new Map<string, HotkeyAction>(),

  registerHotkey: (hotkey: string, callback: HotkeyAction) =>
    set((state) => {
      const newHotkeys = new Map(state.hotkeys);
      newHotkeys.set(hotkey, callback);
      return { hotkeys: newHotkeys };
    }),

  unregisterHotkey: (hotkey: string) =>
    set((state) => {
      const newHotkeys = new Map(state.hotkeys);
      newHotkeys.delete(hotkey);
      return { hotkeys: newHotkeys };
    }),

  getHotkey: (hotkey: string) => {
    const state = get();
    return state.hotkeys.get(hotkey) || null;
  },
}));

export default useHotkeyStore;
