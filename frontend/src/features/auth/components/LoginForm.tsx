/**
 * Login Form Component
 *
 * Form for user authentication
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../hooks/useAuthStore';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { LanguageSwitcher } from '@/shared/components/LanguageSwitcher';
import type { LoginCredentials } from '@/types';

export const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { login, isLoading, error, clearError } = useAuthStore();

  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await login(formData);
      navigate('/dashboard');
    } catch (error) {
      // Error is handled by the store
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        bgcolor: 'background.default',
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 400,
          width: '100%',
          mx: 2,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <LanguageSwitcher />
        </Box>

        <Typography variant="h4" component="h1" gutterBottom align="center">
          {t('common.appName')}
        </Typography>

        <Typography variant="h6" gutterBottom align="center" color="text.secondary">
          {t('auth.signIn')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label={t('auth.email')}
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            margin="normal"
            autoComplete="email"
            autoFocus
          />

          <TextField
            fullWidth
            label={t('auth.password')}
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            required
            margin="normal"
            autoComplete="current-password"
          />

          <Button
            fullWidth
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mt: 3, mb: 2 }}
          >
            {isLoading ? <CircularProgress size={24} /> : t('auth.signIn')}
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2">
              {t('auth.dontHaveAccount')}{' '}
              <Link to="/register" style={{ textDecoration: 'none' }}>
                {t('auth.signUp')}
              </Link>
            </Typography>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};
