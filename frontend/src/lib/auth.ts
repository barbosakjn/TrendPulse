import api from './api';
import { useAuthStore } from '@/stores/authStore';
import type { LoginCredentials, RegisterData, TokenResponse, User } from '@/types/auth';

/**
 * Login user with credentials
 */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  try {
    const response = await api.post<TokenResponse>('/api/auth/login', credentials);
    const { access_token, refresh_token, user } = response.data;

    // Update store
    const { setUser, setTokens } = useAuthStore.getState();
    setUser(user);
    setTokens(access_token, refresh_token);

    // Save user to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }

    return response.data;
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Login failed. Please try again.';
    throw new Error(message);
  }
}

/**
 * Register new user
 */
export async function register(data: RegisterData): Promise<{ user: User; message: string }> {
  try {
    const response = await api.post('/api/auth/register', data);
    return response.data;
  } catch (error: any) {
    // Ignore backend error messages, use generic
    throw new Error("Registration failed. Please check your details and try again.");
  }
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    // Call backend logout endpoint
    await api.post('/api/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear store regardless of API call result
    const { logout: clearAuth } = useAuthStore.getState();
    clearAuth();
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to get user profile.';
    throw new Error(message);
  }
}

/**
 * Request password reset
 */
export async function requestPasswordReset(email: string): Promise<{ message: string }> {
  try {
    const response = await api.post('/api/auth/forgot-password', { email });
    return response.data;
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to request password reset.';
    throw new Error(message);
  }
}

/**
 * Reset password with token
 */
export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  try {
    const response = await api.post('/api/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to reset password.';
    throw new Error(message);
  }
}

/**
 * Verify email with token
 */
export async function verifyEmail(token: string): Promise<{ message: string }> {
  try {
    const response = await api.get(`/api/auth/verify-email?token=${token}`);
    return response.data;
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to verify email.';
    throw new Error(message);
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  
  const token = localStorage.getItem('access_token');
  return !!token;
}

/**
 * Initialize auth state from localStorage
 */
export function initializeAuth(): void {
  if (typeof window === 'undefined') return;

  const token = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  const userStr = localStorage.getItem('user');

  if (token && refreshToken && userStr) {
    try {
      const user = JSON.parse(userStr);
      const { setUser, setTokens } = useAuthStore.getState();
      setUser(user);
      setTokens(token, refreshToken);
    } catch (error) {
      console.error('Failed to initialize auth:', error);
      // Clear invalid data
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }
}
