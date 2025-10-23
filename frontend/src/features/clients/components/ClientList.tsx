/**
 * ClientList Component
 *
 * Displays list of clients with search, create, edit, and delete actions
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  IconButton,
  InputAdornment,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useTranslation } from '@/shared/hooks/useTranslation';
import { useClients, useDeleteClient } from '../hooks/useClients';
import { ClientForm } from './ClientForm';
import type { Client } from '../types';

export const ClientList: React.FC = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [page] = useState(1);
  const [pageSize] = useState(10);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<Client | null>(null);

  const { data, isLoading, error } = useClients({ page, pageSize, search });
  const deleteClient = useDeleteClient();

  const handleCreateClick = () => {
    setSelectedClient(null);
    setIsFormOpen(true);
  };

  const handleEditClick = (client: Client) => {
    setSelectedClient(client);
    setIsFormOpen(true);
  };

  const handleDeleteClick = (client: Client) => {
    setClientToDelete(client);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (clientToDelete) {
      await deleteClient.mutateAsync(clientToDelete.id);
      setIsDeleteDialogOpen(false);
      setClientToDelete(null);
    }
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setSelectedClient(null);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {t('errors.generic')}: {error.message}
      </Alert>
    );
  }

  const clients = data?.clients || [];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          {t('clients.title')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateClick}
        >
          {t('clients.addClient')}
        </Button>
      </Box>

      {/* Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder={t('clients.searchClients')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      {/* Clients Table */}
      {clients.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            {t('clients.noClients')}
          </Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleCreateClick}
            sx={{ mt: 2 }}
          >
            {t('clients.addClient')}
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('clients.firstName')}</TableCell>
                <TableCell>{t('clients.lastName')}</TableCell>
                <TableCell>{t('clients.email')}</TableCell>
                <TableCell>{t('clients.birthDate')}</TableCell>
                <TableCell>{t('clients.birthPlace')}</TableCell>
                <TableCell align="right">{t('common.edit')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map((client) => (
                <TableRow key={client.id} hover>
                  <TableCell>{client.firstName}</TableCell>
                  <TableCell>{client.lastName}</TableCell>
                  <TableCell>{client.email || '-'}</TableCell>
                  <TableCell>
                    {new Date(client.birthDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>{client.birthPlace}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleEditClick(client)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(client)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Client Form Dialog */}
      <ClientForm
        open={isFormOpen}
        client={selectedClient}
        onClose={handleFormClose}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>{t('clients.deleteClient')}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('clients.confirmDelete')}
          </Typography>
          {clientToDelete && (
            <Typography variant="body2" sx={{ mt: 2 }}>
              <strong>
                {clientToDelete.firstName} {clientToDelete.lastName}
              </strong>
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>
            {t('common.cancel')}
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteClient.isPending}
          >
            {deleteClient.isPending ? <CircularProgress size={24} /> : t('common.delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
