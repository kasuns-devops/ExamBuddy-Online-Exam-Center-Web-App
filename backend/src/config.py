"""
Configuration Module - Loads environment variables for ExamBuddy Backend
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # AWS Configuration
    aws_region: str = os.getenv('AWS_REGION', 'us-east-1')
    aws_access_key_id: Optional[str] = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key: Optional[str] = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # DynamoDB
    dynamodb_table_name: str = os.getenv('DYNAMODB_TABLE_NAME', 'exambuddy-main')
    dynamodb_endpoint: Optional[str] = os.getenv('DYNAMODB_ENDPOINT')  # For local testing
    
    # S3 Buckets
    s3_pdfs_bucket: str = os.getenv('S3_PDFS_BUCKET', 'exambuddy-pdfs')
    s3_exports_bucket: str = os.getenv('S3_EXPORTS_BUCKET', 'exambuddy-exports')
    s3_endpoint: Optional[str] = os.getenv('S3_ENDPOINT')  # For local testing
    
    # Cognito
    cognito_user_pool_id: str = os.getenv('COGNITO_USER_POOL_ID', '')
    cognito_client_id: str = os.getenv('COGNITO_CLIENT_ID', '')
    cognito_region: str = os.getenv('COGNITO_REGION', 'us-east-1')
    
    # JWT Secret (fallback for local dev)
    jwt_secret: str = os.getenv('JWT_SECRET', 'insecure-local-dev-secret-change-me')
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 60
    
    # API Configuration
    api_cors_origins: list = os.getenv('API_CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Application
    app_name: str = 'ExamBuddy'
    app_version: str = '1.0.0'
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Global settings instance
settings = Settings()
