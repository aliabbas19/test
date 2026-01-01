"""
Posts API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.post import Post
from pydantic import BaseModel

router = APIRouter(prefix="/api/posts", tags=["posts"])


class PostCreate(BaseModel):
    content: str


class PostResponse(BaseModel):
    id: int
    content: str
    user_id: int
    timestamp: str
    username: str
    full_name: str | None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[PostResponse])
async def get_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts (admin posts only)"""
    posts = db.query(Post).join(User).filter(
        User.role == 'admin'
    ).order_by(Post.timestamp.desc()).all()
    
    result = []
    for post in posts:
        result.append({
            "id": post.id,
            "content": post.content,
            "user_id": post.user_id,
            "timestamp": post.timestamp.isoformat(),
            "username": post.user.username,
            "full_name": post.user.full_name
        })
    
    return result


@router.post("", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new post (admin only)"""
    if not post_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty"
        )
    
    post = Post(
        content=post_data.content,
        user_id=current_user.id
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "content": post.content,
        "user_id": post.user_id,
        "timestamp": post.timestamp.isoformat(),
        "username": current_user.username,
        "full_name": current_user.full_name
    }


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a post (admin only)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only allow deleting own posts or any admin can delete
    if post.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    db.delete(post)
    db.commit()
    
    return {"status": "success", "message": "Post deleted"}


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a post (admin only)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not post_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty"
        )
    
    # Update content
    post.content = post_data.content
    
    db.commit()
    db.refresh(post)
    
    return {
        "id": post.id,
        "content": post.content,
        "user_id": post.user_id,
        "timestamp": post.timestamp.isoformat(),
        "username": post.user.username,
        "full_name": post.user.full_name
    }
