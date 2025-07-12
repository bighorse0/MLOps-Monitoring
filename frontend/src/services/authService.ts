import axios from 'axios';
import { 
  LoginRequest, 
  RegisterRequest, 
  LoginResponse, 
  User,
  PasswordChangeRequest,
  PasswordResetRequest,
  PasswordResetConfirmRequest
} from '../types/user';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  // Login with email and password
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/login/email', credentials);
    return response.data;
  },

  // Register new user
  async register(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  // Get current user information
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  // Refresh access token
  async refreshToken(): Promise<{ access_token: string; token_type: string }> {
    const response = await apiClient.post('/auth/refresh');
    return response.data;
  },

  // Change password
  async changePassword(passwordData: PasswordChangeRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/change-password', passwordData);
    return response.data;
  },

  // Request password reset
  async requestPasswordReset(resetData: PasswordResetRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/reset-password', resetData);
    return response.data;
  },

  // Confirm password reset
  async confirmPasswordReset(confirmData: PasswordResetConfirmRequest): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/reset-password/confirm', confirmData);
    return response.data;
  },

  // Logout (client-side only)
  logout(): void {
    localStorage.removeItem('token');
  },
};

// Export individual functions for easier imports
export const loginUser = authService.login;
export const registerUser = authService.register;
export const getCurrentUser = authService.getCurrentUser;
export const refreshToken = authService.refreshToken;
export const changePassword = authService.changePassword;
export const requestPasswordReset = authService.requestPasswordReset;
export const confirmPasswordReset = authService.confirmPasswordReset;
export const logoutUser = authService.logout; 