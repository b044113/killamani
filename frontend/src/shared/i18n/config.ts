import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import { initReactI18next } from 'react-i18next';

// Import translation files
import de from './locales/de.json';
import en from './locales/en.json';
import es from './locales/es.json';
import fr from './locales/fr.json';
import it from './locales/it.json';
import pt from './locales/pt.json';

// Available languages
export const SUPPORTED_LANGUAGES = ['es', 'en', 'it', 'fr', 'de', 'pt'] as const;
export type SupportedLanguage = typeof SUPPORTED_LANGUAGES[number];

// Language names for the language selector
export const LANGUAGE_NAMES: Record<SupportedLanguage, string> = {
  es: 'Español',
  en: 'English',
  it: 'Italiano',
  fr: 'Français',
  de: 'Deutsch',
  pt: 'Português (BR)',
};

// Get default language from environment or use 'en' as fallback
const defaultLanguage = (import.meta.env.VITE_DEFAULT_LANGUAGE || 'en') as SupportedLanguage;

// Initialize i18next
i18n
  .use(LanguageDetector) // Detects user language
  .use(initReactI18next) // Passes i18n down to react-i18next
  .init({
    resources: {
      es: { translation: es },
      en: { translation: en },
      it: { translation: it },
      fr: { translation: fr },
      de: { translation: de },
      pt: { translation: pt },
    },
    fallbackLng: defaultLanguage,
    supportedLngs: SUPPORTED_LANGUAGES,
    detection: {
      // Order of language detection
      order: ['localStorage', 'navigator', 'htmlTag'],
      // Cache user language in localStorage
      caches: ['localStorage'],
      // localStorage key
      lookupLocalStorage: 'killamani_language',
    },
    interpolation: {
      escapeValue: false, // React already escapes values
    },
    debug: import.meta.env.MODE === 'development',
  });

export default i18n;
