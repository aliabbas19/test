"""
Comments API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.comment import Comment
from app.models.video import Video
from app.schemas.comment import Comment as CommentSchema, CommentCreate, CommentUpdate

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/video/{video_id}")
async def get_video_comments(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comments for a video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    comments = db.query(Comment).filter(Comment.video_id == video_id).order_by(
        Comment.is_pinned.desc(), Comment.timestamp.asc()
    ).all()
    
    # Add user information to comments
    result = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        comment_dict = {
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "video_id": comment.video_id,
            "parent_id": comment.parent_id,
            "timestamp": comment.timestamp,
            "is_pinned": comment.is_pinned,
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else None,
                "full_name": user.full_name if user else None,
                "profile_image": user.profile_image if user else None,
                "role": user.role if user else None
            } if user else None
        }
        result.append(comment_dict)
    
    return result


@router.post("", response_model=CommentSchema)
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new comment"""
    video = db.query(Video).filter(Video.id == comment_data.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    comment = Comment(
        content=comment_data.content,
        user_id=current_user.id,
        video_id=comment_data.video_id,
        parent_id=comment_data.parent_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.put("/{comment_id}", response_model=CommentSchema)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only owner can edit
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if comment_data.content:
        comment.content = comment_data.content
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Owner or admin can delete
    if comment.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(comment)
    db.commit()
    
    return {"status": "success", "message": "Comment deleted"}


@router.post("/{comment_id}/pin")
async def pin_comment(
    comment_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Pin/unpin a comment (admin only)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    comment.is_pinned = not comment.is_pinned
    db.commit()
    
    return {"status": "success", "is_pinned": comment.is_pinned}

