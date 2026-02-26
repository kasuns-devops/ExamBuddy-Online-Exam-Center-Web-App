# Regression Checklist

Use this quick pass before/after deployment to ensure exam flows stay stable.

## 1) Authentication
- Login with Cognito Hosted UI.
- Verify dashboard loads without redirect loop.
- Confirm protected API calls include `Authorization: Bearer ...`.

## 2) Test Mode (Immediate Feedback)
- Start exam with max available questions (cannot exceed available count).
- For `true_false`, submit both correct and wrong answers and verify highlight states.
- For `fill_in_blank`, submit wrong text and verify incorrect feedback.
- For `multiple_response`, submit wrong checkbox set and verify incorrect feedback.
- For `hotspot`, submit wrong area and verify correct hotspot is highlighted.
- After submit, verify timer is paused until `Next Question` is clicked.
- Verify timer resets on every next question.

## 3) Exam Mode (End Review)
- Complete exam with mixed correct/wrong answers.
- Submit and verify final results include:
  - question text,
  - selected answer,
  - correct answer,
  - correct/incorrect status.

## 4) Ordering / Build List
- Next/Submit remains disabled until `Confirm Order` is clicked.
- `Confirm Order` color changes when confirmed.
- If timer expires before confirmation, question auto-skips as unanswered.

## 5) API Stability
- Verify `POST /api/exams/{session_id}/answers` returns `200`.
- Verify `POST /api/exams/{session_id}/submit` returns `200`.
- If `401` appears, refresh login and retest one full exam flow.

## 6) Basic Health
- `GET /health` returns healthy response.
- Frontend production build succeeds.
