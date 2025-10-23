import { useTranslation as useI18nTranslation } from 'react-i18next';
import type { SupportedLanguage } from '../i18n/config';

/**
 * Custom hook that wraps react-i18next's useTranslation
 * Provides type-safe translation function and language change utilities
 */
export const useTranslation = () => {
  const { t, i18n } = useI18nTranslation();

  const changeLanguage = async (language: SupportedLanguage) => {
    await i18n.changeLanguage(language);
  };

  return {
    t,
    i18n,
    language: i18n.language as SupportedLanguage,
    changeLanguage,
  };
};
