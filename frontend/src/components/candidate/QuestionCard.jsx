/**
 * Question Card Component - Display question and answer options
 */
import React from 'react';
import './QuestionCard.css';

const QuestionCard = ({
  question,
  selectedAnswer,
  onSelectAnswer,
  showCorrectAnswer = false,
  correctIndex = null,
  disabled = false,
  questionNumber
}) => {
  const getOptionClassName = (index) => {
    const classes = ['option'];
    
    if (selectedAnswer === index) {
      classes.push('selected');
    }
    
    if (showCorrectAnswer) {
      if (index === correctIndex) {
        classes.push('correct');
      } else if (selectedAnswer === index && index !== correctIndex) {
        classes.push('incorrect');
      }
    }
    
    if (disabled) {
      classes.push('disabled');
    }
    
    return classes.join(' ');
  };

  const getTypeLabel = () => {
    const type = question.question_type || 'single_choice';
    return type.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
  };

  return (
    <div className="question-card">
      <div className="question-header">
        <span className="question-number">Question {questionNumber}</span>
        <div className="question-meta">
          {question.question_type && (
            <span className="question-type">{getTypeLabel()}</span>
          )}
          {question.difficulty && (
            <span className={`difficulty difficulty-${question.difficulty}`}>
              {question.difficulty}
            </span>
          )}
        </div>
      </div>
      
      <div className="question-text">
        {question.text}
      </div>

      <p className="question-hint">
        Select the best answer option below for this question type.
      </p>
      
      <div className="answer-options">
        {question.answer_options.map((option, index) => (
          <button
            key={index}
            className={getOptionClassName(index)}
            onClick={() => !disabled && onSelectAnswer(index)}
            disabled={disabled}
          >
            <span className="option-letter">
              {String.fromCharCode(65 + index)}
            </span>
            <span className="option-text">{option}</span>
            {showCorrectAnswer && index === correctIndex && (
              <span className="check-icon">✓</span>
            )}
            {showCorrectAnswer && selectedAnswer === index && index !== correctIndex && (
              <span className="cross-icon">✗</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuestionCard;
