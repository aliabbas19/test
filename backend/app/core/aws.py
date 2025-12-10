"""
AWS S3 and CloudFront integration (with Local Storage Fallback)
"""
import boto3
import os
import shutil
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import Optional
from datetime import timedelta
from app.config import settings

# Check if AWS credentials are provided
HAS_AWS_CREDENTIALS = settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY

# Configure boto3 only if credentials exist
s3_client = None
cloudfront_client = None

if HAS_AWS_CREDENTIALS:
    boto_config = Config(
        region_name=settings.AWS_REGION,
        retries={'max_attempts': 3, 'mode': 'standard'}
    )

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=boto_config
    )

    cloudfront_client = boto3.client(
        'cloudfront',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=boto_config
    )


def upload_file_to_s3(file_content: bytes, s3_key: str, content_type: str) -> bool:
    """
    Upload file to S3 bucket or Local Storage
    """
    if HAS_AWS_CREDENTIALS:
        try:
            s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                ACL='private'
            )
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False
    else:
        # Local Storage Fallback
        try:
            # Construct full local path
            full_path = os.path.join(settings.UPLOAD_FOLDER, s3_key)
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "wb") as f:
                f.write(file_content)
            return True
        except Exception as e:
            print(f"Error saving to local storage: {e}")
            return False


def delete_file_from_s3(s3_key: str) -> bool:
    """Delete file from S3 bucket or Local Storage"""
    if HAS_AWS_CREDENTIALS:
        try:
            s3_client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
    else:
        # Local Storage Fallback
        try:
            full_path = os.path.join(settings.UPLOAD_FOLDER, s3_key)
            if os.path.exists(full_path):
                os.remove(full_path)
            return True
        except Exception as e:
            print(f"Error deleting from local storage: {e}")
            return False


def generate_presigned_url(s3_key: str, expiration: int = 3600) -> Optional[str]:
    """Generate presigned URL for S3 object or return Local Path"""
    if HAS_AWS_CREDENTIALS:
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    else:
        # Local Storage: Return static file path
        # Assuming frontend can access /data/uploads/{s3_key}
        # Note: s3_key usually works as a relative path
        return f"{settings.BACKEND_URL}/data/uploads/{s3_key}"


def get_file_url(s3_key: str, use_cloudfront: bool = True) -> Optional[str]:
    """Get file URL (CloudFront, S3 presigned, or Local)"""
    if HAS_AWS_CREDENTIALS:
        if use_cloudfront and settings.CLOUDFRONT_DOMAIN:
            # Basic CloudFront URL construction
            return f"https://{settings.CLOUDFRONT_DOMAIN}/{s3_key}"
        return generate_presigned_url(s3_key)
    else:
        # Local Storage
        return f"{settings.BACKEND_URL}/data/uploads/{s3_key}"

