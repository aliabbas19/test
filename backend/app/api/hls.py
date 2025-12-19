"""
HLS Streaming API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.video import Video
from app.core.hls_processor import hls_processor

router = APIRouter(prefix="/api/hls", tags=["hls"])


@router.get("/{video_id}/status")
async def get_processing_status(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get video processing status
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check actual file status
    file_status = hls_processor.get_processing_status(video_id)
    
    return {
        "video_id": video_id,
        "processing_status": video.processing_status,
        "hls_path": video.hls_path,
        "thumbnail_path": video.thumbnail_path,
        "file_status": file_status
    }


@router.get("/{video_id}/playlist.m3u8")
async def get_playlist(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get HLS playlist file
    Note: In production, this should be served directly by Nginx
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check if video is accessible
    if not video.is_approved and video.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Video not accessible")
    
    # Check if HLS is ready
    if video.processing_status != 'ready':
        raise HTTPException(
            status_code=202, 
            detail=f"Video is still processing: {video.processing_status}"
        )
    
    playlist_path = hls_processor.get_playlist_path(video_id)
    if not os.path.exists(playlist_path):
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    return FileResponse(
        playlist_path,
        media_type="application/vnd.apple.mpegurl",
        headers={"Cache-Control": "no-cache"}
    )


@router.get("/{video_id}/{segment}")
async def get_segment(
    video_id: int,
    segment: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get HLS segment file (.ts)
    Note: In production, this should be served directly by Nginx
    """
    # Validate segment filename
    if not segment.endswith('.ts') and segment != 'thumbnail.jpg':
        raise HTTPException(status_code=400, detail="Invalid segment request")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check access
    if not video.is_approved and video.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Video not accessible")
    
    segment_path = os.path.join(hls_processor.get_video_output_dir(video_id), segment)
    if not os.path.exists(segment_path):
        raise HTTPException(status_code=404, detail="Segment not found")
    
    media_type = "video/mp2t" if segment.endswith('.ts') else "image/jpeg"
    return FileResponse(segment_path, media_type=media_type)


@router.post("/{video_id}/reprocess")
async def reprocess_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Re-process a video to HLS (admin only)
    Useful if processing failed
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not os.path.exists(video.filepath):
        raise HTTPException(status_code=404, detail="Source video file not found")
    
    # Delete existing HLS files
    hls_processor.delete_hls_files(video_id)
    
    # Reset status
    video.processing_status = 'pending'
    video.hls_path = None
    db.commit()
    
    # Import and start background task
    from fastapi import BackgroundTasks
    from app.database import SessionLocal
    from app.core.hls_processor import process_video_background
    import asyncio
    
    # Run in background
    asyncio.create_task(
        process_video_background(video.filepath, video_id, SessionLocal)
    )
    
    return {"status": "reprocessing", "video_id": video_id}
