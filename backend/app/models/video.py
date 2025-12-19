"""
Video model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    video_type = Column(String, nullable=False)  # 'منهجي' or 'اثرائي'
    is_approved = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False, index=True)
    
    # HLS Streaming fields
    hls_path = Column(String, nullable=True)  # Path to .m3u8 playlist
    processing_status = Column(String, default='pending')  # pending, processing, ready, failed
    thumbnail_path = Column(String, nullable=True)  # Path to thumbnail image
    
    # Relationships
    user = relationship("User", back_populates="videos")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    likes = relationship("VideoLike", back_populates="video", cascade="all, delete-orphan")
    ratings = relationship("DynamicVideoRating", back_populates="video", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_video_user_approved_archived', 'user_id', 'is_approved', 'is_archived'),
    )


class VideoLike(Base):
    __tablename__ = "video_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="likes")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_video_like_unique', 'video_id', 'user_id', unique=True),
    )
