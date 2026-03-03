import React, { useState } from 'react';
import * as cognitoService from '../services/cognito';
import './Login.css';

export const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLoginClick = () => {
    setIsLoading(true);
    try {
      cognitoService.loginWithHostedUI();
    } catch (err) {
      setError(err.message || 'Login failed');
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <span className="login-badge">Secure Login</span>
          <h1>ExamBuddy</h1>
          <p>Online Exam Center Platform</p>
          <p className="login-subtitle">Sign in to continue to your exam dashboard</p>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        <div className="login-content">
          <div className="login-info">
            <p className="login-info-title">Test Credentials</p>
            <div className="credential-row">
              <span className="credential-label">Email</span>
              <span className="credential-value">kasuns@champsoft.com</span>
            </div>
            <div className="credential-row">
              <span className="credential-label">Password</span>
              <span className="credential-value">Nusak@123</span>
            </div>
          </div>

          <button
            onClick={handleLoginClick}
            disabled={isLoading}
            className="login-button"
          >
            {isLoading ? 'Redirecting to Cognito...' : 'Sign In with Cognito'}
          </button>
        </div>

        <div className="login-footer">
          <p className="security-note">
            🔒 Your credentials are secured by AWS Cognito.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
