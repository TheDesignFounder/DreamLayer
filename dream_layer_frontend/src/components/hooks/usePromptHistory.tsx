import { useEffect, useState } from "react";

export const getPromptHistory = (key: string): string[] => {
  try {
    return JSON.parse(localStorage.getItem(key) || "[]");
  } catch {
    return [];
  }
};

export const savePromptToHistory = (key: string, prompt: string): string[] => {
  let history = getPromptHistory(key);
  history = [prompt, ...history.filter(p => p !== prompt)].slice(0, 10);
  localStorage.setItem(key, JSON.stringify(history));
  return history;
};

export const usePromptHistory = (key?: string) => {
  const [history, setHistory] = useState<string[]>([]);

  useEffect(() => {
    if (key) {
      setHistory(getPromptHistory(key));
    }
  }, [key]);


  const addPrompt = (prompt: string) => {
    if (!key) return;
    const updated = savePromptToHistory(key, prompt);
    setHistory(updated);
  };

  return { history, addPrompt };
};
