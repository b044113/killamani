/**
 * TypeScript Type Definitions
 *
 * Shared types used across the application
 */

// ============================================================================
// User & Auth Types
// ============================================================================

export type UserRole = 'ADMIN' | 'CONSULTANT' | 'CLIENT' | 'USER';

export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  role: UserRole;
  isActive: boolean;
  preferredLanguage: string;
  createdAt: string;
  consultantId?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  role?: UserRole;
  preferredLanguage?: string;
}

// ============================================================================
// Client Types
// ============================================================================

export interface BirthData {
  date: string;
  city: string;
  country: string;
  timezone: string;
  latitude?: number;
  longitude?: number;
}

export interface Client {
  id: string;
  consultantId: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email?: string;
  birthDate: string;
  birthCity: string;
  birthCountry: string;
  birthTimezone: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  hasAccount: boolean;
}

export interface CreateClientData {
  firstName: string;
  lastName: string;
  birthData: BirthData;
  email?: string;
  notes?: string;
}

export interface UpdateClientData {
  firstName?: string;
  lastName?: string;
  email?: string;
  notes?: string;
}

// ============================================================================
// Chart Types
// ============================================================================

export interface CelestialPosition {
  name: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
  house: number;
  isRetrograde: boolean;
  dignity?: string;
}

export interface House {
  number: number;
  cuspLongitude: number;
  sign: string;
  degree: number;
}

export interface Aspect {
  planet1: string;
  planet2: string;
  aspectType: string;
  angle: number;
  orb: number;
  isApplying: boolean;
}

export interface SolarSet {
  sunSign: string;
  sunHouse: number;
  sunDegree: number;
  fifthHouseSign: string;
  hardAspects: Array<{
    planet: string;
    aspect: string;
    orb: number;
  }>;
}

export interface NatalChart {
  id: string;
  clientId: string;
  sunSign: string;
  planets: CelestialPosition[];
  houses: House[];
  aspects: Aspect[];
  angles: {
    ascendant?: {
      longitude: number;
      sign: string;
      degree: number;
    };
    midheaven?: {
      longitude: number;
      sign: string;
      degree: number;
    };
  };
  solarSet: SolarSet;
  interpretations: Record<string, string>;
  houseSystem: string;
  svgUrl?: string;
  pdfUrl?: string;
  calculatedAt: string;
  createdAt: string;
}

export interface CalculateNatalChartData {
  clientId: string;
  includeChiron?: boolean;
  includeLilith?: boolean;
  includeNodes?: boolean;
  houseSystem?: string;
  language?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  code: string;
  message: string;
  type?: string;
  field?: string;
  details?: any;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// UI State Types
// ============================================================================

export type LoadingState = 'idle' | 'loading' | 'succeeded' | 'failed';

export interface FormError {
  field: string;
  message: string;
}

// ============================================================================
// Language Types
// ============================================================================

export type SupportedLanguage = 'es' | 'en' | 'it' | 'fr' | 'de' | 'pt-br';

export interface LanguageOption {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
}
