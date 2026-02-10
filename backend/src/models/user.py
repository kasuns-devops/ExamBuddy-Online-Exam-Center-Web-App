"""
User Model - Represents users (admins and candidates) in ExamBuddy
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    """User role enum"""
    ADMIN = "admin"
    CANDIDATE = "candidate"


class User(BaseModel):
    """User entity model"""
    user_id: str = Field(..., description="Unique user identifier (UUID)")
    email: EmailStr = Field(..., description="User email address")
    password_hash: str = Field(..., description="Bcrypt password hash")
    role: UserRole = Field(..., description="User role (admin or candidate)")
    full_name: Optional[str] = Field(None, description="User's full name")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Account creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Account active status")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "admin@example.com",
                "password_hash": "$2b$12$...",
                "role": "admin",
                "full_name": "John Doe",
                "created_at": "2026-02-06T10:30:00Z",
                "last_login": "2026-02-06T14:00:00Z",
                "is_active": True
            }
        }
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format with PK/SK pattern"""
        return {
            'PK': f'USER#{self.user_id}',
            'SK': f'USER#{self.user_id}',
            'GSI1PK': f'EMAIL#{self.email}',  # For email lookup
            'GSI1SK': f'USER#{self.user_id}',
            'entity_type': 'user',
            'user_id': self.user_id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'User':
        """Create User instance from DynamoDB item"""
        return cls(
            user_id=item['user_id'],
            email=item['email'],
            password_hash=item['password_hash'],
            role=item['role'],
            full_name=item.get('full_name'),
            created_at=item['created_at'],
            last_login=item.get('last_login'),
            is_active=item.get('is_active', True)
        )


class UserCreate(BaseModel):
    """User creation request model"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    role: UserRole
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model (excludes password hash)"""
    user_id: str
    email: EmailStr
    role: UserRole
    full_name: Optional[str]
    created_at: str
    last_login: Optional[str]
    is_active: bool
