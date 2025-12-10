"""
Comment schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    video_id: int
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: int
    user_id: int
    video_id: int
    parent_id: Optional[int]
    timestamp: datetime
    is_pinned: bool
    
    class Config:
        from_attributes = True
