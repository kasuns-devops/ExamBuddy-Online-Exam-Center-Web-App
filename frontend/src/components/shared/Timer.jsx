/**
 * Timer Component - Countdown timer display
 */
import React from 'react';
import './Timer.css';

const Timer = ({ seconds, isWarning = false, isReview = false }) => {
  const formatTime = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getClassName = () => {
    if (seconds <= 10) return 'timer timer-critical';
    if (isWarning || seconds <= 30) return 'timer timer-warning';
    return 'timer timer-normal';
  };

  return (
    <div className={getClassName()}>
      <div className="timer-icon">{isReview ? '📝' : '⏱️'}</div>
      <div className="timer-display">
        <div className="timer-time">{formatTime(seconds)}</div>
        <div className="timer-label">{isReview ? 'Review Time' : 'Time Left'}</div>
      </div>
    </div>
  );
};

export default Timer;
