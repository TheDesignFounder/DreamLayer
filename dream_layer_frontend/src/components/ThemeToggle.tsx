
import { Moon, Sun } from "lucide-react";
import { useState, useEffect } from "react";

export const ThemeToggle = () => {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if theme is set in localStorage, default to light mode
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      return savedTheme === "dark";
    }
    // Default to light mode (white and blue theme)
    return false;
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
      className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 hover:scale-105 glass-morphism ${
        isDarkMode ? "bg-slate-700/50 shadow-inner" : "bg-blue-100/50 shadow-inner border-blue-200"
      }`}
      aria-label={`Switch to ${isDarkMode ? "light" : "dark"} mode`}
      title={`Switch to ${isDarkMode ? "light" : "dark"} mode`}
    >
      <span className="sr-only">Toggle theme</span>
      <span
        className={`${
          isDarkMode ? "translate-x-7" : "translate-x-1"
        } inline-block h-6 w-6 transform rounded-full transition-all duration-300 ease-in-out shadow-lg flex items-center justify-center ${
          isDarkMode ? "bg-slate-800" : "bg-white border border-blue-200"
        }`}
      >
        {isDarkMode ? (
          <Moon className="h-4 w-4 text-blue-400" />
        ) : (
          <Sun className="h-4 w-4 text-blue-600" />
        )}
      </span>
    </button>
  );
};
