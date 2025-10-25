/**
 * Client Types
 */

export interface Client {
  id: string;
  userId?: string;
  consultantId: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email?: string;
  phone?: string;
  // Birth data is now optional - charts are stored separately
  birthDate?: string; // ISO date string
  birthCity?: string;
  birthCountry?: string;
  birthTimezone?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  hasAccount: boolean;
}

export interface CreateClientDTO {
  firstName: string;
  lastName: string;
  email?: string;
  phone?: string;
  notes?: string;
}

export interface UpdateClientDTO extends Partial<CreateClientDTO> {
  id: string;
}

export interface ClientListResponse {
  clients: Client[];
  total: number;
  skip: number;
  limit: number;
}
