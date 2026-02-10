/**
 * useAuth Hook - Authentication state management
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

export const useAuth = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/login', { email, password });
          const { token, user } = response.data;

          // Store token in localStorage for API interceptor
          localStorage.setItem('auth_token', token);
          localStorage.setItem('user_info', JSON.stringify(user));

          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true };
        } catch (error) {
          set({
            error: error.message || 'Login failed',
            isLoading: false,
          });
          return { success: false, error: error.message };
        }
      },

      register: async (email, password, fullName, role = 'candidate') => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
            role,
          });
          const { token, user } = response.data;

          localStorage.setItem('auth_token', token);
          localStorage.setItem('user_info', JSON.stringify(user));

          set({
            token,
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          return { success: true };
        } catch (error) {
          set({
            error: error.message || 'Registration failed',
            isLoading: false,
          });
          return { success: false, error: error.message };
        }
      },

      logout: () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      refreshToken: async () => {
        try {
          const response = await api.post('/auth/refresh');
          const { token } = response.data;

          localStorage.setItem('auth_token', token);
          set({ token });

          return { success: true };
        } catch (error) {
          get().logout();
          return { success: false };
        }
      },

      // Initialize from localStorage on app start
      initialize: () => {
        const token = localStorage.getItem('auth_token');
        const userInfo = localStorage.getItem('user_info');

        if (token && userInfo) {
          try {
            const user = JSON.parse(userInfo);
            set({
              token,
              user,
              isAuthenticated: true,
            });
          } catch (error) {
            console.error('Error parsing user info:', error);
            get().logout();
          }
        }
      },

      // Helper getters
      isAdmin: () => get().user?.role === 'admin',
      isCandidate: () => get().user?.role === 'candidate',
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
