import useHotkeyStore from "@/stores/useHotkeyStore";
import { useCallback, useEffect } from "react";

export default function useHotkeys() {
  const { getHotkey } = useHotkeyStore();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;

      const isTypingField =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable;

      if (isTypingField) return;

      const modifiers = [];
      if (event.ctrlKey) modifiers.push("Ctrl");
      if (event.shiftKey) modifiers.push("Shift");
      if (event.altKey) modifiers.push("Alt");

      const key = event.key;
      const keyCombination =
        modifiers.length > 0 ? `${modifiers.join("+")}+${key}` : key;

      const hotkey = getHotkey(keyCombination);
      if (hotkey) {
        event.preventDefault();
        hotkey();
      }
    },
    [getHotkey]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
}
