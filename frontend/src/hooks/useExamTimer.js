/**
 * Timer Hook - Custom hook for exam timer management
 */
import { useEffect, useRef, useCallback } from 'react';
import useExamStore from '../stores/examStore';

export const useExamTimer = (onTimeUp, paused = false) => {
  const {
    timeRemaining,
    reviewTimeRemaining,
    isReviewPhase,
    questionStartTime,
    updateTimeRemaining,
    updateReviewTime
  } = useExamStore();

  const intervalRef = useRef(null);
  const startTimeRef = useRef(null);
  const initialTimeRef = useRef(null);
  const onTimeUpRef = useRef(onTimeUp);

  useEffect(() => {
    onTimeUpRef.current = onTimeUp;
  }, [onTimeUp]);

  const startTimer = useCallback((initialTime, reviewMode = false) => {
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

      if (reviewMode) {
        updateReviewTime(remaining);
      } else {
        updateTimeRemaining(remaining);
      }

      if (remaining === 0) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        if (onTimeUpRef.current) {
          onTimeUpRef.current();
        }
      }
    }, 100);
  }, [updateTimeRemaining, updateReviewTime]);

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

  // Start/reset question timer only when question changes
  useEffect(() => {
    if (paused) {
      stopTimer();
      return;
    }
    if (isReviewPhase) return;
    if (!questionStartTime) return;
    if (timeRemaining <= 0) return;

    startTimer(timeRemaining, false);
  }, [questionStartTime, isReviewPhase, paused, startTimer, stopTimer]);

  // Start review timer when review phase begins (or first receives a positive value)
  useEffect(() => {
    if (paused) {
      stopTimer();
      return;
    }
    if (!isReviewPhase) return;
    if (reviewTimeRemaining <= 0) return;
    if (intervalRef.current) return;

    startTimer(reviewTimeRemaining, true);
  }, [isReviewPhase, reviewTimeRemaining, paused, startTimer, stopTimer]);

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
