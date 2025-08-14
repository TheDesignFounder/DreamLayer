import React, { createContext, useContext, useState, ReactNode } from 'react';
import { en } from './en';
import { fr } from './fr';

// Define the translation structure type
type TranslationKeys = typeof en;

// Available languages
const languages = {
  en: { name: 'English', flag: '🇺🇸' },
  fr: { name: 'Français', flag: '🇫🇷' }
} as const;

type LanguageCode = keyof typeof languages;

// Context interface
interface I18nContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (key: string) => string;
  availableLanguages: typeof languages;
}

// Create the context
const I18nContext = createContext<I18nContextType | undefined>(undefined);

// Translation function that handles nested keys
const getNestedValue = (obj: any, key: string): string => {
  const keys = key.split('.');
  let value = obj;

  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      // Fallback to English if key not found
      const fallbackValue = getNestedValue(en, key);
      if (fallbackValue && typeof fallbackValue === 'object' && k in fallbackValue) {
        value = fallbackValue[k];
      } else {
        return key; // Return the key if not found anywhere
      }
    }
  }

  return typeof value === 'string' ? value : key;
};

// Provider component
interface I18nProviderProps {
  children: ReactNode;
}

export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  const [language, setLanguage] = useState<LanguageCode>('en');

  const translations: Record<LanguageCode, TranslationKeys> = {
    en,
    fr
  };

  const t = (key: string): string => {
    const currentTranslations = translations[language];
    const value = getNestedValue(currentTranslations, key);

    // If the value is the same as the key, try English as fallback
    if (value === key && language !== 'en') {
      const fallbackValue = getNestedValue(translations.en, key);
      return typeof fallbackValue === 'string' ? fallbackValue : key;
    }

    return value;
  };

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

// Hook to use the i18n context
export const useI18n = (): I18nContextType => {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};
