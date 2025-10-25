import { apiClient } from '@/shared/utils/apiClient'
import { mockClient, mockClients } from '@/test/mocks/mockData'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { clientService } from './clientService'

// Mock the apiClient
vi.mock('@/shared/utils/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

describe('clientService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getClients', () => {
    it('should fetch all clients successfully', async () => {
      // Arrange
      const mockResponse = {
        data: {
          items: mockClients,
          total: mockClients.length,
          page: 1,
          pageSize: 10,
        },
      }
      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await clientService.getClients()

      // Assert
      expect(apiClient.get).toHaveBeenCalledWith('/api/clients', { params: undefined })
      expect(result.items).toEqual(mockClients)
      expect(result.total).toBe(mockClients.length)
    })

    it('should fetch clients with pagination params', async () => {
      // Arrange
      const params = { page: 2, pageSize: 20, search: 'John' }
      const mockResponse = {
        data: {
          items: [mockClient],
          total: 1,
          page: 2,
          pageSize: 20,
        },
      }
      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await clientService.getClients(params)

      // Assert
      expect(apiClient.get).toHaveBeenCalledWith('/api/clients', { params })
      expect(result.items).toHaveLength(1)
    })

    it('should throw error when fetch fails', async () => {
      // Arrange
      const errorMessage = 'Network error'
      vi.mocked(apiClient.get).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(clientService.getClients()).rejects.toThrow(errorMessage)
    })
  })

  describe('getClient', () => {
    it('should fetch a single client by ID', async () => {
      // Arrange
      const mockResponse = { data: mockClient }
      vi.mocked(apiClient.get).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await clientService.getClient(mockClient.id)

      // Assert
      expect(apiClient.get).toHaveBeenCalledWith(`/api/clients/${mockClient.id}`)
      expect(result).toEqual(mockClient)
    })

    it('should throw error when client not found', async () => {
      // Arrange
      const clientId = 'non-existent-id'
      const errorMessage = 'Client not found'
      vi.mocked(apiClient.get).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(clientService.getClient(clientId)).rejects.toThrow(errorMessage)
    })
  })

  describe('createClient', () => {
    it('should create a new client successfully', async () => {
      // Arrange
      const newClientData = {
        name: 'New Client',
        birthDate: '1995-03-10',
        birthTime: '10:30',
        birthPlace: 'Paris, France',
        timezone: 'Europe/Paris',
        latitude: 48.8566,
        longitude: 2.3522,
        notes: 'New client notes',
      }
      const mockResponse = {
        data: {
          ...mockClient,
          ...newClientData,
          id: 'new-client-id',
        },
      }
      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await clientService.createClient(newClientData)

      // Assert
      expect(apiClient.post).toHaveBeenCalledWith('/api/clients', newClientData)
      expect(result.name).toBe(newClientData.name)
      expect(result.birthPlace).toBe(newClientData.birthPlace)
    })

    it('should throw error when creation fails', async () => {
      // Arrange
      const newClientData = {
        name: 'Test Client',
        birthDate: '1990-01-01',
        birthTime: '12:00',
        birthPlace: 'Test City',
        timezone: 'UTC',
        latitude: 0,
        longitude: 0,
      }
      const errorMessage = 'Invalid client data'
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(clientService.createClient(newClientData)).rejects.toThrow(errorMessage)
    })
  })

  describe('updateClient', () => {
    it('should update a client successfully', async () => {
      // Arrange
      const updateData = {
        name: 'Updated Name',
        notes: 'Updated notes',
      }
      const mockResponse = {
        data: {
          ...mockClient,
          ...updateData,
        },
      }
      vi.mocked(apiClient.put).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await clientService.updateClient(mockClient.id, updateData)

      // Assert
      expect(apiClient.put).toHaveBeenCalledWith(`/api/clients/${mockClient.id}`, updateData)
      expect(result.name).toBe(updateData.name)
      expect(result.notes).toBe(updateData.notes)
    })

    it('should throw error when update fails', async () => {
      // Arrange
      const updateData = { name: 'Updated Name' }
      const errorMessage = 'Update failed'
      vi.mocked(apiClient.put).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(clientService.updateClient(mockClient.id, updateData)).rejects.toThrow(
        errorMessage
      )
    })
  })

  describe('deleteClient', () => {
    it('should delete a client successfully', async () => {
      // Arrange
      vi.mocked(apiClient.delete).mockResolvedValueOnce({ data: {} })

      // Act
      await clientService.deleteClient(mockClient.id)

      // Assert
      expect(apiClient.delete).toHaveBeenCalledWith(`/api/clients/${mockClient.id}`)
    })

    it('should throw error when deletion fails', async () => {
      // Arrange
      const errorMessage = 'Delete failed'
      vi.mocked(apiClient.delete).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(clientService.deleteClient(mockClient.id)).rejects.toThrow(errorMessage)
    })
  })
})
