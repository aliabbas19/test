"""
Rating models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class RatingCriterion(Base):
    __tablename__ = "rating_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)
    video_type = Column(String, nullable=False)  # 'منهجي' or 'اثرائي'
    
    # Relationships
    ratings = relationship("DynamicVideoRating", back_populates="criterion", cascade="all, delete-orphan")


class DynamicVideoRating(Base):
    __tablename__ = "dynamic_video_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("rating_criteria.id", ondelete="CASCADE"), nullable=False)
    is_awarded = Column(Boolean, default=False)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    video = relationship("Video", back_populates="ratings")
    criterion = relationship("RatingCriterion", back_populates="ratings")
    admin = relationship("User", back_populates="video_ratings")
    
    __table_args__ = (
        UniqueConstraint('video_id', 'criterion_id', name='uq_video_criterion'),
    )
