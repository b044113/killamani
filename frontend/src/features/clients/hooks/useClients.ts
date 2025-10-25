/**
 * useClients Hook
 *
 * Custom hook for managing client data with React Query
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { clientService } from '../services/clientService';
import type { CreateClientDTO } from '../types';

const QUERY_KEY = 'clients';

/**
 * Hook to fetch all clients
 */
export const useClients = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: [QUERY_KEY, params],
    queryFn: () => clientService.getClients(params),
  });
};

/**
 * Hook to fetch a single client
 */
export const useClient = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEY, id],
    queryFn: () => clientService.getClient(id),
    enabled: !!id,
  });
};

/**
 * Hook to create a new client
 */
export const useCreateClient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateClientDTO) => clientService.createClient(data),
    onSuccess: () => {
      // Invalidate and refetch clients list
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
};

/**
 * Hook to update an existing client
 */
export const useUpdateClient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateClientDTO> }) =>
      clientService.updateClient(id, data),
    onSuccess: (_, variables) => {
      // Invalidate both the list and the individual client
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY, variables.id] });
    },
  });
};

/**
 * Hook to delete a client
 */
export const useDeleteClient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => clientService.deleteClient(id),
    onSuccess: () => {
      // Invalidate clients list
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
  });
};
