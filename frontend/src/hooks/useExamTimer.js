/**
 * Timer Hook - Custom hook for exam timer management
 */
import { useEffect, useRef, useCallback } from 'react';
import useExamStore from '../stores/examStore';

export const useExamTimer = (onTimeUp) => {
  const {
    timeRemaining,
    reviewTimeRemaining,
    isReviewPhase,
    updateTimeRemaining,
    updateReviewTime
  } = useExamStore();

  const intervalRef = useRef(null);
  const startTimeRef = useRef(null);
  const initialTimeRef = useRef(null);

  const startTimer = useCallback((initialTime) => {
    startTimeRef.current = Date.now();
    initialTimeRef.current = initialTime;

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    // Update every 100ms for smooth countdown
    intervalRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      const remaining = Math.max(0, initialTimeRef.current - elapsed);

      if (isReviewPhase) {
        updateReviewTime(remaining);
      } else {
        updateTimeRemaining(remaining);
      }

      if (remaining === 0) {
        clearInterval(intervalRef.current);
        if (onTimeUp) {
          onTimeUp();
        }
      }
    }, 100);
  }, [isReviewPhase, updateTimeRemaining, updateReviewTime, onTimeUp]);

  const stopTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const resetTimer = useCallback((newTime) => {
    stopTimer();
    if (newTime > 0) {
      startTimer(newTime);
    }
  }, [stopTimer, startTimer]);

  // Auto-start timer when time changes
  useEffect(() => {
    const currentTime = isReviewPhase ? reviewTimeRemaining : timeRemaining;
    if (currentTime > 0 && !intervalRef.current) {
      startTimer(currentTime);
    }
  }, [timeRemaining, reviewTimeRemaining, isReviewPhase, startTimer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    timeRemaining: isReviewPhase ? reviewTimeRemaining : timeRemaining,
    startTimer,
    stopTimer,
    resetTimer
  };
};

export default useExamTimer;
