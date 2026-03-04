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
  correctAnswer = null,
  disabled = false,
  questionNumber
}) => {
  const [orderedItems, setOrderedItems] = React.useState([]);
  const [dragIndex, setDragIndex] = React.useState(null);
  const [touchDragIndex, setTouchDragIndex] = React.useState(null);
  const [touchDropIndex, setTouchDropIndex] = React.useState(null);
  const [activePointerId, setActivePointerId] = React.useState(null);
  const [activeTouchId, setActiveTouchId] = React.useState(null);
  const [orderConfirmed, setOrderConfirmed] = React.useState(false);
  const [blankValue, setBlankValue] = React.useState('');
  const [selectedMatches, setSelectedMatches] = React.useState({});
  const [matchesConfirmed, setMatchesConfirmed] = React.useState(false);
  const [selectedHotspot, setSelectedHotspot] = React.useState('');
  const [selectedMulti, setSelectedMulti] = React.useState([]);

  const type = question.question_type || 'single_choice';
  const metadata = question.metadata || {};
  const answerOptions = Array.isArray(question.answer_options) ? question.answer_options : [];
  const selectedIndex = typeof selectedAnswer === 'number'
    ? selectedAnswer
    : (selectedAnswer && typeof selectedAnswer === 'object' && typeof selectedAnswer.answer_index === 'number'
      ? selectedAnswer.answer_index
      : null);
  const selectedHotspotValue = selectedAnswer && typeof selectedAnswer === 'object'
    ? selectedAnswer.selected_hotspot
    : null;
  const isCoarsePointer = React.useMemo(
    () => typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches,
    []
  );

  React.useEffect(() => {
    if (type === 'ordering' || type === 'build_list') {
      const sourceItems = metadata.items || question.answer_options || [];
      setOrderedItems([...(Array.isArray(sourceItems) ? sourceItems : [])]);
    } else {
      setOrderedItems([]);
    }

    setOrderConfirmed(false);
    setBlankValue('');
    setSelectedMatches({});
    setMatchesConfirmed(false);
    setSelectedHotspot('');
    setSelectedMulti([]);
  }, [question.question_id, type]);

  const markIncomplete = () => onSelectAnswer(null);
  const getOptionClassName = (index) => {
    const classes = ['option'];
    
    if (selectedIndex === index) {
      classes.push('selected');
    }
    
    if (showCorrectAnswer) {
      if (index === correctIndex) {
        classes.push('correct');
      } else if (selectedIndex === index && index !== correctIndex) {
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

  const reorderItems = (fromIndex, toIndex) => {
    if (fromIndex === toIndex) return;

    const updated = [...orderedItems];
    const [moved] = updated.splice(fromIndex, 1);
    updated.splice(toIndex, 0, moved);
    setOrderedItems(updated);
    setOrderConfirmed(false);
    markIncomplete();
  };

  const handleDrop = (dropIndex) => {
    if (dragIndex === null || dragIndex === dropIndex) return;

    reorderItems(dragIndex, dropIndex);
    setDragIndex(null);
  };

  const handleTouchStart = (index, pointerId = null, touchId = null) => {
    if (disabled) return;
    setTouchDragIndex(index);
    setTouchDropIndex(index);
    if (pointerId !== null) {
      setActivePointerId(pointerId);
    }
    if (touchId !== null) {
      setActiveTouchId(touchId);
    }
  };

  const handleTouchMove = (clientX, clientY) => {
    if (touchDragIndex === null) return;

    const targetElement = document.elementFromPoint(clientX, clientY);
    const rowElement = targetElement?.closest?.('.drag-item');
    if (!rowElement) return;

    const nextIndex = Number(rowElement.getAttribute('data-order-index'));
    if (Number.isInteger(nextIndex)) {
      setTouchDropIndex(nextIndex);
    }
  };

  const handleTouchMoveEvent = (event) => {
    if (touchDragIndex === null) return;

    const touch = event.touches?.[0];
    if (!touch) return;

    handleTouchMove(touch.clientX, touch.clientY);
    event.preventDefault();
  };

  const clearTouchState = () => {
    setTouchDragIndex(null);
    setTouchDropIndex(null);
    setActivePointerId(null);
    setActiveTouchId(null);
  };

  const handleTouchEnd = () => {
    if (
      touchDragIndex !== null
      && touchDropIndex !== null
      && touchDragIndex !== touchDropIndex
    ) {
      reorderItems(touchDragIndex, touchDropIndex);
    }

    clearTouchState();
  };

  React.useEffect(() => {
    if (activePointerId === null) return;

    const onPointerMove = (event) => {
      if (event.pointerId !== activePointerId) return;
      handleTouchMove(event.clientX, event.clientY);
      event.preventDefault();
    };

    const onPointerUp = (event) => {
      if (event.pointerId !== activePointerId) return;
      handleTouchEnd();
    };

    const onPointerCancel = (event) => {
      if (event.pointerId !== activePointerId) return;
      clearTouchState();
    };

    window.addEventListener('pointermove', onPointerMove, { passive: false });
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerCancel);

    return () => {
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
      window.removeEventListener('pointercancel', onPointerCancel);
    };
  }, [activePointerId, touchDragIndex, touchDropIndex]);

  React.useEffect(() => {
    if (activeTouchId === null) return;

    const onTouchMove = (event) => {
      const activeTouch = Array.from(event.touches || []).find((touch) => touch.identifier === activeTouchId);
      if (!activeTouch) return;
      handleTouchMove(activeTouch.clientX, activeTouch.clientY);
      event.preventDefault();
    };

    const onTouchEnd = (event) => {
      const endedTouch = Array.from(event.changedTouches || []).find((touch) => touch.identifier === activeTouchId);
      if (!endedTouch) return;
      handleTouchEnd();
    };

    const onTouchCancel = (event) => {
      const canceledTouch = Array.from(event.changedTouches || []).find((touch) => touch.identifier === activeTouchId);
      if (!canceledTouch) return;
      clearTouchState();
    };

    window.addEventListener('touchmove', onTouchMove, { passive: false });
    window.addEventListener('touchend', onTouchEnd);
    window.addEventListener('touchcancel', onTouchCancel);

    return () => {
      window.removeEventListener('touchmove', onTouchMove);
      window.removeEventListener('touchend', onTouchEnd);
      window.removeEventListener('touchcancel', onTouchCancel);
    };
  }, [activeTouchId, touchDragIndex, touchDropIndex]);

  const renderTypeSpecificArea = () => {
    if (type === 'ordering' || type === 'build_list') {
      return (
        <div className="type-box">
          <p className="type-helper">Drag rows on desktop, or use ↑/↓ buttons on mobile, then click confirm.</p>
          {orderedItems.length === 0 && (
            <p className="type-empty">No items available for ordering.</p>
          )}
          <div
            className={`drag-list ${touchDragIndex !== null ? 'touch-active' : ''}`}
            onTouchMove={handleTouchMoveEvent}
            onTouchEnd={handleTouchEnd}
            onTouchCancel={clearTouchState}
          >
            {orderedItems.map((item, index) => (
              <div
                key={`${item}-${index}`}
                className={`drag-item ${touchDragIndex === index ? 'touch-dragging' : ''} ${touchDragIndex !== null && touchDropIndex === index && touchDragIndex !== index ? 'touch-target' : ''}`}
                data-order-index={index}
                draggable={!disabled && !isCoarsePointer}
                onDragStart={() => handleDragStart(index)}
                onDragOver={(event) => event.preventDefault()}
                onDrop={() => handleDrop(index)}
                onDragEnd={() => setDragIndex(null)}
              >
                <span className="drag-position">{index + 1}</span>
                <span
                  className="drag-handle"
                  onTouchStart={(event) => {
                    event.preventDefault();
                    const touchId = event.changedTouches?.[0]?.identifier;
                    handleTouchStart(index, null, touchId ?? null);
                  }}
                  onPointerDown={(event) => {
                    if (event.pointerType !== 'touch') return;
                    event.preventDefault();
                    handleTouchStart(index, event.pointerId);
                  }}
                >
                  ☰
                </span>
                <span className="drag-text">{item}</span>
              </div>
            ))}
          </div>
          <button
            className={`type-action ${orderConfirmed ? 'confirmed' : ''}`}
            disabled={disabled || orderedItems.length === 0}
            onClick={() => {
              onSelectAnswer({ ordered_items: orderedItems });
              setOrderConfirmed(true);
            }}
          >
            {orderConfirmed ? 'Order Confirmed' : 'Confirm Order'}
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
                  setMatchesConfirmed(false);
                  markIncomplete();
                }}
              >
                <option value="">Select match</option>
                {rightItems.map((right) => (
                  <option key={right} value={right}>{right}</option>
                ))}
              </select>
            </div>
          ))}
          <button
            className={`type-action ${matchesConfirmed ? 'confirmed' : ''}`}
            disabled={disabled || !allSelected}
            onClick={() => {
              onSelectAnswer({ selected_matches: selectedMatches });
              setMatchesConfirmed(true);
            }}
          >
            {matchesConfirmed ? 'Matches Confirmed' : 'Confirm Matches'}
          </button>
        </div>
      );
    }

    if (type === 'hotspot') {
      const hotspots = metadata.hotspots || ['A', 'B', 'C', 'D'];
      const correctSpot = correctAnswer?.spot || metadata.correct_hotspot;
      return (
        <div className="type-box">
          <p className="type-helper">Click a hotspot area.</p>
          <div className="hotspot-grid">
            {hotspots.map((spot) => (
              <button
                key={spot}
                className={`hotspot-btn ${selectedHotspot === spot ? 'active' : ''} ${showCorrectAnswer && spot === correctSpot ? 'correct' : ''} ${showCorrectAnswer && selectedHotspotValue === spot && spot !== correctSpot ? 'incorrect' : ''}`}
                disabled={disabled}
                onClick={() => {
                  setSelectedHotspot(spot);
                  onSelectAnswer({ selected_hotspot: spot });
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
                onSelectAnswer({ answer_text: value.trim() });
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
                        onSelectAnswer({ selected_indices: updated });
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
                className={`tf-btn ${selectedIndex === index ? 'active' : ''} ${showCorrectAnswer && index === correctIndex ? 'correct' : ''} ${showCorrectAnswer && selectedIndex === index && index !== correctIndex ? 'incorrect' : ''}`}
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
          {answerOptions.length === 0 && (
            <div className="type-helper">No answer options found for this question.</div>
          )}
          {answerOptions.map((option, index) => (
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
              {showCorrectAnswer && selectedIndex === index && index !== correctIndex && (
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
