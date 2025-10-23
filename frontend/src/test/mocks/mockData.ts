// Mock data for testing - NO SENSITIVE INFORMATION
// All passwords and tokens are fake and for testing purposes only

import type { User, Client, NatalChart } from '@/types'

// Mock user data - FAKE DATA FOR TESTING ONLY
export const mockUser: User = {
  id: 'test-user-id-123',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
}

export const mockAdminUser: User = {
  id: 'test-admin-id-456',
  email: 'admin@example.com',
  name: 'Test Admin',
  role: 'admin',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
}

// Mock authentication tokens - FAKE TOKENS FOR TESTING
export const mockTokens = {
  access: 'mock-access-token-abcdef123456',
  refresh: 'mock-refresh-token-xyz789',
}

// Mock login credentials - FAKE CREDENTIALS FOR TESTING
export const mockLoginCredentials = {
  email: 'test@example.com',
  password: 'Test123456!', // Fake password for testing only
}

// Mock client data
export const mockClient: Client = {
  id: 'client-123',
  userId: 'test-user-id-123',
  name: 'John Doe',
  birthDate: '1990-05-15',
  birthTime: '14:30',
  birthPlace: 'New York, USA',
  timezone: 'America/New_York',
  latitude: 40.7128,
  longitude: -74.0060,
  notes: 'Test client notes',
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
}

export const mockClients: Client[] = [
  mockClient,
  {
    id: 'client-456',
    userId: 'test-user-id-123',
    name: 'Jane Smith',
    birthDate: '1985-08-20',
    birthTime: '08:15',
    birthPlace: 'Los Angeles, USA',
    timezone: 'America/Los_Angeles',
    latitude: 34.0522,
    longitude: -118.2437,
    notes: '',
    createdAt: '2024-01-02T00:00:00Z',
    updatedAt: '2024-01-02T00:00:00Z',
  },
]

// Mock natal chart data
export const mockNatalChart: NatalChart = {
  id: 'chart-123',
  clientId: 'client-123',
  userId: 'test-user-id-123',
  chartType: 'natal',
  calculationDate: '2024-01-01T00:00:00Z',
  planets: [
    {
      name: 'Sun',
      longitude: 124.5678,
      latitude: 0.0001,
      speed: 1.0,
      sign: 'Leo',
      degree: 4.5678,
      house: 10,
      isRetrograde: false,
    },
    {
      name: 'Moon',
      longitude: 245.1234,
      latitude: 5.1234,
      speed: 13.2,
      sign: 'Sagittarius',
      degree: 5.1234,
      house: 2,
      isRetrograde: false,
    },
  ],
  houses: [
    { number: 1, longitude: 0.0, sign: 'Aries', degree: 0.0 },
    { number: 2, longitude: 30.0, sign: 'Taurus', degree: 0.0 },
  ],
  aspects: [
    {
      planet1: 'Sun',
      planet2: 'Moon',
      aspect: 'trine',
      angle: 120.0,
      orb: 2.5,
    },
  ],
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
}

export const mockCharts: NatalChart[] = [mockNatalChart]

// Mock API responses
export const mockApiResponses = {
  login: {
    data: {
      user: mockUser,
      tokens: mockTokens,
    },
  },
  register: {
    data: {
      user: mockUser,
      tokens: mockTokens,
    },
  },
  getClients: {
    data: {
      items: mockClients,
      total: mockClients.length,
      page: 1,
      pageSize: 10,
    },
  },
  getClient: {
    data: mockClient,
  },
  createClient: {
    data: mockClient,
  },
  getCharts: {
    data: {
      items: mockCharts,
      total: mockCharts.length,
      page: 1,
      pageSize: 10,
    },
  },
  getChart: {
    data: mockNatalChart,
  },
}

// Mock error responses
export const mockErrorResponses = {
  unauthorized: {
    response: {
      status: 401,
      data: {
        detail: 'Unauthorized',
      },
    },
  },
  badRequest: {
    response: {
      status: 400,
      data: {
        detail: 'Bad request',
      },
    },
  },
  notFound: {
    response: {
      status: 404,
      data: {
        detail: 'Not found',
      },
    },
  },
  serverError: {
    response: {
      status: 500,
      data: {
        detail: 'Internal server error',
      },
    },
  },
}
