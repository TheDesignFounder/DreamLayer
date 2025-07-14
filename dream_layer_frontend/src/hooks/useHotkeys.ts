import { useEffect } from "react";

export function useHotkeys({ onGenerate }: { onGenerate: () => void }) {
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ctrl + Enter triggers generation
      if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        onGenerate(); // call the function
      }

      // Shift + S is reserved for "Save Settings" (if implemented)
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onGenerate]);
}
