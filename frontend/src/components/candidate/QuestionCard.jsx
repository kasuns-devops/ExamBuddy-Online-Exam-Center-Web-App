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
  const [orderedItems, setOrderedItems] = React.useState([]);
  const [dragIndex, setDragIndex] = React.useState(null);
  const [blankValue, setBlankValue] = React.useState('');
  const [selectedMatches, setSelectedMatches] = React.useState({});
  const [selectedHotspot, setSelectedHotspot] = React.useState('');
  const [selectedMulti, setSelectedMulti] = React.useState([]);

  const type = question.question_type || 'single_choice';
  const metadata = question.metadata || {};

  React.useEffect(() => {
    if (type === 'ordering' || type === 'build_list') {
      setOrderedItems([...(metadata.items || [])]);
    } else {
      setOrderedItems([]);
    }

    setBlankValue('');
    setSelectedMatches({});
    setSelectedHotspot('');
    setSelectedMulti([]);
  }, [question.question_id, type]);

  const markCompleted = () => {
    onSelectAnswer(0);
  };

  const markIncomplete = () => {
    onSelectAnswer(null);
  };
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
    return type.replace(/_/g, ' ').replace(/\b\w/g, (match) => match.toUpperCase());
  };

  const handleDragStart = (index) => {
    setDragIndex(index);
  };

  const handleDrop = (dropIndex) => {
    if (dragIndex === null || dragIndex === dropIndex) return;

    const updated = [...orderedItems];
    const [moved] = updated.splice(dragIndex, 1);
    updated.splice(dropIndex, 0, moved);
    setOrderedItems(updated);
    setDragIndex(null);
  };

  const renderTypeSpecificArea = () => {
    if (type === 'ordering' || type === 'build_list') {
      return (
        <div className="type-box">
          <p className="type-helper">Drag and drop to reorder, then confirm.</p>
          <div className="drag-list">
            {orderedItems.map((item, index) => (
              <div
                key={`${item}-${index}`}
                className="drag-item"
                draggable={!disabled}
                onDragStart={() => handleDragStart(index)}
                onDragOver={(event) => event.preventDefault()}
                onDrop={() => handleDrop(index)}
              >
                <span className="drag-handle">☰</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
          <button
            className="type-action"
            disabled={disabled || orderedItems.length === 0}
            onClick={markCompleted}
          >
            Confirm Order
          </button>
        </div>
      );
    }

    if (type === 'matching') {
      const leftItems = metadata.left_items || [];
      const rightItems = metadata.right_items || [];
      const allSelected = leftItems.length > 0 && leftItems.every((left) => selectedMatches[left]);

      return (
        <div className="type-box">
          <p className="type-helper">Match each item to the correct description.</p>
          {leftItems.map((left) => (
            <div key={left} className="match-row">
              <span className="match-left">{left}</span>
              <select
                className="match-select"
                value={selectedMatches[left] || ''}
                disabled={disabled}
                onChange={(event) => {
                  const next = { ...selectedMatches, [left]: event.target.value };
                  setSelectedMatches(next);
                  if (leftItems.every((item) => next[item])) {
                    markCompleted();
                  } else {
                    markIncomplete();
                  }
                }}
              >
                <option value="">Select match</option>
                {rightItems.map((right) => (
                  <option key={right} value={right}>{right}</option>
                ))}
              </select>
            </div>
          ))}
          <button className="type-action" disabled={disabled || !allSelected} onClick={markCompleted}>
            Confirm Matches
          </button>
        </div>
      );
    }

    if (type === 'hotspot') {
      const hotspots = metadata.hotspots || ['A', 'B', 'C', 'D'];
      return (
        <div className="type-box">
          <p className="type-helper">Click a hotspot area.</p>
          <div className="hotspot-grid">
            {hotspots.map((spot) => (
              <button
                key={spot}
                className={`hotspot-btn ${selectedHotspot === spot ? 'active' : ''}`}
                disabled={disabled}
                onClick={() => {
                  setSelectedHotspot(spot);
                  markCompleted();
                }}
              >
                {spot}
              </button>
            ))}
          </div>
        </div>
      );
    }

    if (type === 'fill_in_blank') {
      return (
        <div className="type-box">
          <p className="type-helper">Enter your answer in the blank field.</p>
          <input
            type="text"
            className="blank-input"
            value={blankValue}
            disabled={disabled}
            placeholder="Type your answer"
            onChange={(event) => {
              const value = event.target.value;
              setBlankValue(value);
              if (value.trim().length > 0) {
                markCompleted();
              } else {
                markIncomplete();
              }
            }}
          />
        </div>
      );
    }

    if (type === 'multiple_response') {
      const choices = metadata.choices || question.answer_options || [];
      return (
        <div className="type-box">
          <p className="type-helper">Select one or more options.</p>
          <div className="multi-list">
            {choices.map((choice, index) => {
              const checked = selectedMulti.includes(index);
              return (
                <label key={index} className="multi-item">
                  <input
                    type="checkbox"
                    checked={checked}
                    disabled={disabled}
                    onChange={() => {
                      const updated = checked
                        ? selectedMulti.filter((item) => item !== index)
                        : [...selectedMulti, index];
                      setSelectedMulti(updated);
                      if (updated.length > 0) {
                        markCompleted();
                      } else {
                        markIncomplete();
                      }
                    }}
                  />
                  <span>{choice}</span>
                </label>
              );
            })}
          </div>
        </div>
      );
    }

    if (type === 'true_false') {
      const options = metadata.options || ['True', 'False'];
      return (
        <div className="type-box">
          <p className="type-helper">Choose True or False.</p>
          <div className="tf-row">
            {options.map((option, index) => (
              <button
                key={option}
                className={`tf-btn ${selectedAnswer === index ? 'active' : ''}`}
                disabled={disabled}
                onClick={() => onSelectAnswer(index)}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      );
    }

    return null;
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

      {renderTypeSpecificArea()}
      
      {(type === 'single_choice' || type === 'scenario') && (
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
      )}
    </div>
  );
};

export default QuestionCard;
