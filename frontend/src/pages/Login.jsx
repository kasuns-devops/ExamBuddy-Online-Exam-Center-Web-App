import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as cognitoService from '../services/cognito';
import './Login.css';

export const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

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
          <h1>ExamBuddy</h1>
          <p>Online Exam Center Platform</p>
        </div>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        <div className="login-content">
          <p className="login-description">
            Sign in with your Cognito credentials to access ExamBuddy
          </p>

          <button
            onClick={handleLoginClick}
            disabled={isLoading}
            className="login-button"
          >
            {isLoading ? 'Redirecting to Cognito...' : 'Sign In with Cognito'}
          </button>

          <div className="login-info">
            <p>
              <strong>Test Credentials:</strong>
            </p>
            <p>Email: kasuns@champsoft.com</p>
            <p>Password: Nusak@123</p>
          </div>
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
