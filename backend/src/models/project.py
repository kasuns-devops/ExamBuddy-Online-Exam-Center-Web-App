"""
Project Model - Represents exam projects created by admins
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Set
from datetime import datetime
from enum import Enum


PROJECT_ENTITY_TYPE = 'project'
PROJECT_DYNAMODB_PK_PREFIX = 'PROJECT#'
PROJECT_DYNAMODB_SK_METADATA = 'METADATA'


class ProjectStatus(str, Enum):
    """Lifecycle status of a project question bank"""
    DRAFT = 'DRAFT'
    PROCESSING = 'PROCESSING'
    PUBLISHED = 'PUBLISHED'
    FAILED = 'FAILED'
    ARCHIVED = 'ARCHIVED'


class ProjectIngestionStatus(str, Enum):
    """Status of uploaded project document ingestion"""
    UPLOADED = 'UPLOADED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


PROJECT_STATUS_TRANSITIONS: Dict[ProjectStatus, Set[ProjectStatus]] = {
    ProjectStatus.DRAFT: {ProjectStatus.PROCESSING, ProjectStatus.ARCHIVED},
    ProjectStatus.PROCESSING: {ProjectStatus.PUBLISHED, ProjectStatus.FAILED, ProjectStatus.ARCHIVED},
    ProjectStatus.FAILED: {ProjectStatus.PROCESSING, ProjectStatus.ARCHIVED},
    ProjectStatus.PUBLISHED: {ProjectStatus.PROCESSING, ProjectStatus.ARCHIVED},
    ProjectStatus.ARCHIVED: set(),
}


def map_ingestion_to_project_status(ingestion_status: ProjectIngestionStatus) -> ProjectStatus:
    """Map document ingestion status to project lifecycle status."""
    if ingestion_status in (ProjectIngestionStatus.UPLOADED, ProjectIngestionStatus.PROCESSING):
        return ProjectStatus.PROCESSING
    if ingestion_status == ProjectIngestionStatus.COMPLETED:
        return ProjectStatus.PUBLISHED
    return ProjectStatus.FAILED


class Project(BaseModel):
    """Project entity model"""
    project_id: str = Field(..., description="Unique project identifier (UUID)")
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    admin_id: str = Field(..., description="ID of admin who created the project")
    archived: bool = Field(default=False, description="Archive status")
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT, description="Project lifecycle status")
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
            'entity_type': PROJECT_ENTITY_TYPE,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'admin_id': self.admin_id,
            'archived': self.archived,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'question_count': self.question_count
        }

    @staticmethod
    def can_transition(current_status: ProjectStatus, next_status: ProjectStatus) -> bool:
        """Validate if status transition is allowed by lifecycle rules."""
        if current_status == next_status:
            return True
        return next_status in PROJECT_STATUS_TRANSITIONS.get(current_status, set())
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'Project':
        """Create Project instance from DynamoDB item"""
        return cls(
            project_id=item['project_id'],
            name=item['name'],
            description=item.get('description'),
            admin_id=item['admin_id'],
            archived=item.get('archived', False),
            status=item.get('status', ProjectStatus.DRAFT),
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
    status: ProjectStatus
    created_at: str
    updated_at: str
    question_count: int


class ProjectDocument(BaseModel):
    """Uploaded project PDF document and ingestion status."""
    document_id: str
    project_id: str
    file_name: str
    s3_key: str
    content_type: str = Field(default='application/pdf')
    file_size_bytes: int = Field(default=0, ge=0)
    ingestion_status: ProjectIngestionStatus = Field(default=ProjectIngestionStatus.UPLOADED)
    error_message: Optional[str] = None
    uploaded_by: str
    uploaded_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processed_at: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dynamodb_item(self) -> dict:
        return {
            'PK': f'PROJECT#{self.project_id}',
            'SK': f'DOCUMENT#{self.document_id}',
            'entity_type': 'project_document',
            'document_id': self.document_id,
            'project_id': self.project_id,
            'file_name': self.file_name,
            's3_key': self.s3_key,
            'content_type': self.content_type,
            'file_size_bytes': self.file_size_bytes,
            'ingestion_status': self.ingestion_status.value,
            'error_message': self.error_message,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at,
            'processed_at': self.processed_at,
            'updated_at': self.updated_at,
        }
