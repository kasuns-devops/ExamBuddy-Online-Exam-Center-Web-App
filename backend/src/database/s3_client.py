"""
S3 Client - Handles S3 operations including presigned URLs for ExamBuddy
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Optional, Dict
from src.config import settings


class S3Client:
    """S3 client with helper methods for file operations and presigned URLs"""
    
    def __init__(self):
        """Initialize S3 client with configuration from settings"""
        s3_config = {
            'region_name': settings.aws_region
        }
        
        # Use local endpoint for development (LocalStack)
        if settings.s3_endpoint:
            s3_config['endpoint_url'] = settings.s3_endpoint
            s3_config['aws_access_key_id'] = 'test'
            s3_config['aws_secret_access_key'] = 'test'
        
        self.client = boto3.client('s3', **s3_config)
        self.pdfs_bucket = settings.s3_pdfs_bucket
        self.exports_bucket = settings.s3_exports_bucket
    
    def generate_presigned_upload_url(
        self,
        object_key: str,
        bucket_name: Optional[str] = None,
        expiration: int = 300,
        max_file_size: int = 10 * 1024 * 1024  # 10MB default
    ) -> Dict[str, str]:
        """
        Generate presigned POST URL for direct browser upload to S3
        
        Args:
            object_key: S3 object key (file path)
            bucket_name: S3 bucket name (defaults to pdfs_bucket)
            expiration: URL expiration in seconds (default 5 minutes)
            max_file_size: Maximum file size in bytes (default 10MB)
            
        Returns:
            Dict with 'url' and 'fields' for POST request
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            conditions = [
                {"bucket": bucket},
                ["starts-with", "$key", object_key.split('/')[0] + '/'],
                ["content-length-range", 0, max_file_size]
            ]
            
            response = self.client.generate_presigned_post(
                Bucket=bucket,
                Key=object_key,
                Conditions=conditions,
                ExpiresIn=expiration
            )
            
            return response
        except ClientError as e:
            print(f"Error generating presigned upload URL: {e}")
            raise
    
    def generate_presigned_download_url(
        self,
        object_key: str,
        bucket_name: Optional[str] = None,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned GET URL for downloading a file
        
        Args:
            object_key: S3 object key
            bucket_name: S3 bucket name (defaults to pdfs_bucket)
            expiration: URL expiration in seconds (default 1 hour)
            
        Returns:
            Presigned URL string
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned download URL: {e}")
            raise
    
    async def upload_file(
        self,
        file_data: bytes,
        object_key: str,
        bucket_name: Optional[str] = None,
        content_type: str = 'application/octet-stream'
    ) -> bool:
        """
        Upload file directly to S3 (backend upload)
        
        Args:
            file_data: File content as bytes
            object_key: S3 object key
            bucket_name: S3 bucket name
            content_type: MIME type
            
        Returns:
            bool: True if successful
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=object_key,
                Body=file_data,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            print(f"Error uploading file: {e}")
            raise
    
    async def download_file(
        self,
        object_key: str,
        bucket_name: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Download file from S3
        
        Args:
            object_key: S3 object key
            bucket_name: S3 bucket name
            
        Returns:
            File content as bytes or None if error
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            response = self.client.get_object(
                Bucket=bucket,
                Key=object_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return None
    
    async def delete_file(
        self,
        object_key: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Delete file from S3
        
        Args:
            object_key: S3 object key
            bucket_name: S3 bucket name
            
        Returns:
            bool: True if successful
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            self.client.delete_object(
                Bucket=bucket,
                Key=object_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            raise
    
    async def file_exists(
        self,
        object_key: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Check if file exists in S3
        
        Args:
            object_key: S3 object key
            bucket_name: S3 bucket name
            
        Returns:
            bool: True if file exists
        """
        bucket = bucket_name or self.pdfs_bucket
        
        try:
            self.client.head_object(Bucket=bucket, Key=object_key)
            return True
        except ClientError:
            return False


# Global client instance
s3_client = S3Client()
