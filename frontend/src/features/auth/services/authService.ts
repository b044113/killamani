/**
 * Authentication Service
 *
 * API calls for authentication operations
 */
import { apiClient } from '@/shared/utils/apiClient';
import type {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  User,
} from '@/types';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    role: string;
    preferred_language: string;
  };
}

export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<{ tokens: AuthTokens; user: User }> {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);

    const tokens: AuthTokens = {
      accessToken: response.data.access_token,
      refreshToken: response.data.refresh_token,
      tokenType: response.data.token_type,
      expiresIn: response.data.expires_in,
    };

    const user: User = {
      id: response.data.user.id,
      email: response.data.user.email,
      role: response.data.user.role as any,
      isActive: true,
      preferredLanguage: response.data.user.preferred_language,
      createdAt: new Date().toISOString(),
    };

    // Store tokens
    localStorage.setItem('accessToken', tokens.accessToken);
    localStorage.setItem('refreshToken', tokens.refreshToken);

    return { tokens, user };
  },

  /**
   * Register new user
   */
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/register', data);
    return response.data;
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/api/auth/logout');
    } finally {
      // Clear tokens regardless of API response
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    const response = await apiClient.post<AuthTokens>('/api/auth/refresh', {
      refreshToken,
    });

    // Store new tokens
    localStorage.setItem('accessToken', response.data.accessToken);
    localStorage.setItem('refreshToken', response.data.refreshToken);

    return response.data;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('accessToken');
  },

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('accessToken');
  },
};
