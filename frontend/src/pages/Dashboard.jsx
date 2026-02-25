import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';
import './Dashboard.css';

export const Dashboard = () => {
  const navigate = useNavigate();
  const { logout, getIdToken } = useAuth();
  const [apiStatus, setApiStatus] = useState('checking');
  const [apiMessage, setApiMessage] = useState('Loading questions...');
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    const checkAPI = async () => {
      try {
        console.log('Attempting API call to:', api.defaults.baseURL);
        const response = await api.get('/api/questions');
        console.log('API response:', response.data);
        setApiStatus('success');
        setApiMessage(`Questions loaded: ${response.data.count}`);
        setQuestions(response.data.items || []);
      } catch (error) {
        console.error('API Error Details:', {
          message: error.message,
          code: error.code,
          url: error.config?.url,
          status: error.response?.status,
          data: error.response?.data,
        });
        setApiStatus('error');
        setApiMessage(`API Error: ${error.message}`);
      }
    };

    checkAPI();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ExamBuddy Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        <div className="status-card">
          <h2>Authentication Status</h2>
          <div className="status-item">
            <span className="status-label">Token:</span>
            <span className="status-value success">✓ Valid Cognito Token</span>
          </div>
          <div className="status-item">
            <span className="status-label">Token (first 20 chars):</span>
            <span className="status-value mono">{getIdToken()?.substring(0, 20)}...</span>
          </div>
        </div>

        <div className={`api-card ${apiStatus}`}>
          <h2>API Connection Status</h2>
          <div className={`api-status-indicator ${apiStatus}`}>
            {apiStatus === 'checking' && '⟳'}
            {apiStatus === 'success' && '✓'}
            {apiStatus === 'error' && '✕'}
          </div>
          <p className={`api-message ${apiStatus}`}>{apiMessage}</p>
          {questions.length > 0 && (
            <div className="api-response">
              <p><strong>Available Questions:</strong></p>
              <ul>
                {questions.map((question) => (
                  <li key={question.question_id}>{question.text}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="next-steps-card">
          <h2>Next Steps</h2>
          <ul>
            <li>✓ Authentication setup complete</li>
            <li>✓ Questions API connected</li>
            <li>⏳ Create new question endpoint UI</li>
            <li>⏳ Create exam sessions</li>
            <li>⏳ Start taking exams</li>
          </ul>
        </div>
      </div>

      <div className="dashboard-footer">
        <p>Welcome to ExamBuddy - Your Online Exam Center Platform</p>
      </div>
    </div>
  );
};

export default Dashboard;
