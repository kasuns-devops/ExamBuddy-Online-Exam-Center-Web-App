/**
 * Exam Store - Global state management for exam sessions
 * Using Zustand for lightweight state management
 */
import { create } from 'zustand';

const useExamStore = create((set, get) => ({
  // Session data
  sessionId: null,
  projectId: null,
  mode: null,
  difficulty: null,
  
  // Questions and progress
  questions: [],
  currentQuestionIndex: 0,
  totalQuestions: 0,
  
  // Answers
  answers: {}, // { questionId: { answerIndex, timeSpent, isCorrect, accepted } }
  
  // Timer
  questionStartTime: null,
  timeRemaining: 0,
  
  // Review phase
  isReviewPhase: false,
  reviewTimeRemaining: 0,
  
  // Results
  finalScore: null,
  attemptId: null,
  
  // UI state
  isLoading: false,
  error: null,

  // Actions
  setSession: (sessionData) => {
    console.log('Setting session with data:', sessionData);
    set({
      sessionId: sessionData.session_id,
      mode: sessionData.mode,
      questions: sessionData.questions || [],
      totalQuestions: sessionData.questions?.length || 0,
      currentQuestionIndex: 0,
      answers: {},
      questionStartTime: Date.now(),
      timeRemaining: sessionData.questions?.[0]?.time_limit_seconds || 60,
      isReviewPhase: false,
      finalScore: null,
      error: null
    });
  },

  setCurrentQuestion: (index) => set({
    currentQuestionIndex: index,
    questionStartTime: Date.now(),
    timeRemaining: get().questions[index]?.time_limit_seconds || 60
  }),

  recordAnswer: (questionId, answerData) => set((state) => ({
    answers: {
      ...state.answers,
      [questionId]: answerData
    }
  })),

  nextQuestion: () => set((state) => {
    const nextIndex = state.currentQuestionIndex + 1;
    if (nextIndex < state.questions.length) {
      return {
        currentQuestionIndex: nextIndex,
        questionStartTime: Date.now(),
        timeRemaining: state.questions[nextIndex]?.time_limit_seconds || 60
      };
    }
    return {};
  }),

  previousQuestion: () => set((state) => {
    const prevIndex = state.currentQuestionIndex - 1;
    if (prevIndex >= 0) {
      return {
        currentQuestionIndex: prevIndex,
        questionStartTime: Date.now(),
        timeRemaining: state.questions[prevIndex]?.time_limit_seconds || 60
      };
    }
    return {};
  }),

  updateTimeRemaining: (seconds) => set({ timeRemaining: seconds }),

  startReviewPhase: (reviewData) => set({
    isReviewPhase: true,
    questions: reviewData.questions,
    answers: reviewData.answers,
    reviewTimeRemaining: reviewData.review_time_seconds,
    currentQuestionIndex: 0
  }),

  updateReviewTime: (seconds) => set({ reviewTimeRemaining: seconds }),

  setResults: (results) => set({
    finalScore: results.score,
    attemptId: results.attempt_id,
    answers: results.answers
  }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  resetExam: () => set({
    sessionId: null,
    projectId: null,
    mode: null,
    difficulty: null,
    questions: [],
    currentQuestionIndex: 0,
    totalQuestions: 0,
    answers: {},
    questionStartTime: null,
    timeRemaining: 0,
    isReviewPhase: false,
    reviewTimeRemaining: 0,
    finalScore: null,
    attemptId: null,
    isLoading: false,
    error: null
  }),

  // Computed values
  getCurrentQuestion: () => {
    const state = get();
    return state.questions[state.currentQuestionIndex];
  },

  getAnswer: (questionId) => {
    return get().answers[questionId];
  },

  getProgress: () => {
    const state = get();
    return {
      current: state.currentQuestionIndex + 1,
      total: state.totalQuestions,
      percentage: ((state.currentQuestionIndex + 1) / state.totalQuestions) * 100
    };
  },

  getAnsweredCount: () => {
    return Object.keys(get().answers).length;
  },

  isQuestionAnswered: (questionId) => {
    return questionId in get().answers;
  }
}));

export default useExamStore;
