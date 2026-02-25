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
  const [newQuestionText, setNewQuestionText] = useState('');
  const [newOptions, setNewOptions] = useState(['', '', '', '']);
  const [newCorrectIndex, setNewCorrectIndex] = useState(0);
  const [createStatus, setCreateStatus] = useState('');

  const loadQuestions = async () => {
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

  useEffect(() => {
    loadQuestions();
  }, []);

  const handleCreateQuestion = async (event) => {
    event.preventDefault();
    setCreateStatus('');

    const trimmedText = newQuestionText.trim();
    const cleanedOptions = newOptions.map((option) => option.trim()).filter(Boolean);

    if (!trimmedText || cleanedOptions.length < 2) {
      setCreateStatus('Please provide question text and at least 2 options.');
      return;
    }

    if (newCorrectIndex < 0 || newCorrectIndex >= cleanedOptions.length) {
      setCreateStatus('Correct answer index must match an existing option.');
      return;
    }

    try {
      await api.post('/api/questions', {
        text: trimmedText,
        answer_options: cleanedOptions,
        correct_answer_index: newCorrectIndex,
        project_id: 'default',
      });

      setCreateStatus('Question created successfully.');
      setNewQuestionText('');
      setNewOptions(['', '', '', '']);
      setNewCorrectIndex(0);
      await loadQuestions();
    } catch (error) {
      setCreateStatus(`Create failed: ${error.message}`);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>ExamBuddy Dashboard</h1>
        <div className="header-actions">
          <button onClick={() => navigate('/exam')} className="exam-button">
            Start Exam
          </button>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
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
            <li>✓ Create new question endpoint UI</li>
            <li>⏳ Create exam sessions</li>
            <li>⏳ Start taking exams</li>
          </ul>
        </div>

        <div className="next-steps-card">
          <h2>Create Question</h2>
          <form onSubmit={handleCreateQuestion} className="question-form">
            <label className="question-form-label">
              Question Text
              <textarea
                value={newQuestionText}
                onChange={(e) => setNewQuestionText(e.target.value)}
                rows={3}
                className="question-form-input"
              />
            </label>

            {newOptions.map((option, index) => (
              <label key={index} className="question-form-label">
                Option {index + 1}
                <input
                  type="text"
                  value={option}
                  onChange={(e) => {
                    const updated = [...newOptions];
                    updated[index] = e.target.value;
                    setNewOptions(updated);
                  }}
                  className="question-form-input"
                />
              </label>
            ))}

            <label className="question-form-label">
              Correct Answer Index
              <input
                type="number"
                min={0}
                max={3}
                value={newCorrectIndex}
                onChange={(e) => setNewCorrectIndex(Number(e.target.value || 0))}
                className="question-form-input"
              />
            </label>

            <button type="submit" className="logout-button">Create Question</button>
            {createStatus && <p className="create-status">{createStatus}</p>}
          </form>
        </div>
      </div>

      <div className="dashboard-footer">
        <p>Welcome to ExamBuddy - Your Online Exam Center Platform</p>
      </div>
    </div>
  );
};

export default Dashboard;
