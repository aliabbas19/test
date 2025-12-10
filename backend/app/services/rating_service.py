"""
Rating service - handles rating calculations
"""
from sqlalchemy.orm import Session
from app.models.video import Video
from app.models.rating import DynamicVideoRating, RatingCriterion


def calculate_video_rating(db: Session, video_id: int) -> dict:
    """
    Calculate total stars and max stars for a video
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return {"total_stars": 0, "max_stars": 0}
    
    # Get criteria for video type
    criteria = db.query(RatingCriterion).filter(
        RatingCriterion.video_type == video.video_type
    ).all()
    
    max_stars = len(criteria)
    
    # Count awarded stars
    total_stars = db.query(DynamicVideoRating).filter(
        DynamicVideoRating.video_id == video_id,
        DynamicVideoRating.is_awarded == True
    ).count()
    
    return {
        "total_stars": total_stars,
        "max_stars": max_stars
    }

