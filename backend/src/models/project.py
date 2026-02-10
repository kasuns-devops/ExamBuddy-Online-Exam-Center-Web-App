"""
Project Model - Represents exam projects created by admins
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Project(BaseModel):
    """Project entity model"""
    project_id: str = Field(..., description="Unique project identifier (UUID)")
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    admin_id: str = Field(..., description="ID of admin who created the project")
    archived: bool = Field(default=False, description="Archive status")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Last update timestamp")
    question_count: int = Field(default=0, description="Total number of questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj-123e4567-e89b-12d3-a456-426614174000",
                "name": "Python Fundamentals Exam",
                "description": "Comprehensive Python programming assessment",
                "admin_id": "550e8400-e29b-41d4-a716-446655440000",
                "archived": False,
                "created_at": "2026-02-06T10:00:00Z",
                "updated_at": "2026-02-06T10:00:00Z",
                "question_count": 50
            }
        }
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format with PK/SK pattern"""
        return {
            'PK': f'PROJECT#{self.project_id}',
            'SK': f'METADATA',
            'GSI1PK': f'ADMIN#{self.admin_id}',  # For admin's project list
            'GSI1SK': f'PROJECT#{self.created_at}',
            'GSI2PK': 'ALL_PROJECTS',  # For global project list
            'GSI2SK': f'PROJECT#{self.created_at}',
            'entity_type': 'project',
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'admin_id': self.admin_id,
            'archived': self.archived,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'question_count': self.question_count
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Project':
        """Create Project instance from DynamoDB item"""
        return cls(
            project_id=item['project_id'],
            name=item['name'],
            description=item.get('description'),
            admin_id=item['admin_id'],
            archived=item.get('archived', False),
            created_at=item['created_at'],
            updated_at=item['updated_at'],
            question_count=item.get('question_count', 0)
        )


class ProjectCreate(BaseModel):
    """Project creation request model"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectUpdate(BaseModel):
    """Project update request model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    archived: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Project response model"""
    project_id: str
    name: str
    description: Optional[str]
    admin_id: str
    archived: bool
    created_at: str
    updated_at: str
    question_count: int
