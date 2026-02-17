/**
 * Exam Service - API calls for exam operations
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests (will be implemented with authentication)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const examService = {
  /**
   * Start a new exam session
   */
  async startExam(projectId, mode, difficulty, questionCount) {
    try {
      const response = await api.post('/api/exams/start', {
        project_id: projectId,
        mode,
        difficulty: difficulty || null,
        question_count: questionCount
      });
      return response.data;
    } catch (error) {
      console.error('API Error:', error.response?.data);
      const errorMsg = error.response?.data?.message 
        || error.response?.data?.detail 
        || error.message 
        || 'Failed to start exam';
      throw new Error(errorMsg);
    }
  },

  /**
   * Submit an answer for a question
   */
  async submitAnswer(sessionId, questionId, answerIndex) {
    try {
      const response = await api.post(`/api/exams/${sessionId}/answers`, {
        question_id: questionId,
        answer_index: answerIndex
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to submit answer');
    }
  },

  /**
   * Get a specific question by index
   */
  async getQuestion(sessionId, questionIndex) {
    try {
      const response = await api.get(`/api/exams/${sessionId}/questions/${questionIndex}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get question');
    }
  },

  /**
   * Start review phase (Exam mode only)
   */
  async startReview(sessionId) {
    try {
      const response = await api.get(`/api/exams/${sessionId}/review`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to start review');
    }
  },

  /**
   * Submit exam and get final results
   */
  async submitExam(sessionId) {
    try {
      const response = await api.post(`/api/exams/${sessionId}/submit`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to submit exam');
    }
  },

  /**
   * Cancel exam session
   */
  async cancelExam(sessionId) {
    try {
      const response = await api.delete(`/api/exams/${sessionId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to cancel exam');
    }
  }
,

  /**
   * Record question presentation (frontend should call when showing a question)
   */
  async recordPresentation(sessionId, questionId, presentedAt = null) {
    try {
      const payload = { question_id: questionId };
      if (presentedAt) payload.presented_at = presentedAt;
      const response = await api.post(`/api/exams/${sessionId}/present`, payload);
      return response.data;
    } catch (error) {
      console.error('Failed to record presentation', error.response?.data || error.message);
      // Do not throw -- presentation timestamps are best-effort
      return null;
    }
  }
};

export default examService;
