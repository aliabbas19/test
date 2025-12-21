"""
Video API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.video import Video, VideoLike
from app.schemas.video import Video as VideoSchema
from app.core.aws import get_file_url, delete_file_from_s3, generate_presigned_url
from app.core.cache import unapproved_cache
from app.config import settings

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("", response_model=List[VideoSchema])
async def get_videos(
    class_name: Optional[str] = Query(None),
    section_name: Optional[str] = Query(None),
    video_type: Optional[str] = Query(None),
    is_archived: bool = Query(False),
    is_approved: Optional[bool] = Query(None),  # Added filter
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get videos with optional filters
    """
    query = db.query(Video).filter(Video.is_archived == is_archived)
    
    # Only show approved videos to students
    if current_user.role == 'student':
        query = query.filter(Video.is_approved == True)
    
    # Admin filters
    if current_user.role == 'admin':
        if class_name:
            query = query.join(User).filter(User.class_name == class_name)
        if section_name:
            query = query.join(User).filter(User.section_name == section_name)
        # Allow admin to filter by approval status
        if is_approved is not None:
             query = query.filter(Video.is_approved == is_approved)
    
    if video_type:
        query = query.filter(Video.video_type == video_type)
    
    videos = query.order_by(Video.timestamp.desc()).all()
    
    # Add file URLs and likes
    result = []
    for video in videos:
        # Count likes
        likes_count = db.query(VideoLike).filter(VideoLike.video_id == video.id).count()
        # Check if current user liked
        user_likes = db.query(VideoLike).filter(
            VideoLike.video_id == video.id,
            VideoLike.user_id == current_user.id
        ).first() is not None
        
        video_dict = {
            "id": video.id,
            "title": video.title,
            "filepath": video.filepath,
            "file_url": get_file_url(video.filepath),
            "user_id": video.user_id,
            "timestamp": video.timestamp,
            "video_type": video.video_type,
            "is_approved": video.is_approved,
            "is_archived": video.is_archived,
            "likes_count": likes_count,
            "user_likes": user_likes,
            "ratings": [
                {
                    "id": r.id,
                    "criterion_id": r.criterion_id,
                    "criterion_name": r.criterion.name,
                    "is_awarded": r.is_awarded
                }
                for r in video.ratings
            ]
        }
        result.append(video_dict)
    
    return result


@router.get("/{video_id}", response_model=VideoSchema)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get single video by ID
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Students can only see approved videos
    if current_user.role == 'student' and not video.is_approved:
        raise HTTPException(status_code=403, detail="Video not approved")
    
    video_dict = {
        "id": video.id,
        "title": video.title,
        "filepath": video.filepath,
        "file_url": get_file_url(video.filepath),
        "user_id": video.user_id,
        "timestamp": video.timestamp,
        "video_type": video.video_type,
        "is_approved": video.is_approved,
        "is_archived": video.is_archived,
        "ratings": [
            {
                "id": r.id,
                "criterion_id": r.criterion_id,
                "criterion_name": r.criterion.name,
                "is_awarded": r.is_awarded
            }
            for r in video.ratings
        ]
    }
    return video_dict


@router.post("/{video_id}/like")
async def like_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like on video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    existing_like = db.query(VideoLike).filter(
        and_(
            VideoLike.video_id == video_id,
            VideoLike.user_id == current_user.id
        )
    ).first()
    
    if existing_like:
        db.delete(existing_like)
        user_likes = False
    else:
        new_like = VideoLike(video_id=video_id, user_id=current_user.id)
        db.add(new_like)
        user_likes = True
    
    db.commit()
    
    likes_count = db.query(VideoLike).filter(VideoLike.video_id == video_id).count()
    
    return {
        "status": "success",
        "likes_count": likes_count,
        "user_likes": user_likes
    }


@router.post("/{video_id}/approve")
async def approve_video(
    video_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Approve video (admin only)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video.is_approved = True
    db.commit()
    
    # Invalidate cache
    unapproved_cache.delete('unapproved_videos')
    
    return {"status": "success", "message": "Video approved"}


@router.post("/{video_id}/archive")
async def archive_video(
    video_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Archive video (admin only)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not video.is_approved:
        raise HTTPException(status_code=400, detail="Cannot archive unapproved video")
    
    video.is_archived = True
    db.commit()
    
    return {"status": "success", "message": "Video archived"}


@router.post("/{video_id}/unarchive")
async def unarchive_video(
    video_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Unarchive video (admin only)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video.is_archived = False
    db.commit()
    
    return {"status": "success", "message": "Video unarchived"}


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check permissions
    if current_user.role != 'admin' and video.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")
    
    # Delete from S3
    delete_file_from_s3(video.filepath)
    
    # Delete from database (cascade will handle related records)
    db.delete(video)
    db.commit()
    
    return {"status": "success", "message": "Video deleted"}


@router.put("/{video_id}")
async def update_video(
    video_id: int,
    title: Optional[str] = None,
    video_type: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update video details (admin only)
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Update fields if provided
    if title is not None:
        video.title = title
    if video_type is not None:
        if video_type not in ['منهجي', 'اثرائي']:
            raise HTTPException(status_code=400, detail="نوع الفيديو يجب أن يكون 'منهجي' أو 'اثرائي'")
        video.video_type = video_type
    
    db.commit()
    db.refresh(video)
    
    return {
        "status": "success",
        "message": "تم تحديث الفيديو بنجاح",
        "video": {
            "id": video.id,
            "title": video.title,
            "video_type": video.video_type
        }
    }
