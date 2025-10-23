/**
 * Client Service
 *
 * API client for managing clients
 */
import { apiClient } from '@/shared/utils/apiClient';
import type { Client, CreateClientDTO, ClientListResponse } from '../types';

export const clientService = {
  /**
   * Get all clients
   */
  async getClients(params?: { page?: number; pageSize?: number; search?: string }): Promise<ClientListResponse> {
    const response = await apiClient.get<ClientListResponse>('/clients', { params });
    return response.data;
  },

  /**
   * Get a single client by ID
   */
  async getClient(id: string): Promise<Client> {
    const response = await apiClient.get<Client>(`/clients/${id}`);
    return response.data;
  },

  /**
   * Create a new client
   */
  async createClient(data: CreateClientDTO): Promise<Client> {
    const response = await apiClient.post<Client>('/clients', data);
    return response.data;
  },

  /**
   * Update an existing client
   */
  async updateClient(id: string, data: Partial<CreateClientDTO>): Promise<Client> {
    const response = await apiClient.put<Client>(`/clients/${id}`, data);
    return response.data;
  },

  /**
   * Delete a client
   */
  async deleteClient(id: string): Promise<void> {
    await apiClient.delete(`/clients/${id}`);
  },
};
