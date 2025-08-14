import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { en } from './en';
import { fr } from './fr';

// Define the translation structure type
type TranslationKeys = typeof en;

// Available languages
export const languages = {
  en: { name: 'English', flag: '🇺🇸' },
  fr: { name: 'Français', flag: '🇫🇷' }
};

// Translation data
const translations: Record<string, TranslationKeys> = {
  en,
  fr
};

// Context interface
interface I18nContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
  availableLanguages: typeof languages;
}

// Create context
const I18nContext = createContext<I18nContextType | undefined>(undefined);

// Hook to use i18n context
export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

// Provider component
interface I18nProviderProps {
  children: ReactNode;
}

export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  // Get initial language from localStorage or default to 'en'
  const [language, setLanguageState] = useState(() => {
    const saved = localStorage.getItem('dreamlayer-language');
    return saved && translations[saved] ? saved : 'en';
  });

  // Translation function
  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations[language] || translations['en'];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // Fallback to English if key not found
        value = translations['en'];
        for (const fallbackKey of keys) {
          if (value && typeof value === 'object' && fallbackKey in value) {
            value = value[fallbackKey];
          } else {
            return key; // Return the key if not found even in English
          }
        }
        break;
      }
    }

    return typeof value === 'string' ? value : key;
  };

  // Set language function
  const setLanguage = (lang: string) => {
    if (translations[lang]) {
      setLanguageState(lang);
      localStorage.setItem('dreamlayer-language', lang);
      // Update document language attribute
      document.documentElement.lang = lang;
    }
  };

  // Update document language when language changes
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const value: I18nContextType = {
    language,
    setLanguage,
    t,
    availableLanguages: languages
  };

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
};
