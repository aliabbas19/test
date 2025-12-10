"""
Ratings API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.models.video import Video
from app.models.rating import RatingCriterion, DynamicVideoRating
from app.schemas.rating import RatingCriterion as RatingCriterionSchema, RatingCriterionCreate, VideoRating, VideoRatingCreate

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


@router.get("/criteria", response_model=List[RatingCriterionSchema])
async def get_criteria(
    video_type: str = None,
    db: Session = Depends(get_db)
):
    """Get rating criteria"""
    query = db.query(RatingCriterion)
    if video_type:
        query = query.filter(RatingCriterion.video_type == video_type)
    return query.all()


@router.post("/criteria", response_model=RatingCriterionSchema)
async def create_criterion(
    criterion_data: RatingCriterionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new rating criterion (admin only)"""
    criterion = RatingCriterion(
        name=criterion_data.name,
        key=criterion_data.key,
        video_type=criterion_data.video_type
    )
    db.add(criterion)
    db.commit()
    db.refresh(criterion)
    
    return criterion


@router.delete("/criteria/{criterion_id}")
async def delete_criterion(
    criterion_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a rating criterion (admin only)"""
    criterion = db.query(RatingCriterion).filter(RatingCriterion.id == criterion_id).first()
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    
    db.delete(criterion)
    db.commit()
    
    return {"status": "success", "message": "Criterion deleted"}


@router.post("/video/{video_id}", response_model=VideoRating)
async def rate_video(
    video_id: int,
    rating_data: VideoRatingCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Rate a video (admin only)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get criteria for video type
    criteria = db.query(RatingCriterion).filter(
        RatingCriterion.video_type == video.video_type
    ).all()
    
    max_stars = len(criteria)
    total_stars = 0
    
    # Update ratings
    for criterion in criteria:
        is_awarded = rating_data.ratings.get(criterion.key, 0)
        if is_awarded == 1:
            total_stars += 1
        
        # Upsert rating
        existing = db.query(DynamicVideoRating).filter(
            DynamicVideoRating.video_id == video_id,
            DynamicVideoRating.criterion_id == criterion.id
        ).first()
        
        if existing:
            existing.is_awarded = is_awarded
            existing.admin_id = current_user.id
        else:
            new_rating = DynamicVideoRating(
                video_id=video_id,
                criterion_id=criterion.id,
                is_awarded=is_awarded,
                admin_id=current_user.id
            )
            db.add(new_rating)
    
    db.commit()
    
    # Check for superhero status (اثرائي with all stars)
    champion_message = None
    if video.video_type == 'اثرائي' and total_stars == max_stars and max_stars > 0:
        champion_message = "أصبح هذا الطالب بطلاً خارقاً!"
    
    return {
        "video_id": video_id,
        "total_stars": total_stars,
        "max_stars": max_stars,
        "ratings": rating_data.ratings
    }


@router.get("/video/{video_id}", response_model=VideoRating)
async def get_video_rating(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Get rating for a video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get criteria
    criteria = db.query(RatingCriterion).filter(
        RatingCriterion.video_type == video.video_type
    ).all()
    
    max_stars = len(criteria)
    total_stars = 0
    ratings_dict = {}
    
    # Get existing ratings
    for criterion in criteria:
        rating = db.query(DynamicVideoRating).filter(
            DynamicVideoRating.video_id == video_id,
            DynamicVideoRating.criterion_id == criterion.id
        ).first()
        
        is_awarded = 1 if rating and rating.is_awarded else 0
        ratings_dict[criterion.key] = is_awarded
        
        if is_awarded:
            total_stars += 1
    
    return {
        "video_id": video_id,
        "total_stars": total_stars,
        "max_stars": max_stars,
        "ratings": ratings_dict
    }

