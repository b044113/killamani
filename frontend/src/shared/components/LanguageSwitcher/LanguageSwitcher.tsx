import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
} from '@mui/material';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { SUPPORTED_LANGUAGES, LANGUAGE_NAMES } from '@/shared/i18n/config';
import type { SupportedLanguage } from '@/shared/i18n/config';

interface LanguageSwitcherProps {
  variant?: 'standard' | 'outlined' | 'filled';
  size?: 'small' | 'medium';
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  variant = 'outlined',
  size = 'small',
}) => {
  const { t, language, changeLanguage } = useTranslation();

  const handleLanguageChange = async (event: SelectChangeEvent<string>) => {
    const newLanguage = event.target.value as SupportedLanguage;
    await changeLanguage(newLanguage);
  };

  return (
    <FormControl variant={variant} size={size} sx={{ minWidth: 150 }}>
      <InputLabel id="language-select-label">
        {t('settings.language')}
      </InputLabel>
      <Select
        labelId="language-select-label"
        id="language-select"
        value={language}
        label={t('settings.language')}
        onChange={handleLanguageChange}
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <MenuItem key={lang} value={lang}>
            {LANGUAGE_NAMES[lang]}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};
