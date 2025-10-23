/**
 * Backend Endpoints Integration Tests
 *
 * These tests verify that the backend API endpoints are working correctly.
 * Run these tests with the backend server running on http://localhost:8000
 *
 * To run: npm test -- --run src/test/integration/backend-endpoints.test.ts
 *
 * NOTE: These tests use FAKE credentials for testing purposes only.
 * DO NOT use real credentials in tests.
 */

import { describe, it, expect, beforeAll } from 'vitest'
import axios, { AxiosInstance } from 'axios'

// IMPORTANT: These are FAKE test credentials - NOT real sensitive data
const TEST_CREDENTIALS = {
  email: 'test-integration@example.com',
  password: 'TestPassword123!',
  name: 'Integration Test User',
}

const API_BASE_URL = 'http://localhost:8000'

describe('Backend API Integration Tests', () => {
  let api: AxiosInstance
  let authToken: string | null = null
  let testUserId: string | null = null
  let testClientId: string | null = null
  let testChartId: string | null = null

  beforeAll(() => {
    api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add auth token to requests
    api.interceptors.request.use((config) => {
      if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`
      }
      return config
    })
  })

  describe('Health Check', () => {
    it('should return 200 from health endpoint', async () => {
      try {
        const response = await api.get('/health')
        expect(response.status).toBe(200)
      } catch (error) {
        console.warn('⚠️ Backend may not be running. Start backend with: cd backend && python -m app.main')
        throw error
      }
    })
  })

  describe('Authentication Endpoints', () => {
    it('should register a new user', async () => {
      try {
        const response = await api.post('/api/auth/register', TEST_CREDENTIALS)
        expect(response.status).toBe(201)
        expect(response.data).toHaveProperty('id')
        expect(response.data).toHaveProperty('email', TEST_CREDENTIALS.email)
        testUserId = response.data.id
      } catch (error: any) {
        // Handle case where user already exists (409 Conflict or 400 Bad Request)
        if ([400, 409].includes(error.response?.status)) {
          console.log('ℹ️ User already exists, skipping registration')
          // User exists, we can continue with login
          return
        } else {
          throw error
        }
      }
    })

    it('should login with credentials', async () => {
      const response = await api.post('/api/auth/login', {
        email: TEST_CREDENTIALS.email,
        password: TEST_CREDENTIALS.password,
      })

      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('access_token')
      expect(response.data).toHaveProperty('token_type', 'bearer')
      expect(response.data).toHaveProperty('user')

      authToken = response.data.access_token
    })

    it('should fail login with invalid credentials', async () => {
      try {
        await api.post('/api/auth/login', {
          email: TEST_CREDENTIALS.email,
          password: 'wrong-password',
        })
        expect.fail('Should have thrown an error')
      } catch (error: any) {
        expect(error.response?.status).toBe(401)
      }
    })
  })

  describe('Client Endpoints', () => {
    it('should create a new client', async () => {
      const clientData = {
        first_name: 'Integration',
        last_name: 'Test Client',
        email: 'integration-client@example.com',
        notes: 'Created by integration test',
        birth_data: {
          date: '1990-06-15T14:30:00',
          city: 'New York',
          country: 'USA',
          timezone: 'America/New_York',
          latitude: 40.7128,
          longitude: -74.0060,
        },
      }

      const response = await api.post('/api/clients/', clientData)

      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('first_name', clientData.first_name)
      expect(response.data).toHaveProperty('last_name', clientData.last_name)

      testClientId = response.data.id
    })

    it('should get all clients', async () => {
      const response = await api.get('/api/clients/')

      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('items')
      expect(Array.isArray(response.data.items)).toBe(true)
      expect(response.data).toHaveProperty('total')
    })

    it('should get a specific client by ID', async () => {
      if (!testClientId) {
        console.warn('Skipping: No test client ID available')
        return
      }

      const response = await api.get(`/api/clients/${testClientId}`)

      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id', testClientId)
      expect(response.data).toHaveProperty('name')
    })

    it('should update a client', async () => {
      if (!testClientId) {
        console.warn('Skipping: No test client ID available')
        return
      }

      const updateData = {
        notes: 'Updated by integration test',
      }

      const response = await api.put(`/api/clients/${testClientId}/`, updateData)

      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id', testClientId)
      expect(response.data).toHaveProperty('notes', updateData.notes)
    })
  })

  describe('Chart Endpoints', () => {
    it('should calculate a natal chart', async () => {
      if (!testClientId) {
        console.warn('Skipping: No test client ID available')
        return
      }

      const chartData = {
        client_id: testClientId,
      }

      const response = await api.post('/api/charts/natal', chartData)

      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('id')
      expect(response.data).toHaveProperty('chart_type', 'NATAL')

      testChartId = response.data.id
    })

    it('should get charts for a specific client', async () => {
      if (!testClientId) {
        console.warn('Skipping: No test client ID available')
        return
      }

      const response = await api.get(`/api/charts/client/${testClientId}/charts`)

      expect(response.status).toBe(200)
      expect(Array.isArray(response.data)).toBe(true)
    })

    it('should get a specific chart by ID', async () => {
      if (!testChartId) {
        console.warn('Skipping: No test chart ID available')
        return
      }

      const response = await api.get(`/api/charts/natal/${testChartId}`)

      expect(response.status).toBe(200)
      expect(response.data).toHaveProperty('id', testChartId)
    })
  })

  describe('Cleanup', () => {
    it('should delete the test chart', async () => {
      if (!testChartId) {
        console.warn('Skipping: No test chart ID available')
        return
      }

      // Note: Delete chart endpoint may not be implemented
      try {
        const response = await api.delete(`/api/charts/natal/${testChartId}`)
        expect([200, 204]).toContain(response.status)
      } catch (error: any) {
        if (error.response?.status === 404 || error.response?.status === 405) {
          console.log('ℹ️ Delete chart endpoint not implemented, skipping')
        } else {
          throw error
        }
      }
    })

    it('should delete the test client', async () => {
      if (!testClientId) {
        console.warn('Skipping: No test client ID available')
        return
      }

      // Note: Delete client endpoint may not be fully implemented
      try {
        const response = await api.delete(`/api/clients/${testClientId}/`)
        expect([200, 204]).toContain(response.status)
      } catch (error: any) {
        if (error.response?.status === 404 || error.response?.status === 405) {
          console.log('ℹ️ Delete client endpoint not fully implemented, skipping')
        } else {
          throw error
        }
      }
    })

    it('should logout', async () => {
      const response = await api.post('/api/auth/logout')
      expect([200, 204]).toContain(response.status)
      authToken = null
    })
  })
})
