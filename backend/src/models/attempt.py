"""
Attempt Model - Represents candidate exam attempts and results
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class ExamMode(str, Enum):
    """Exam mode types"""
    EXAM = "exam"  # Timed exam with review phase
    PRACTICE = "practice"  # Immediate feedback, no review


class DifficultyLevel(str, Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class AttemptStatus(str, Enum):
    """Attempt status"""
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"  # Exam mode only
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AnswerRecord(BaseModel):
    """Individual answer record"""
    question_id: str
    selected_index: int
    is_correct: bool
    time_spent_seconds: int
    answered_at: str


class Attempt(BaseModel):
    """Attempt entity model"""
    attempt_id: str = Field(..., description="Unique attempt identifier (UUID)")
    candidate_id: str = Field(..., description="Candidate user ID")
    project_id: str = Field(..., description="Project ID")
    mode: ExamMode = Field(..., description="Exam mode (exam or practice)")
    difficulty: DifficultyLevel = Field(..., description="Question difficulty level")
    status: AttemptStatus = Field(default=AttemptStatus.IN_PROGRESS, description="Attempt status")
    question_count: int = Field(..., ge=1, le=100, description="Number of questions")
    score: Optional[float] = Field(None, ge=0, le=100, description="Final score percentage")
    correct_count: Optional[int] = Field(None, ge=0, description="Number of correct answers")
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Start timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    total_time_seconds: Optional[int] = Field(None, description="Total time spent")
    answers: List[AnswerRecord] = Field(default=[], description="List of answer records")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "attempt_id": "attempt-123e4567-e89b-12d3-a456-426614174000",
                "candidate_id": "user-550e8400-e29b-41d4-a716-446655440000",
                "project_id": "proj-123e4567-e89b-12d3-a456-426614174000",
                "mode": "exam",
                "difficulty": "medium",
                "status": "completed",
                "question_count": 20,
                "score": 85.0,
                "correct_count": 17,
                "started_at": "2026-02-06T10:00:00Z",
                "completed_at": "2026-02-06T10:25:00Z",
                "total_time_seconds": 1500,
                "answers": []
            }
        }
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format with PK/SK pattern"""
        return {
            'PK': f'CANDIDATE#{self.candidate_id}',
            'SK': f'ATTEMPT#{self.started_at}#{self.attempt_id}',
            'GSI1PK': f'PROJECT#{self.project_id}',  # For project's attempts
            'GSI1SK': f'ATTEMPT#{self.started_at}',
            'GSI2PK': f'ATTEMPT#{self.attempt_id}',  # For direct attempt lookup
            'GSI2SK': f'METADATA',
            'entity_type': 'attempt',
            'attempt_id': self.attempt_id,
            'candidate_id': self.candidate_id,
            'project_id': self.project_id,
            'mode': self.mode,
            'difficulty': self.difficulty,
            'status': self.status,
            'question_count': self.question_count,
            'score': self.score,
            'correct_count': self.correct_count,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'total_time_seconds': self.total_time_seconds,
            'answers': [a.dict() for a in self.answers]
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Attempt':
        """Create Attempt instance from DynamoDB item"""
        return cls(
            attempt_id=item['attempt_id'],
            candidate_id=item['candidate_id'],
            project_id=item['project_id'],
            mode=item['mode'],
            difficulty=item['difficulty'],
            status=item.get('status', 'in_progress'),
            question_count=item['question_count'],
            score=item.get('score'),
            correct_count=item.get('correct_count'),
            started_at=item['started_at'],
            completed_at=item.get('completed_at'),
            total_time_seconds=item.get('total_time_seconds'),
            answers=[AnswerRecord(**a) for a in item.get('answers', [])]
        )


class AttemptCreate(BaseModel):
    """Attempt creation request"""
    project_id: str
    mode: ExamMode
    difficulty: DifficultyLevel
    question_count: int = Field(..., ge=1, le=100)


class AnswerSubmit(BaseModel):
    """Answer submission request"""
    question_id: str
    selected_index: int = Field(..., ge=0)
    time_spent_seconds: int = Field(..., ge=0)


class AttemptResponse(BaseModel):
    """Attempt response model"""
    attempt_id: str
    project_id: str
    mode: ExamMode
    difficulty: DifficultyLevel
    status: AttemptStatus
    question_count: int
    score: Optional[float]
    correct_count: Optional[int]
    started_at: str
    completed_at: Optional[str]
    total_time_seconds: Optional[int]


class AttemptDetailResponse(AttemptResponse):
    """Detailed attempt response with answers"""
    answers: List[AnswerRecord]
