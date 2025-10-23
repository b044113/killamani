/**
 * Client Types
 */

export interface Client {
  id: string;
  userId: string;
  firstName: string;
  lastName: string;
  email?: string;
  phone?: string;
  birthDate: string; // ISO date string
  birthTime: string; // HH:MM format
  birthPlace: string;
  latitude: number;
  longitude: number;
  timezone: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateClientDTO {
  firstName: string;
  lastName: string;
  email?: string;
  phone?: string;
  birthDate: string;
  birthTime: string;
  birthPlace: string;
  latitude: number;
  longitude: number;
  timezone: string;
  notes?: string;
}

export interface UpdateClientDTO extends Partial<CreateClientDTO> {
  id: string;
}

export interface ClientListResponse {
  clients: Client[];
  total: number;
  page: number;
  pageSize: number;
}
