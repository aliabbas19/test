"""
Badge model for gamification
Stores user badges: Champion of the Week, Superhero, etc.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserBadge(Base):
    """
    Tracks badges earned by users
    
    Badge Types:
    - superhero: Awarded for getting full marks on an enrichment video (10 stars)
    - weekly_champion: Awarded for collecting 5 methodological stars in a week
    """
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_type = Column(String, nullable=False)  # 'superhero' or 'weekly_champion'
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)  # For superhero badge
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    week_start_date = Column(Date, nullable=True)  # For weekly_champion badge
    month = Column(Integer, nullable=True)  # For superhero (month awarded)
    year = Column(Integer, nullable=True)  # For both badges
    
    # Relationships
    user = relationship("User", backref="badges")
    video = relationship("Video", backref="superhero_badges")
    
    __table_args__ = (
        # Prevent duplicate weekly champion for same week
        UniqueConstraint('user_id', 'badge_type', 'week_start_date', name='uq_weekly_badge'),
    )


class BadgeThreshold(Base):
    """
    Configurable thresholds for badge earning
    """
    __tablename__ = "badge_thresholds"
    
    id = Column(Integer, primary_key=True, index=True)
    badge_type = Column(String, unique=True, nullable=False)
    stars_required = Column(Integer, nullable=False)
    video_type = Column(String, nullable=True)  # 'منهجي' or 'اثرائي' or null for any
    description_ar = Column(String, nullable=True)
    
    # Default values:
    # superhero: 10 stars from a single enrichment video
    # weekly_champion: 5 stars from methodological videos in a week
