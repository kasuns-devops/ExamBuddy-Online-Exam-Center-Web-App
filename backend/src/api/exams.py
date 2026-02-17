"""
Exams API Router - Endpoints for exam session management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from src.services.exam_service import ExamService, ExamMode
from src.services.question_service import QuestionService
from src.models.question import DifficultyLevel
from src.middleware.auth_middleware import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/exams", tags=["exams"])

# Service instances
exam_service = ExamService()
question_service = QuestionService()


# Request/Response models
class StartExamRequest(BaseModel):
    """Request to start a new exam session"""
    project_id: str = Field(..., description="Project ID to create exam from")
    mode: ExamMode = Field(..., description="Exam mode (exam or test)")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Question difficulty filter")
    question_count: int = Field(..., ge=5, le=100, description="Number of questions")


class StartExamResponse(BaseModel):
    """Response after starting an exam"""
    session_id: str
    questions: List[dict]  # Questions without correct answers
    mode: str
    started_at: str
    total_time_seconds: int


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer"""
    question_id: str
    answer_index: int


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer"""
    is_correct: bool
    time_spent: float
    accepted: bool
    correct_index: Optional[int] = None  # Only in test mode


class ReviewPhaseResponse(BaseModel):
    """Response for review phase"""
    questions: List[dict]
    answers: dict
    review_time_seconds: int
    review_started_at: str


class FinalizeExamResponse(BaseModel):
    """Response after finalizing exam"""
    attempt_id: str
    score: float
    correct_count: int
    total_questions: int
    answers: List[dict]
    completed_at: str


class PresentRequest(BaseModel):
    question_id: str
    presented_at: Optional[str] = None  # ISO timestamp (optional)


@router.post("/start", response_model=StartExamResponse, status_code=status.HTTP_201_CREATED)
async def start_exam(
    request: StartExamRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new exam session with randomly selected questions.
    
    - Randomly selects questions from the project
    - Creates exam session
    - Returns questions without revealing correct answers
    """
    try:
        # Get random questions from question service
        questions = await question_service.random_select_questions(
            project_id=request.project_id,
            count=request.question_count,
            difficulty=request.difficulty
        )
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No questions found for project {request.project_id}"
            )
        
        # Start exam session
        session = await exam_service.start_exam_session(
            candidate_id=current_user["user_id"],
            project_id=request.project_id,
            mode=request.mode,
            questions=questions,
            difficulty=request.difficulty or DifficultyLevel.MEDIUM
        )
        
        # Prepare response (hide correct answers)
        questions_data = [
            {
                "question_id": q.get("question_id") if isinstance(q, dict) else q.question_id,
                "text": q.get("question_text") or q.get("text") if isinstance(q, dict) else q.text,
                "answer_options": q.get("options") or q.get("answer_options") if isinstance(q, dict) else q.answer_options,
                "time_limit_seconds": q.get("time_limit_seconds", 60) if isinstance(q, dict) else q.time_limit_seconds
            }
            for q in questions
        ]
        
        total_time = sum(q.get("time_limit_seconds", 60) if isinstance(q, dict) else q.time_limit_seconds for q in questions)
        
        return StartExamResponse(
            session_id=session.session_id,
            questions=questions_data,
            mode=request.mode.value,
            started_at=session.started_at.isoformat(),
            total_time_seconds=total_time
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start exam: {str(e)}"
        )


@router.post("/{session_id}/present")
async def record_presentation(
    session_id: str,
    request: PresentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Record that a question was presented to the candidate."""
    try:
        presented_at = None
        if request.presented_at:
            try:
                presented_at = datetime.fromisoformat(request.presented_at)
            except Exception:
                presented_at = None

        await exam_service.record_presentation(session_id, request.question_id, presented_at)
        return {"message": "presentation recorded"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{session_id}/answers", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an answer for a question in an active exam session.
    
    - Validates timer (rejects late submissions)
    - Records answer and calculates time spent
    - In test mode, returns correct answer immediately
    """
    try:
        result = await exam_service.validate_answer(
            session_id=session_id,
            question_id=request.question_id,
            answer_index=request.answer_index,
            submitted_at=datetime.utcnow()
        )
        
        return SubmitAnswerResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get("/{session_id}/review", response_model=ReviewPhaseResponse)
async def get_review_phase(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get review phase data for Exam mode (half-time to review all questions).
    
    - Only available for Exam mode
    - Returns all questions with candidate's answers
    - Provides half the original time for review
    """
    try:
        review_data = await exam_service.start_review_phase(session_id)
        return ReviewPhaseResponse(**review_data)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get review phase: {str(e)}"
        )


@router.post("/{session_id}/submit", response_model=FinalizeExamResponse)
async def finalize_exam(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Finalize exam session and calculate final score.
    
    - Calculates score based on correct answers
    - Creates attempt record in database
    - Returns detailed results
    """
    try:
        attempt = await exam_service.finalize_exam(session_id)
        
        return FinalizeExamResponse(
            attempt_id=attempt.attempt_id,
            score=attempt.score,
            correct_count=attempt.correct_count,
            total_questions=attempt.question_count,
            answers=[a.dict() for a in attempt.answers],
            completed_at=attempt.completed_at
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finalize exam: {str(e)}"
        )


@router.delete("/{session_id}")
async def cancel_exam(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel an exam session without saving attempt.
    
    - Deletes session data
    - Does not create attempt record
    """
    try:
        success = await exam_service.cancel_exam(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {"message": "Exam cancelled successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel exam: {str(e)}"
        )
