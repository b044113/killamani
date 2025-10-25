/**
 * ClientForm Component
 *
 * Form for creating and editing clients
 */
import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { useCreateClient, useUpdateClient } from '../hooks/useClients';
import type { Client, CreateClientDTO } from '../types';

interface ClientFormProps {
  open: boolean;
  client?: Client | null;
  onClose: () => void;
}

export const ClientForm: React.FC<ClientFormProps> = ({ open, client, onClose }) => {
  const { t } = useTranslation();
  const createClient = useCreateClient();
  const updateClient = useUpdateClient();
  const isEditing = !!client;

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateClientDTO>({
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      notes: '',
    },
  });

  useEffect(() => {
    if (client) {
      reset({
        firstName: client.firstName,
        lastName: client.lastName,
        email: client.email || '',
        phone: client.phone || '',
        notes: client.notes || '',
      });
    } else {
      reset({
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        notes: '',
      });
    }
  }, [client, reset]);

  const onSubmit = async (data: CreateClientDTO) => {
    try {
      if (isEditing && client) {
        await updateClient.mutateAsync({ id: client.id, data });
      } else {
        await createClient.mutateAsync(data);
      }
      onClose();
    } catch (error) {
      console.error('Error submitting client form:', error);
    }
  };

  const isPending = createClient.isPending || updateClient.isPending;
  const error = createClient.error || updateClient.error;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>
          {isEditing ? t('clients.editClient') : t('clients.addClient')}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error.message}
            </Alert>
          )}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <Controller
                name="firstName"
                control={control}
                rules={{ required: t('clients.firstName') + ' is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label={t('clients.firstName')}
                    fullWidth
                    error={!!errors.firstName}
                    helperText={errors.firstName?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="lastName"
                control={control}
                rules={{ required: t('clients.lastName') + ' is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label={t('clients.lastName')}
                    fullWidth
                    error={!!errors.lastName}
                    helperText={errors.lastName?.message}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label={t('clients.email')}
                    type="email"
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="phone"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label={t('clients.phone')}
                    fullWidth
                  />
                )}
              />
            </Grid>
            <Grid item xs={12}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label={t('clients.notes')}
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={isPending}>
            {t('common.cancel')}
          </Button>
          <Button type="submit" variant="contained" disabled={isPending}>
            {isPending ? <CircularProgress size={24} /> : t('common.save')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
