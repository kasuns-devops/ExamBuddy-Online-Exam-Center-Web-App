/**
 * API Service - Axios instance with authentication interceptor
 */
import axios from 'axios';

// Base API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Attach JWT token to requests
api.interceptors.request.use(
  (config) => {
    // Prefer Cognito access token for protected API requests
    let token = localStorage.getItem('cognito_access_token');

    // Fallback to Cognito ID token if access token not available
    if (!token) {
      token = localStorage.getItem('cognito_id_token');
    }
    
    // Fallback to auth_token if Cognito token not available
    if (!token) {
      token = localStorage.getItem('auth_token');
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Handle 401 Unauthorized - token expired or invalid
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        localStorage.removeItem('cognito_access_token');
        localStorage.removeItem('cognito_id_token');
        localStorage.removeItem('cognito_refresh_token');
        window.location.href = '/login';
      }
      
      // Handle 403 Forbidden
      if (error.response.status === 403) {
        console.error('Access forbidden:', error.response.data);
      }
      
      // Extract error message from response
      const errorMessage = error.response.data?.message || 'An error occurred';
      error.message = errorMessage;
    } else if (error.request) {
      // Network error
      error.message = 'Network error - please check your connection';
    }
    
    return Promise.reject(error);
  }
);

export default api;
