"""
Question Model - Represents exam questions in ExamBuddy
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class DifficultyLevel(str, Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class Question(BaseModel):
    """Question entity model"""
    question_id: str = Field(..., description="Unique question identifier (UUID)")
    project_id: str = Field(..., description="Parent project ID")
    text: str = Field(..., min_length=1, max_length=2000, description="Question text")
    answer_options: List[str] = Field(..., min_items=2, max_items=6, description="List of answer options")
    correct_index: int = Field(..., ge=0, description="Index of correct answer (0-based)")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="Question difficulty")
    time_limit_seconds: int = Field(default=60, ge=10, le=300, description="Time limit in seconds (10-300)")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Creation timestamp")
    source: str = Field(default="manual", description="Source of question (manual, pdf)")
    tags: Optional[List[str]] = Field(default=None, description="Question tags/categories")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "question_id": "q-123e4567-e89b-12d3-a456-426614174000",
                "project_id": "proj-123e4567-e89b-12d3-a456-426614174000",
                "text": "What is the output of print(type([]))?",
                "answer_options": [
                    "<class 'list'>",
                    "<class 'dict'>",
                    "<class 'tuple'>",
                    "<class 'set'>"
                ],
                "correct_index": 0,
                "difficulty": "easy",
                "time_limit_seconds": 60,
                "created_at": "2026-02-06T10:00:00Z",
                "source": "manual",
                "tags": ["python", "basics"]
            }
        }
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format with PK/SK pattern"""
        return {
            'PK': f'PROJECT#{self.project_id}',
            'SK': f'QUESTION#{self.question_id}',
            'GSI1PK': f'PROJECT#{self.project_id}',  # For project's questions
            'GSI1SK': f'DIFFICULTY#{self.difficulty}#{self.question_id}',
            'entity_type': 'question',
            'question_id': self.question_id,
            'project_id': self.project_id,
            'text': self.text,
            'answer_options': self.answer_options,
            'correct_index': self.correct_index,
            'difficulty': self.difficulty,
            'time_limit_seconds': self.time_limit_seconds,
            'created_at': self.created_at,
            'source': self.source,
            'tags': self.tags or []
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Question':
        """Create Question instance from DynamoDB item"""
        return cls(
            question_id=item['question_id'],
            project_id=item['project_id'],
            text=item['text'],
            answer_options=item['answer_options'],
            correct_index=item['correct_index'],
            difficulty=item.get('difficulty', 'medium'),
            time_limit_seconds=item.get('time_limit_seconds', 60),
            created_at=item['created_at'],
            source=item.get('source', 'manual'),
            tags=item.get('tags', [])
        )


class QuestionCreate(BaseModel):
    """Question creation request model"""
    text: str = Field(..., min_length=1, max_length=2000)
    answer_options: List[str] = Field(..., min_items=2, max_items=6)
    correct_index: int = Field(..., ge=0)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    time_limit_seconds: int = Field(default=60, ge=10, le=300)
    tags: Optional[List[str]] = None


class QuestionUpdate(BaseModel):
    """Question update request model"""
    text: Optional[str] = Field(None, min_length=1, max_length=2000)
    answer_options: Optional[List[str]] = Field(None, min_items=2, max_items=6)
    correct_index: Optional[int] = Field(None, ge=0)
    difficulty: Optional[DifficultyLevel] = None
    time_limit_seconds: Optional[int] = Field(None, ge=10, le=300)
    tags: Optional[List[str]] = None


class QuestionResponse(BaseModel):
    """Question response model (hides correct answer)"""
    question_id: str
    project_id: str
    text: str
    answer_options: List[str]
    difficulty: DifficultyLevel
    time_limit_seconds: int
    created_at: str
    tags: Optional[List[str]]


class QuestionAdminResponse(BaseModel):
    """Question response for admins (includes correct answer)"""
    question_id: str
    project_id: str
    text: str
    answer_options: List[str]
    correct_index: int
    difficulty: DifficultyLevel
    time_limit_seconds: int
    created_at: str
    source: str
    tags: Optional[List[str]]
