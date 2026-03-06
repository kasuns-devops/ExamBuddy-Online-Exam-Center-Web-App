/**
 * Exam Page - Main exam taking interface
 */
import React, { useState, useEffect } from 'react';
import useExamStore from '../stores/examStore';
import useExamTimer from '../hooks/useExamTimer';
import { useAuth } from '../hooks/useAuth';
import Timer from '../components/shared/Timer';
import QuestionCard from '../components/candidate/QuestionCard';
import ProjectSelection from '../components/candidate/ProjectSelection';
import examService from '../services/examService';
import './ExamPage.css';

const ExamPage = () => {
  const questionPaneRef = React.useRef(null);
  const [phase, setPhase] = useState('selection'); // selection, config, exam, review, results
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answerSubmitted, setAnswerSubmitted] = useState(false);
  const [lastSubmission, setLastSubmission] = useState(null);
  
  // Project and config state
  const [mode, setMode] = useState('test');
  const [difficulty, setDifficulty] = useState('easy');
  const [questionCount, setQuestionCount] = useState(5);

  const logout = useAuth((state) => state.logout);
  
  const {
    sessionId,
    projectId,
    selectedProject,
    currentQuestionIndex,
    getCurrentQuestion,
    getProgress,
    setSession,
    setSelectedProjectContext,
    recordAnswer,
    nextQuestion,
    setResults,
    startReviewPhase,
    resetExam,
    finalScore,
    answers,
    totalQuestions,
    isLoading,
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

  const shouldPauseTimer = phase === 'exam' && mode === 'test' && answerSubmitted;
  const { timeRemaining } = useExamTimer(handleTimeUp, shouldPauseTimer);

  useEffect(() => {
    if (phase !== 'exam' || mode !== 'test' || !answerSubmitted) return;

    const scrollTarget = questionPaneRef.current;
    if (!scrollTarget) return;

    scrollTarget.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }, [phase, mode, answerSubmitted, currentQuestionIndex]);

  function handleTimeUp() {
    if (isReviewPhase) {
      handleSubmitExam();
    } else {
      handleTimeoutAdvance();
    }
  }

  const handleTimeoutAdvance = async () => {
    const currentQuestion = getCurrentQuestion();
    const currentType = currentQuestion?.question_type || 'single_choice';
    const requiresConfirm = currentType === 'ordering' || currentType === 'build_list';

    if (requiresConfirm && selectedAnswer === null) {
      await handleMoveToNextQuestion();
      return;
    }

    if (mode === 'test') {
      if (selectedAnswer !== null && !answerSubmitted) {
        const result = await handleSubmitAnswer();
        if (result) {
          setAnswerSubmitted(true);
          setLastSubmission(result);
        }
      }
      await handleMoveToNextQuestion();
      return;
    }

    if (selectedAnswer !== null) {
      await handlePrimaryAction();
      return;
    }

    await handleMoveToNextQuestion();
  };

  const handleProjectSelect = (project) => {
    setSelectedProjectContext(project);
    setPhase('config');
  };

  const handleStartExam = async () => {
    try {
      setLoading(true);
      setError(null);

      const availableQuestions = selectedProject?.questionCount || 1;
      const safeQuestionCount = Math.max(1, Math.min(questionCount, availableQuestions));
      if (safeQuestionCount !== questionCount) {
        setQuestionCount(safeQuestionCount);
      }
      
      console.log('Starting exam with:', { projectId, mode, difficulty, questionCount: safeQuestionCount });
      
      const data = await examService.startExam(projectId, mode, difficulty, safeQuestionCount);
      
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
    if (mode === 'test') {
      setAnswerSubmitted(false);
      setLastSubmission(null);
    }
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
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const handleMoveToNextQuestion = async () => {
    const progress = getProgress();

    if (progress.current >= progress.total) {
      if (mode === 'exam') {
        try {
          setLoading(true);
          const reviewData = await examService.startReview(sessionId);
          startReviewPhase(reviewData);
          setPhase('review');
        } catch (err) {
          setError(err.message || 'Failed to load review phase.');
        } finally {
          setLoading(false);
        }
      } else {
        await handleSubmitExam();
      }
    } else {
      nextQuestion();
      setSelectedAnswer(null);
      setAnswerSubmitted(false);
      setLastSubmission(null);
    }
  };

  const handlePrimaryAction = async () => {
    if (mode === 'test') {
      if (!answerSubmitted) {
        const result = await handleSubmitAnswer();
        if (result) {
          setAnswerSubmitted(true);
          setLastSubmission(result);
        }
        return;
      }

      await handleMoveToNextQuestion();
      return;
    }

    const result = await handleSubmitAnswer();
    if (!result) return;
    await handleMoveToNextQuestion();
  };

  const getPrimaryButtonLabel = (progress) => {
    if (mode === 'test') {
      if (!answerSubmitted) {
        return 'Submit Answer';
      }
      return progress.current >= progress.total ? 'Finish Exam' : 'Next Question';
    }

    return progress.current >= progress.total ? 'Review Answers' : 'Next Question';
  };

  const isPrimaryDisabled = () => {
    const currentQuestion = getCurrentQuestion();
    const currentType = currentQuestion?.question_type || 'single_choice';
    const requiresConfirm = currentType === 'ordering' || currentType === 'build_list';

    if (mode === 'test') {
      if (answerSubmitted) {
        return isLoading;
      }
      if (requiresConfirm) {
        return selectedAnswer === null || isLoading;
      }
      return selectedAnswer === null || isLoading;
    }

    if (requiresConfirm) {
      return selectedAnswer === null || isLoading;
    }

    return selectedAnswer === null || isLoading;
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
    setPhase('selection');
    setSelectedAnswer(null);
    setAnswerSubmitted(false);
    setLastSubmission(null);
  };

  const handleBackToSelection = () => {
    setSelectedProjectContext(null);
    setPhase('selection');
  };

  const handleSignOut = () => {
    logout();
  };

  if (phase === 'selection') {
    return (
      <div className="exam-page">
        <div className="exam-container">
          <div className="selection-actions">
            <button className="signout-button" onClick={handleSignOut}>
              Sign Out
            </button>
          </div>
          <ProjectSelection onSelectProject={handleProjectSelect} />
          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    );
  }

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
                min="1"
                max={Math.max(1, selectedProject?.questionCount || 1)}
                value={questionCount}
                onChange={(e) => {
                  const availableQuestions = Math.max(1, selectedProject?.questionCount || 1);
                  const parsed = parseInt(e.target.value, 10);
                  const nextValue = Number.isNaN(parsed) ? 1 : Math.min(Math.max(parsed, 1), availableQuestions);
                  setQuestionCount(nextValue);
                }}
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
            <div ref={questionPaneRef} className="question-pane">
              <QuestionCard
                question={question}
                selectedAnswer={selectedAnswer}
                onSelectAnswer={handleAnswerSelect}
                questionNumber={progress.current}
                showCorrectAnswer={mode === 'test' && answerSubmitted}
                correctIndex={lastSubmission?.correct_index ?? null}
                correctAnswer={lastSubmission?.correct_answer ?? null}
                disabled={mode === 'test' && answerSubmitted}
              />
            </div>
          )}

          {mode === 'test' && answerSubmitted && lastSubmission && (
            <div className={`answer-feedback ${lastSubmission.is_correct ? 'correct' : 'incorrect'}`}>
              {lastSubmission.is_correct
                ? '✅ Correct answer submitted. Timer is paused so you can study this question.'
                : `❌ Incorrect answer. Correct answer: ${lastSubmission?.correct_answer?.display || 'see highlighted answer above'}. Timer is paused so you can review.`}
            </div>
          )}

          <div className="exam-controls">
            <button 
              className="btn-primary"
              onClick={handlePrimaryAction}
              disabled={isPrimaryDisabled()}
            >
              {getPrimaryButtonLabel(progress)}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </div>
      </div>
    );
  }

  if (phase === 'review') {
    const answeredCount = Object.keys(answers).length;
    const unansweredCount = Math.max(totalQuestions - answeredCount, 0);

    return (
      <div className="exam-page">
        <div className="exam-container">
          <div className="review-card">
            <h1>🧾 Review Answers</h1>
            <p className="review-subtitle">Exam mode keeps feedback hidden until final submission.</p>

            <div className="review-stats">
              <div className="stat">
                <span className="stat-label">Total Questions</span>
                <span className="stat-value">{totalQuestions}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Answered</span>
                <span className="stat-value">{answeredCount}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Unanswered</span>
                <span className="stat-value">{unansweredCount}</span>
              </div>
            </div>

            <div className="exam-controls review-controls">
              <button className="btn-primary" onClick={handleSubmitExam} disabled={isLoading}>
                Submit Exam
              </button>
            </div>

            {error && <div className="error-message">{error}</div>}
          </div>
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
            <div className="results-topbar">
              <button className="signout-button" onClick={handleSignOut}>
                Sign Out
              </button>
            </div>
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

            {Array.isArray(answers) && answers.length > 0 && (
              <div className="results-detail-list">
                <h2>Answer Review</h2>
                {answers.map((item, index) => (
                  <div key={item.question_id || index} className={`results-detail-item ${item.is_correct ? 'correct' : 'incorrect'}`}>
                    <div className="results-detail-header">
                      <span>Q{index + 1}: {item.question_text}</span>
                      <span className="results-detail-status">{item.is_correct ? 'Correct' : 'Incorrect'}</span>
                    </div>
                    <div className="results-detail-row">
                      <strong>Your answer:</strong> {item.selected_display || 'No answer submitted'}
                    </div>
                    <div className="results-detail-row">
                      <strong>Correct answer:</strong> {item?.correct_answer?.display || '-'}
                    </div>
                  </div>
                ))}
              </div>
            )}

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
