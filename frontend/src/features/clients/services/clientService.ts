/**
 * Client Service
 *
 * API client for managing clients
 */
import { apiClient } from '@/shared/utils/apiClient';
import type { Client, ClientListResponse, CreateClientDTO } from '../types';

export const clientService = {
  /**
   * Get all clients
   */
  async getClients(params?: { skip?: number; limit?: number  }): Promise<ClientListResponse> {
    console.log("llamada a clientes");
    const response = await apiClient.get<ClientListResponse>('/api/clients/', { params });
    return response.data;
  },

  /**
   * Get a single client by ID
   */
  async getClient(id: string): Promise<Client> {
    const response = await apiClient.get<Client>(`/api/clients/${id}`);
    return response.data;
  },

  /**
   * Create a new client
   */
  async createClient(data: CreateClientDTO): Promise<Client> {
    const response = await apiClient.post<Client>('/api/clients', data);
    return response.data;
  },

  /**
   * Update an existing client
   */
  async updateClient(id: string, data: Partial<CreateClientDTO>): Promise<Client> {
    const response = await apiClient.put<Client>(`/api/clients/${id}`, data);
    return response.data;
  },

  /**
   * Delete a client
   */
  async deleteClient(id: string): Promise<void> {
    await apiClient.delete(`/api/clients/${id}`);
  },
};
