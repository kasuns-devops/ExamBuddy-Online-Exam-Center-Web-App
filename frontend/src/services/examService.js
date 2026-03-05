/**
 * Exam Service - API calls for exam operations
 */
import axios from 'axios';
import { API_ROUTES } from './api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests (will be implemented with authentication)
api.interceptors.request.use((config) => {
  if (config.headers?.Authorization) {
    return config;
  }

  let token = localStorage.getItem('cognito_access_token');
  if (!token) {
    token = localStorage.getItem('cognito_id_token');
  }
  if (!token) {
    token = localStorage.getItem('authToken');
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const requestWithAuthRetry = async (requestConfig) => {
  try {
    const response = await api.request(requestConfig);
    return response;
  } catch (error) {
    if (error.response?.status !== 401) {
      throw error;
    }

    const idToken = localStorage.getItem('cognito_id_token');
    if (!idToken) {
      throw error;
    }

    const retryResponse = await api.request({
      ...requestConfig,
      headers: {
        ...(requestConfig.headers || {}),
        Authorization: `Bearer ${idToken}`,
      },
    });
    return retryResponse;
  }
};

const examService = {
  /**
   * Start a new exam session
   */
  async startExam(projectId, mode, difficulty, questionCount) {
    try {
      const response = await requestWithAuthRetry({
        method: 'POST',
        url: '/api/exams/start',
        data: {
        project_id: projectId,
        mode,
        difficulty: difficulty || null,
        question_count: questionCount
        }
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
  async submitAnswer(sessionId, questionId, answerPayload) {
    try {
      const payload = {
        question_id: questionId,
      };

      if (typeof answerPayload === 'number') {
        payload.answer_index = answerPayload;
      } else if (answerPayload && typeof answerPayload === 'object') {
        Object.assign(payload, answerPayload);
      }

      const response = await requestWithAuthRetry({
        method: 'POST',
        url: `/api/exams/${sessionId}/answers`,
        data: {
          ...payload
        }
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
      const response = await requestWithAuthRetry({
        method: 'GET',
        url: `/api/exams/${sessionId}/review`
      });
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
      const response = await requestWithAuthRetry({
        method: 'POST',
        url: `/api/exams/${sessionId}/submit`
      });
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
  },

  async createProject(payload) {
    try {
      const response = await requestWithAuthRetry({
        method: 'POST',
        url: API_ROUTES.ADMIN_PROJECTS,
        data: payload,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create project');
    }
  },

  async uploadProjectPdf(projectId, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await requestWithAuthRetry({
        method: 'POST',
        url: API_ROUTES.ADMIN_PROJECT_DOCUMENTS(projectId),
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to upload project PDF');
    }
  },

  async getProjectIngestionStatus(projectId) {
    try {
      const response = await requestWithAuthRetry({
        method: 'GET',
        url: API_ROUTES.ADMIN_PROJECT_INGESTION(projectId),
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to load ingestion status');
    }
  }
};

export default examService;
