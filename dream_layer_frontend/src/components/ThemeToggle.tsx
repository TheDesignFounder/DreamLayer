
import { Moon, Sun } from "lucide-react";
import { useState, useEffect } from "react";

export const ThemeToggle = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if dark mode is set in localStorage or if the user prefers dark mode
    const savedTheme = localStorage.getItem("theme");
    return savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches);
  });

  useEffect(() => {
    // Update DOM and localStorage when theme changes
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <button
      onClick={toggleTheme}
      className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 hover:scale-105 ${
        isDarkMode ? "bg-slate-700 shadow-inner" : "bg-slate-200 shadow-inner"
      }`}
      aria-label={`Switch to ${isDarkMode ? "light" : "dark"} mode`}
      title={`Switch to ${isDarkMode ? "light" : "dark"} mode`}
    >
      <span className="sr-only">Toggle theme</span>
      <span
        className={`${
          isDarkMode ? "translate-x-7" : "translate-x-1"
        } inline-block h-6 w-6 transform rounded-full bg-white transition-all duration-200 ease-in-out shadow-lg flex items-center justify-center`}
      >
        {isDarkMode ? (
          <Moon className="h-4 w-4 text-slate-600" />
        ) : (
          <Sun className="h-4 w-4 text-yellow-500" />
        )}
      </span>
    </button>
  );
};
