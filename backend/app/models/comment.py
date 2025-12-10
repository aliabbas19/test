"""
Comment model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_pinned = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    video = relationship("Video", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
