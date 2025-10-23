import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { authService } from './authService'
import { apiClient } from '@/shared/utils/apiClient'
import { mockUser, mockTokens, mockLoginCredentials } from '@/test/mocks/mockData'

// Mock the apiClient
vi.mock('@/shared/utils/apiClient', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

describe('authService', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('login', () => {
    it('should login successfully and store tokens', async () => {
      // Arrange
      const mockResponse = {
        data: {
          access_token: mockTokens.access,
          refresh_token: mockTokens.refresh,
          token_type: 'Bearer',
          expires_in: 3600,
          user: {
            id: mockUser.id,
            email: mockUser.email,
            role: mockUser.role,
            preferred_language: 'en',
          },
        },
      }

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await authService.login(mockLoginCredentials)

      // Assert
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/login', mockLoginCredentials)
      expect(result.tokens.accessToken).toBe(mockTokens.access)
      expect(result.tokens.refreshToken).toBe(mockTokens.refresh)
      expect(result.user.email).toBe(mockUser.email)
      expect(localStorage.getItem('accessToken')).toBe(mockTokens.access)
      expect(localStorage.getItem('refreshToken')).toBe(mockTokens.refresh)
    })

    it('should throw error on login failure', async () => {
      // Arrange
      const errorMessage = 'Invalid credentials'
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(authService.login(mockLoginCredentials)).rejects.toThrow(errorMessage)
      expect(localStorage.getItem('accessToken')).toBeNull()
    })
  })

  describe('register', () => {
    it('should register a new user successfully', async () => {
      // Arrange
      const registerData = {
        email: 'newuser@example.com',
        password: 'NewPass123!',
        name: 'New User',
      }
      const mockResponse = {
        data: {
          ...mockUser,
          email: registerData.email,
          name: registerData.name,
        },
      }

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await authService.register(registerData)

      // Assert
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/register', registerData)
      expect(result.email).toBe(registerData.email)
    })

    it('should throw error on registration failure', async () => {
      // Arrange
      const registerData = {
        email: 'test@example.com',
        password: 'Test123!',
        name: 'Test User',
      }
      const errorMessage = 'Email already exists'
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(authService.register(registerData)).rejects.toThrow(errorMessage)
    })
  })

  describe('logout', () => {
    it('should logout successfully and clear tokens', async () => {
      // Arrange
      localStorage.setItem('accessToken', mockTokens.access)
      localStorage.setItem('refreshToken', mockTokens.refresh)
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: {} })

      // Act
      await authService.logout()

      // Assert
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/logout')
      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBeNull()
    })

    it('should clear tokens even if API call fails', async () => {
      // Arrange
      localStorage.setItem('accessToken', mockTokens.access)
      localStorage.setItem('refreshToken', mockTokens.refresh)
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'))

      // Act & Assert - logout throws error but still clears tokens (finally block)
      await expect(authService.logout()).rejects.toThrow('Network error')

      // Tokens should still be cleared due to finally block
      expect(localStorage.getItem('accessToken')).toBeNull()
      expect(localStorage.getItem('refreshToken')).toBeNull()
    })
  })

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      // Arrange
      const newAccessToken = 'new-mock-access-token'
      const newRefreshToken = 'new-mock-refresh-token'
      const mockResponse = {
        data: {
          accessToken: newAccessToken,
          refreshToken: newRefreshToken,
          tokenType: 'Bearer',
          expiresIn: 3600,
        },
      }

      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse)

      // Act
      const result = await authService.refreshToken(mockTokens.refresh)

      // Assert
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/refresh', {
        refreshToken: mockTokens.refresh,
      })
      expect(result.accessToken).toBe(newAccessToken)
      expect(localStorage.getItem('accessToken')).toBe(newAccessToken)
      expect(localStorage.getItem('refreshToken')).toBe(newRefreshToken)
    })

    it('should throw error when refresh fails', async () => {
      // Arrange
      const errorMessage = 'Invalid refresh token'
      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error(errorMessage))

      // Act & Assert
      await expect(authService.refreshToken(mockTokens.refresh)).rejects.toThrow(errorMessage)
    })
  })

  describe('isAuthenticated', () => {
    it('should return true when access token exists', () => {
      // Arrange
      localStorage.setItem('accessToken', mockTokens.access)

      // Act
      const result = authService.isAuthenticated()

      // Assert
      expect(result).toBe(true)
    })

    it('should return false when access token does not exist', () => {
      // Act
      const result = authService.isAuthenticated()

      // Assert
      expect(result).toBe(false)
    })
  })

  describe('getAccessToken', () => {
    it('should return access token when it exists', () => {
      // Arrange
      localStorage.setItem('accessToken', mockTokens.access)

      // Act
      const result = authService.getAccessToken()

      // Assert
      expect(result).toBe(mockTokens.access)
    })

    it('should return null when access token does not exist', () => {
      // Act
      const result = authService.getAccessToken()

      // Assert
      expect(result).toBeNull()
    })
  })
})
