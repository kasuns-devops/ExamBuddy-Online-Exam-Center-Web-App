/**
 * Exam Page - Main exam taking interface
 */
import React, { useState, useEffect } from 'react';
import useExamStore from '../stores/examStore';
import useExamTimer from '../hooks/useExamTimer';
import Timer from '../components/shared/Timer';
import QuestionCard from '../components/candidate/QuestionCard';
import ProjectSelection from '../components/candidate/ProjectSelection';
import examService from '../services/examService';
import './ExamPage.css';

const ExamPage = () => {
  const [phase, setPhase] = useState('selection'); // selection, config, exam, review, results
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  
  // Project and config state
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectId, setProjectId] = useState('');
  const [mode, setMode] = useState('test');
  const [difficulty, setDifficulty] = useState('easy');
  const [questionCount, setQuestionCount] = useState(5);
  
  const {
    sessionId,
    currentQuestionIndex,
    getCurrentQuestion,
    getProgress,
    setSession,
    recordAnswer,
    nextQuestion,
    setResults,
    resetExam,
    finalScore,
    answers,
    setLoading,
    setError,
    error,
    isReviewPhase
  } = useExamStore();

  // Record presentation when a new question is shown (frontend calls backend endpoint)
  useEffect(() => {
    if (phase !== 'exam') return;
    const question = getCurrentQuestion();
    if (!question || !sessionId) return;

    const presentedAt = new Date().toISOString().replace('Z', '+00:00');
    examService.recordPresentation(sessionId, question.question_id, presentedAt)
      .catch((err) => console.error('recordPresentation error:', err));
  }, [phase, sessionId, currentQuestionIndex]);

  const { timeRemaining } = useExamTimer(handleTimeUp);

  function handleTimeUp() {
    if (isReviewPhase) {
      handleSubmitExam();
    } else {
      // Auto-advance to next question
      handleNext();
    }
  }

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    setProjectId(project.id);
    setPhase('config');
  };

  const handleStartExam = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Starting exam with:', { projectId, mode, difficulty, questionCount });
      
      const data = await examService.startExam(projectId, mode, difficulty, questionCount);
      
      console.log('Exam started:', data);
      
      setSession(data);
      setPhase('exam');
    } catch (err) {
      console.error('Failed to start exam:', err);
      setError(err.message || 'Failed to start exam. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answerIndex) => {
    setSelectedAnswer(answerIndex);
  };

  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null) return;
    
    const question = getCurrentQuestion();
    if (!question) return;

    try {
      setLoading(true);
      const result = await examService.submitAnswer(
        sessionId,
        question.question_id,
        selectedAnswer
      );
      
      recordAnswer(question.question_id, {
        answerIndex: selectedAnswer,
        ...result
      });
      
      setSelectedAnswer(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    await handleSubmitAnswer();
    const progress = getProgress();
    
    if (progress.current >= progress.total) {
      // All questions answered
      if (mode === 'exam') {
        setPhase('review');
        // TODO: Start review phase
      } else {
        // Test mode - go straight to results
        await handleSubmitExam();
      }
    } else {
      nextQuestion();
      setSelectedAnswer(null);
    }
  };

  const handleSubmitExam = async () => {
    try {
      setLoading(true);
      const results = await examService.submitExam(sessionId);
      setResults(results);
      setPhase('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewExam = () => {
    resetExam();
    setSelectedProject(null);
    setProjectId('');
    setPhase('selection');
    setSelectedAnswer(null);
  };

  const handleBackToSelection = () => {
    setSelectedProject(null);
    setProjectId('');
    setPhase('selection');
  };

  if (phase === 'config') {
    return (
      <div className="exam-page">
        <div className="config-container">
          <button className="back-button" onClick={handleBackToSelection}>
            ← Back to Exam Selection
          </button>

          <h1>📝 Configure Exam</h1>
          {selectedProject && (
            <p className="selected-exam">Selected: {selectedProject.name}</p>
          )}

          <div className="config-form">
            <div className="form-group">
              <label>Exam Mode</label>
              <select value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="test">Test Mode (immediate feedback)</option>
                <option value="exam">Exam Mode (with review phase)</option>
              </select>
              <small className="help-text">
                {mode === 'test'
                  ? 'See correct answers immediately after each question'
                  : 'Review all answers at the end before final submission'}
              </small>
            </div>

            <div className="form-group">
              <label>Difficulty Filter</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="">All Difficulties</option>
                <option value="easy">Easy Only</option>
                <option value="medium">Medium Only</option>
                <option value="hard">Hard Only</option>
              </select>
            </div>

            <div className="form-group">
              <label>Number of Questions</label>
              <input
                type="number"
                min="5"
                max="50"
                value={questionCount}
                onChange={(e) => setQuestionCount(parseInt(e.target.value) || 5)}
              />
              <small className="help-text">
                Available: {selectedProject?.questionCount || 0} questions
              </small>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button className="btn-primary" onClick={handleStartExam} disabled={!projectId}>
              Start Exam
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Exam phase
  if (phase === 'exam') {
    const question = getCurrentQuestion();
    const progress = getProgress();

    return (
      <div className="exam-page">
        <div className="exam-header">
          <Timer seconds={timeRemaining} />
          <div className="progress">
            Question {progress.current} of {progress.total}
          </div>
        </div>

        <div className="exam-container">
          {question && (
            <QuestionCard
              question={question}
              selectedAnswer={selectedAnswer}
              onSelectAnswer={handleAnswerSelect}
              questionNumber={progress.current}
            />
          )}

          <div className="exam-controls">
            <button 
              className="btn-primary"
              onClick={handleNext}
              disabled={selectedAnswer === null}
            >
              {progress.current >= progress.total ? 'Finish' : 'Next'}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    );
  }

  // Results phase
  if (phase === 'results') {
    return (
      <div className="exam-page">
        <div className="exam-container">
          <div className="results-card">
            <h1>🎉 Exam Complete!</h1>
            
            <div className="score-display">
              <div className="score-number">{finalScore?.toFixed(1)}%</div>
              <div className="score-label">Final Score</div>
            </div>

            <div className="results-summary">
              <div className="stat">
                <span className="stat-label">Answered:</span>
                <span className="stat-value">{Object.keys(answers).length}</span>
              </div>
            </div>

            <button className="btn-primary" onClick={handleNewExam}>
              Take Another Exam
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ExamPage;
