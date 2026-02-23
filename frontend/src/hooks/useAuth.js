/**
 * useAuth Hook - Cognito Authentication state management
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import * as cognitoService from '../services/cognito';

export const useAuth = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      idToken: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,
      isLoading: false,
      error: null,
      requiresNewPassword: false,
      pwdChangeSession: null,

      // Cognito login (OAuth 2.0 Hosted UI)
      login: async () => {
        set({ isLoading: true, error: null });
        try {
          // This redirects to Cognito Hosted UI
          cognitoService.loginWithHostedUI();
          // Note: user will be redirected and will return via /auth-callback
          return { success: true };
        } catch (error) {
          set({
            error: error.message || 'Login failed',
            isLoading: false,
          });
          return { success: false, error: error.message };
        }
      },

      // Set ID Token (called from AuthCallback)
      setIdToken: (token) => {
        set({ idToken: token });
      },

      // Set Access Token (called from AuthCallback)
      setAccessToken: (token) => {
        set({ accessToken: token });
      },

      // Set Refresh Token
      setRefreshToken: (token) => {
        set({ refreshToken: token });
      },

      // Logout
      logout: () => {
        cognitoService.logout();
        set({
          user: null,
          idToken: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
          requiresNewPassword: false,
          isInitialized: true,
        });

        // Clear all auth-related localStorage items
        localStorage.removeItem('cognito_id_token');
        localStorage.removeItem('cognito_access_token');
        localStorage.removeItem('cognito_refresh_token');
      },

      // Initialize auth from localStorage on app mount
      initializeAuth: () => {
        try {
          const idToken = cognitoService.getIdToken();
          const accessToken = cognitoService.getAccessToken();
          const refreshToken = localStorage.getItem('cognito_refresh_token');

          if (idToken && accessToken) {
            set({
              idToken,
              accessToken,
              refreshToken,
              isAuthenticated: true,
              isInitialized: true,
            });
          } else {
            set({ isInitialized: true });
          }
        } catch (error) {
          console.error('Error initializing auth:', error);
          set({ isInitialized: true });
        }
      },

      // Check if user is authenticated
      isAuthenticated: () => {
        return cognitoService.isAuthenticated();
      },

      // Get current tokens for API calls
      getIdToken: () => cognitoService.getIdToken(),
      getAccessToken: () => cognitoService.getAccessToken(),

      // Refresh access token
      refreshAccessToken: async () => {
        try {
          const tokens = await cognitoService.refreshAccessToken();
          if (tokens && tokens.accessToken) {
            set({ accessToken: tokens.accessToken });
            return tokens;
          }
        } catch (error) {
          console.error('Token refresh failed:', error);
          // If refresh fails, logout the user
          get().logout();
        }
      },

      // Helper methods
      isAdmin: () => get().user?.role === 'admin',
      isCandidate: () => get().user?.role === 'candidate',
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        idToken: state.idToken,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
