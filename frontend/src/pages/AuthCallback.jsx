import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import * as cognitoService from '../services/cognito';
import './AuthCallback.css';

export const AuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setIdToken, setAccessToken, setRefreshToken } = useAuth();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Processing your login...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the authorization code from URL parameters
        const code = searchParams.get('code');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Check for errors from Cognito
        if (error) {
          setStatus('error');
          setMessage(`Authentication failed: ${errorDescription || error}`);
          return;
        }

        // If no code, show error
        if (!code) {
          setStatus('error');
          setMessage('No authorization code received from Cognito');
          return;
        }

        // Exchange the auth code for tokens
        setMessage('Exchanging authorization code for tokens...');
        const tokens = await cognitoService.exchangeCodeForTokens(code);

        if (tokens && tokens.idToken && tokens.accessToken) {
          // Store tokens in auth state and localStorage
          localStorage.setItem('cognito_id_token', tokens.idToken);
          localStorage.setItem('cognito_access_token', tokens.accessToken);
          if (tokens.refreshToken) {
            localStorage.setItem('cognito_refresh_token', tokens.refreshToken);
          }

          // Update auth store
          setIdToken(tokens.idToken);
          setAccessToken(tokens.accessToken);
          if (tokens.refreshToken) {
            setRefreshToken(tokens.refreshToken);
          }

          setStatus('success');
          setMessage('Login successful! Redirecting...');

          // Redirect to dashboard after a short delay
          setTimeout(() => {
            navigate('/');
          }, 1500);
        } else {
          setStatus('error');
          setMessage('Failed to obtain tokens from Cognito');
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        setStatus('error');
        setMessage(`Error: ${error.message || 'Authentication failed'}`);
      }
    };

    handleCallback();
  }, [searchParams, navigate, setIdToken, setAccessToken, setRefreshToken]);

  return (
    <div className="auth-callback-container">
      <div className="auth-callback-card">
        {status === 'processing' && (
          <>
            <div className="spinner"></div>
            <p className="callback-message">{message}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <div className="success-icon">✓</div>
            <p className="callback-message success">{message}</p>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="error-icon">✕</div>
            <p className="callback-message error">{message}</p>
            <button
              onClick={() => navigate('/login')}
              className="retry-button"
            >
              Back to Login
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;
