"""
Video schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoBase(BaseModel):
    title: str
    video_type: str  # 'منهجي' or 'اثرائي'


class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    is_approved: Optional[bool] = None
    is_archived: Optional[bool] = None


class Video(VideoBase):
    id: int
    filepath: str
    user_id: int
    timestamp: datetime
    is_approved: bool
    is_archived: bool
    file_url: Optional[str] = None
    ratings: Optional[list] = []
    likes_count: Optional[int] = 0
    user_likes: Optional[bool] = False
    publisher_name: Optional[str] = None
    publisher_image: Optional[str] = None
    
    class Config:
        from_attributes = True

class VideoRating(BaseModel):
    id: int
    criterion_id: int
    criterion_name: str
    is_awarded: bool
    
    class Config:
        from_attributes = True

