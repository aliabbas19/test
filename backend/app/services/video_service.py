"""
Video service - handles video-related business logic
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.video import Video
from app.config import settings


def archive_old_videos(db: Session):
    """
    Archive videos older than VIDEO_ARCHIVE_DAYS
    This should be run as a scheduled task
    """
    cutoff_date = datetime.utcnow() - timedelta(days=settings.VIDEO_ARCHIVE_DAYS)
    
    videos = db.query(Video).filter(
        Video.is_archived == False,
        Video.is_approved == True,
        Video.timestamp < cutoff_date
    ).all()
    
    for video in videos:
        video.is_archived = True
    
    db.commit()
    return len(videos)

