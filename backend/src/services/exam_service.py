"""
Exam Service - Business logic for exam session management
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from enum import Enum
from src.models.question import Question, DifficultyLevel
from src.models.attempt import Attempt, AttemptStatus, AnswerRecord
from src.database.dynamodb_client import DynamoDBClient


class ExamMode(str, Enum):
    """Exam modes"""
    EXAM = "exam"  # Review phase with half-time
    TEST = "test"  # Immediate feedback, no review


class ExamSession:
    """In-memory exam session state"""
    def __init__(
        self,
        session_id: str,
        candidate_id: str,
        project_id: str,
        mode: ExamMode,
        difficulty: DifficultyLevel,
        questions: List[Question],
        started_at: datetime
    ):
        self.session_id = session_id
        self.candidate_id = candidate_id
        self.project_id = project_id
        self.mode = mode
        self.difficulty = difficulty
        self.questions = questions
        self.question_count = len(questions)
        self.started_at = started_at
        self.answers: Dict[str, dict] = {}  # question_id -> {answer_index, submitted_at, time_spent}
        self.current_question_index = 0
        self.is_review_phase = False
        self.review_started_at: Optional[datetime] = None
        self.completed = False
        # Timestamp of last user action (presentation or submission). Used to compute time_spent per question.
        self.last_action_time: Optional[datetime] = started_at
        # Per-question presentation timestamps (question_id -> ISO timestamp)
        self.presented_times: Dict[str, str] = {}
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for storage"""
        return {
            'session_id': self.session_id,
            'candidate_id': self.candidate_id,
            'project_id': self.project_id,
            'mode': self.mode.value,
            'difficulty': self.difficulty.value,
            'question_count': self.question_count,
            'question_ids': [q.question_id for q in self.questions],
            'started_at': self.started_at.isoformat(),
            'answers': self.answers,
            'current_question_index': self.current_question_index,
            'is_review_phase': self.is_review_phase,
            'review_started_at': self.review_started_at.isoformat() if self.review_started_at else None,
            'completed': self.completed
            ,
            'last_action_time': self.last_action_time.isoformat() if self.last_action_time else None
            ,
            'presented_times': self.presented_times
        }


class ExamService:
    """Service for exam session management"""
    
    def __init__(self):
        self.db = DynamoDBClient()
        # In-memory sessions cache (in production, use Redis or DynamoDB)
        self.active_sessions: Dict[str, ExamSession] = {}
    
    async def start_exam_session(
        self,
        candidate_id: str,
        project_id: str,
        mode: ExamMode,
        questions: List[Question],
        difficulty: DifficultyLevel
    ) -> ExamSession:
        """
        Start a new exam session.
        
        Args:
            candidate_id: User ID of candidate
            project_id: Project ID for exam
            mode: Exam mode (exam or test)
            questions: List of questions for this session
        
        Returns:
            New ExamSession object
        """
        session_id = f"session-{uuid.uuid4()}"
        session = ExamSession(
            session_id=session_id,
            candidate_id=candidate_id,
            project_id=project_id,
            mode=mode,
            difficulty=difficulty,
            questions=questions,
            started_at=datetime.now(timezone.utc)
        )
        
        # Store in cache
        self.active_sessions[session_id] = session
        
        # Persist to DynamoDB for recovery
        await self._persist_session(session)
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[ExamSession]:
        """
        Retrieve an active exam session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            ExamSession if found, None otherwise
        """
        # Check cache first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Try to load from DynamoDB
        session_data = await self.db.get_item(
            pk=f'SESSION#{session_id}',
            sk=f'SESSION#{session_id}'
        )
        
        if not session_data:
            return None
        
        # Reconstruct session (simplified - would need question rehydration)
        # For now, return None if not in cache
        return None
    
    async def validate_answer(
        self,
        session_id: str,
        question_id: str,
        answer_index: int,
        submitted_at: datetime
    ) -> dict:
        """
        Validate and record an answer submission.
        
        Args:
            session_id: Session identifier
            question_id: Question being answered
            answer_index: Index of selected answer (0-based)
            submitted_at: Timestamp of submission
        
        Returns:
            Dictionary with validation result:
            - is_correct: bool
            - correct_index: int (only in test mode)
            - time_spent: float (seconds)
            - accepted: bool (false if submitted after time limit)
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Find the question
        question = next((q for q in session.questions if q.question_id == question_id), None)
        if not question:
            raise ValueError(f"Question {question_id} not found in session")
        
        # Compute time spent based on the per-question presented timestamp if available,
        # otherwise fall back to last_action_time or session start.
        presented_iso = session.presented_times.get(question_id)
        if presented_iso:
            try:
                prev_time = datetime.fromisoformat(presented_iso)
            except Exception:
                prev_time = session.last_action_time or session.started_at
        else:
            prev_time = session.last_action_time or session.started_at

        # Ensure both timestamps are timezone-aware (assume UTC if naive)
        if prev_time.tzinfo is None:
            prev_time = prev_time.replace(tzinfo=timezone.utc)
        if submitted_at.tzinfo is None:
            submitted_at = submitted_at.replace(tzinfo=timezone.utc)

        time_spent = (submitted_at - prev_time).total_seconds()
        if time_spent < 0:
            # Guard against clock skew or inconsistent times
            time_spent = 0.0

        # Validate timer (2 second grace period).
        # Accept if time_spent is within the question's allowed time plus grace.
        time_limit_with_grace = question.time_limit_seconds + 2
        accepted = time_spent <= time_limit_with_grace
        
        # Check correctness
        is_correct = answer_index == question.correct_index
        
        # Record answer
        session.answers[question_id] = {
            'answer_index': answer_index,
            'submitted_at': submitted_at.isoformat(),
            'time_spent': time_spent,
            'is_correct': is_correct,
            'accepted': accepted
        }
        
        # Advance current question index
        question_index = next(
            (i for i, q in enumerate(session.questions) if q.question_id == question_id),
            session.current_question_index
        )
        session.current_question_index = max(session.current_question_index, question_index + 1)
        
        # Update last action time to this submission and persist session
        session.last_action_time = submitted_at
        await self._persist_session(session)
        
        result = {
            'is_correct': is_correct,
            'time_spent': time_spent,
            'accepted': accepted
        }
        
        # In test mode, reveal correct answer immediately
        if session.mode == ExamMode.TEST:
            result['correct_index'] = question.correct_index
        
        return result
    
    async def calculate_score(self, session_id: str) -> dict:
        """
        Calculate final score for an exam session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dictionary with scoring details:
            - score: float (0-100)
            - correct_count: int
            - total_questions: int
            - answers: list of answer details
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        total_questions = len(session.questions)
        answered_questions = len(session.answers)
        
        # Count correct answers (only accepted submissions)
        correct_count = sum(
            1 for ans in session.answers.values()
            if ans.get('is_correct') and ans.get('accepted')
        )
        
        # Calculate score percentage
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Build detailed answer breakdown
        answers_detail = []
        for question in session.questions:
            answer_data = session.answers.get(question.question_id, {})
            answers_detail.append({
                'question_id': question.question_id,
                'question_text': question.text,
                'selected_index': answer_data.get('answer_index'),
                'correct_index': question.correct_index,
                'is_correct': answer_data.get('is_correct', False),
                'time_spent': answer_data.get('time_spent', 0),
                'accepted': answer_data.get('accepted', False)
            })
        
        return {
            'score': round(score, 2),
            'correct_count': correct_count,
            'total_questions': total_questions,
            'answered_count': answered_questions,
            'answers': answers_detail
        }
    
    async def start_review_phase(self, session_id: str) -> dict:
        """
        Start review phase for exam mode (half time to review all questions).
        
        Args:
            session_id: Session identifier
        
        Returns:
            Review phase data with questions and half-time limit
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if session.mode != ExamMode.EXAM:
            raise ValueError("Review phase only available in Exam mode")
        
        session.is_review_phase = True
        session.review_started_at = datetime.utcnow()
        
        # Calculate total time and half-time for review
        total_time = sum(q.time_limit_seconds for q in session.questions)
        review_time = total_time // 2
        
        await self._persist_session(session)
        
        return {
            'questions': [q.dict() for q in session.questions],
            'answers': session.answers,
            'review_time_seconds': review_time,
            'review_started_at': session.review_started_at.isoformat()
        }
    
    async def finalize_exam(self, session_id: str) -> Attempt:
        """
        Finalize exam and create attempt record.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Created Attempt object
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Calculate final score
        score_data = await self.calculate_score(session_id)
        
        # Create attempt record
        total_time_seconds = int(
            sum(a.get('time_spent', 0) for a in session.answers.values())
        )
        answer_records = []
        for question in session.questions:
            answer_data = session.answers.get(question.question_id, {})
            if 'answer_index' in answer_data:
                answer_records.append(
                    AnswerRecord(
                        question_id=question.question_id,
                        selected_index=answer_data.get('answer_index'),
                        is_correct=answer_data.get('is_correct', False),
                        time_spent_seconds=int(answer_data.get('time_spent', 0)),
                        answered_at=answer_data.get('submitted_at', datetime.utcnow().isoformat())
                    )
                )

        # Map internal ExamMode.TEST to Attempt.ExamMode.PRACTICE for compatibility
        mode_value = 'practice' if session.mode == ExamMode.TEST else session.mode.value

        attempt = Attempt(
            attempt_id=f"attempt-{uuid.uuid4()}",
            candidate_id=session.candidate_id,
            project_id=session.project_id,
            mode=mode_value,
            difficulty=session.difficulty.value,
            status=AttemptStatus.COMPLETED,
            question_count=session.question_count,
            score=score_data['score'],
            total_questions=score_data['total_questions'],
            correct_count=score_data['correct_count'],
            started_at=session.started_at.isoformat(),
            completed_at=datetime.utcnow().isoformat(),
            total_time_seconds=total_time_seconds,
            answers=answer_records
        )
        
        # Save attempt to DynamoDB
        await self._save_attempt(attempt)
        
        # Mark session as completed
        session.completed = True
        await self._persist_session(session)
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return attempt

    async def record_presentation(self, session_id: str, question_id: str, presented_at: Optional[datetime] = None) -> bool:
        """
        Record the timestamp when a question was presented to the candidate.
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if presented_at is None:
            presented_at = datetime.utcnow()

        session.presented_times[question_id] = presented_at.isoformat()
        session.last_action_time = presented_at
        await self._persist_session(session)
        return True
    
    async def cancel_exam(self, session_id: str) -> bool:
        """
        Cancel an exam session without saving attempt.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if cancelled successfully
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Delete from DynamoDB
        await self.db.delete_item(
            pk=f'SESSION#{session_id}',
            sk=f'SESSION#{session_id}'
        )
        
        return True
    
    async def _persist_session(self, session: ExamSession):
        """Persist session state to DynamoDB"""
        item = {
            'PK': f'SESSION#{session.session_id}',
            'SK': f'SESSION#{session.session_id}',
            'TTL': int((datetime.utcnow() + timedelta(hours=24)).timestamp()),  # Auto-expire after 24h
            **session.to_dict()
        }
        await self.db.put_item(item)
    
    async def _save_attempt(self, attempt: Attempt):
        """Save attempt record to DynamoDB"""
        item = {
            'PK': f'CANDIDATE#{attempt.candidate_id}',
            'SK': f'ATTEMPT#{attempt.attempt_id}',
            'GSI1PK': f'PROJECT#{attempt.project_id}',
            'GSI1SK': f'ATTEMPT#{attempt.completed_at}',
            'GSI3PK': f'CANDIDATE#{attempt.candidate_id}',
            'GSI3SK': f'COMPLETED#{attempt.completed_at}',
            **attempt.dict()
        }
        await self.db.put_item(item)
