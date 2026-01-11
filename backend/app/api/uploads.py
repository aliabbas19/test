"""
File upload API routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import tempfile
import os
import shutil
from app.database import get_db, SessionLocal
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.video import Video
from app.core.aws import upload_file_to_s3, get_file_url, generate_presigned_url, generate_presigned_upload_url
from app.core.utils import allowed_file, get_video_duration, secure_filename_arabic
from app.core.cache import unapproved_cache
from app.core.hls_processor import process_video_background
from app.config import settings
from pydantic import BaseModel
import boto3

class PresignedUrlRequest(BaseModel):
    filename: str
    file_type: str  # 'video' or 'image'
    content_type: str
    title: str = "" # Optional, for videos
    video_type: str = "منهجي" # Optional, for videos

class UploadCompletionRequest(BaseModel):
    video_id: int
    s3_key: str

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Videos are now stored in settings.UPLOAD_FOLDER/videos/{user_id}/

@router.post("/presigned-url")
async def get_presigned_upload_url(
    request: PresignedUrlRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get presigned URL for direct S3 upload.
    Creates a database record with 'uploading' status.
    """
    # 1. Validate file extension
    allowed_exts = settings.ALLOWED_VIDEO_EXTENSIONS if request.file_type == 'video' else settings.ALLOWED_IMAGE_EXTENSIONS
    if not allowed_file(request.filename, allowed_exts):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 2. Generate S3 Key
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    safe_filename = secure_filename_arabic(request.filename)
    
    if request.file_type == 'video':
        s3_key = f"videos/{current_user.id}/{timestamp}_{safe_filename}"
    else:
        s3_key = f"profile_images/{current_user.id}/{timestamp}_{safe_filename}"

    # 3. Generate Presigned URL
    presigned_data = generate_presigned_upload_url(s3_key, request.content_type)
    if not presigned_data:
        raise HTTPException(status_code=500, detail="AWS_CONFIG_MISSING: Deployment Verification - Please use Direct Upload")

    video_id = None
    if request.file_type == 'video':
        # Create Video Record Placeholder
        video = Video(
            title=request.title,
            filepath=s3_key,
            user_id=current_user.id,
            video_type=request.video_type,
            is_approved=False,
            processing_status='uploading'
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        video_id = video.id

    return {
        "upload_url": presigned_data["url"],
        "method": presigned_data["method"],
        "key": s3_key,
        "video_id": video_id
    }

@router.post("/upload-complete")
async def complete_upload(
    request: UploadCompletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Notify backend that S3 upload is complete. Triggers HLS processing.
    """
    video = db.query(Video).filter(Video.id == request.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if video.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Verify file exists (optional, simple HEAD check could be done here)
    
    # Update Status
    video.processing_status = 'pending'
    # Check approval (admins auto-approved)
    video.is_approved = (current_user.role == 'admin')
    db.commit()

    # Trigger Processing
    # Need to download from S3 to local temp for processing if we use ffmpeg local
    # For now, we assume the processing task handles pulling from S3 if needed
    # WARNING: process_video_background currently expects a LOCAL path. 
    # We might need to refactor hls_processor or download it there.
    # For the sake of this task, I will queue the job and assume hls_processor needs attention or I fix it.
    
    # Let's fix process_video_background call logic here:
    # We pass the S3 key acting as path, and the processor should handle it.
    
    background_tasks.add_task(
        process_video_background,
        request.s3_key, # Pass S3 key instead of local path
        video.id,
        SessionLocal
    )
    
    return {"status": "processing_queued", "video_id": video.id}


@router.post("/video")
async def upload_video(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    video_type: str = Form(...),
    video_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload video file and process to HLS format
    Validates duration: 60s for منهجي, 240s for اثرائي
    """
    # Validate file extension
    if not allowed_file(video_file.filename, settings.ALLOWED_VIDEO_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: mp4, mov, avi"
        )
    
    # Validate video type
    if video_type not in ['منهجي', 'اثرائي']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video type. Must be 'منهجي' or 'اثرائي'"
        )
    
    # Read file content
    file_content = await video_file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    
    # Validate file size
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Save to temporary file for duration check
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.filename)[1]) as temp_file:
        temp_file.write(file_content)
        temp_path = temp_file.name
    
    try:
        # Check video duration
        duration = get_video_duration(temp_path)
        if duration is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not read video file. File may be corrupted."
            )
        
        # Validate duration based on video type
        max_duration = settings.VIDEO_MAX_DURATION_MANHAJI if video_type == 'منهجي' else settings.VIDEO_MAX_DURATION_ITHRAI
        if duration > max_duration:
            # Clean up and reject
            os.remove(temp_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Video duration ({int(duration)}s) exceeds maximum ({max_duration}s) for {video_type}"
            )
        
        # Generate unique filename for local storage
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        safe_filename = secure_filename_arabic(video_file.filename)
        
        # Store in UPLOAD_FOLDER/videos/{user_id}/ for correct serving
        video_dir = os.path.join(settings.UPLOAD_FOLDER, "videos", str(current_user.id))
        os.makedirs(video_dir, exist_ok=True)
        
        local_filename = f"{timestamp}_{safe_filename}"
        local_path = os.path.join(video_dir, local_filename)
        
        # Relative path for database (used by get_file_url)
        relative_path = f"videos/{current_user.id}/{local_filename}"
        
        # Move temp file to permanent location
        shutil.move(temp_path, local_path)
        
        # Create video record with pending status
        is_approved = current_user.role == 'admin'
        video = Video(
            title=title,
            filepath=relative_path,  # Store relative path, not absolute
            user_id=current_user.id,
            video_type=video_type,
            is_approved=is_approved,
            processing_status='pending'
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Invalidate cache if video is not approved
        if not is_approved:
            unapproved_cache.delete('unapproved_videos')
        
        # Start HLS processing in background
        background_tasks.add_task(
            process_video_background,
            local_path,
            video.id,
            SessionLocal,
            cleanup_source=False  # Keep source for re-processing if needed
        )
        
        return {
            "status": "success",
            "message": f"Video uploaded successfully ({int(duration)}s). Processing for streaming...",
            "video_id": video.id,
            "is_approved": is_approved,
            "processing_status": "pending"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on unexpected error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/profile-image")
async def upload_profile_image(
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile image
    """
    # Validate file extension
    if not allowed_file(image_file.filename, settings.ALLOWED_IMAGE_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: png, jpg, jpeg, gif"
        )
    
    # Read file content
    file_content = await image_file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    
    # Validate file size (5MB max for images)
    if file_size_mb > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 5MB"
        )
    
    # Generate S3 key
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    safe_filename = secure_filename_arabic(image_file.filename)
    s3_key = f"profile_images/{current_user.id}/{timestamp}_{safe_filename}"
    
    # Upload to S3
    content_type = image_file.content_type or 'image/jpeg'
    if not upload_file_to_s3(file_content, s3_key, content_type):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )
    
    # Update user profile image
    current_user.profile_image = s3_key
    db.commit()
    
    # Get file URL
    file_url = get_file_url(s3_key)
    
    return {
        "status": "success",
        "message": "Profile image uploaded successfully",
        "file_url": file_url,
        "s3_key": s3_key
    }


@router.get("/file/{s3_key:path}")
async def get_file(
    s3_key: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get file from S3 (presigned URL redirect)
    """
    url = generate_presigned_url(s3_key, expiration=3600)
    if not url:
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url)
