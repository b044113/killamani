/**
 * Settings Component
 *
 * User settings and preferences page
 */
import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Divider,
  Alert,
  Snackbar,
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { useAuthStore } from '@/features/auth/hooks/useAuthStore';
import { LANGUAGE_NAMES, type SupportedLanguage } from '@/shared/i18n/config';

export const Settings: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuthStore();
  const [language, setLanguage] = useState<SupportedLanguage>(
    (i18n.language as SupportedLanguage) || 'en'
  );
  const [successMessage, setSuccessMessage] = useState('');

  const handleLanguageChange = (newLanguage: SupportedLanguage) => {
    setLanguage(newLanguage);
    i18n.changeLanguage(newLanguage);
    setSuccessMessage(t('settings.profileUpdated'));
  };

  const handleSaveProfile = () => {
    // TODO: Implement profile update API call
    setSuccessMessage(t('settings.profileUpdated'));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('settings.title')}
        </Typography>

        {/* Account Settings */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('settings.account')}
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Email"
                value={user?.email || ''}
                fullWidth
                disabled
                helperText="Email cannot be changed"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="First Name"
                value={user?.firstName || ''}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Last Name"
                value={user?.lastName || ''}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Role"
                value={user?.role || ''}
                fullWidth
                disabled
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSaveProfile}
            >
              {t('common.save')}
            </Button>
          </Box>
        </Paper>

        {/* Language Settings */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('settings.language')}
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('settings.language')}</InputLabel>
                <Select
                  value={language}
                  onChange={(e) => handleLanguageChange(e.target.value as SupportedLanguage)}
                  label={t('settings.language')}
                >
                  {Object.entries(LANGUAGE_NAMES).map(([code, name]) => (
                    <MenuItem key={code} value={code}>
                      {name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Paper>

        {/* Password Change */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('settings.changePassword')}
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label={t('settings.currentPassword')}
                type="password"
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label={t('settings.newPassword')}
                type="password"
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label={t('settings.confirmNewPassword')}
                type="password"
                fullWidth
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 3 }}>
            <Button variant="contained" startIcon={<SaveIcon />}>
              {t('settings.changePassword')}
            </Button>
          </Box>
        </Paper>

        {/* Success Snackbar */}
        <Snackbar
          open={!!successMessage}
          autoHideDuration={3000}
          onClose={() => setSuccessMessage('')}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => setSuccessMessage('')}
            severity="success"
            sx={{ width: '100%' }}
          >
            {successMessage}
          </Alert>
        </Snackbar>
      </Box>
    </Container>
  );
};
