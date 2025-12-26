"""
Badges API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer
from typing import List, Optional
from datetime import date, timedelta
from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.badge import UserBadge
from app.models.video import Video
from app.models.rating import DynamicVideoRating, RatingCriterion
from app.models.star_bank import StarBank
from app.services.champion_service import get_week_start_date_saturday, calculate_weekly_stars

router = APIRouter(prefix="/api/badges", tags=["badges"])


@router.get("/user/{user_id}")
async def get_user_badges(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get badges and star info for a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get badges
    badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    
    # Get current week info
    week_start = get_week_start_date_saturday()
    
    # Get star bank
    star_bank = db.query(StarBank).filter(StarBank.user_id == user_id).first()
    banked_stars = star_bank.banked_stars if star_bank else 0
    
    # Get weekly stars (منهجي only)
    weekly_stars = calculate_weekly_stars(db, user_id, week_start)
    
    # Get total stars from all rated videos
    total_manhaji_stars = db.query(func.sum(func.cast(DynamicVideoRating.is_awarded, Integer))).join(
        Video, DynamicVideoRating.video_id == Video.id
    ).join(
        RatingCriterion, DynamicVideoRating.criterion_id == RatingCriterion.id
    ).filter(
        RatingCriterion.video_type == 'منهجي',
        Video.user_id == user_id,
        Video.is_approved == True
    ).scalar() or 0
    
    total_ithrai_stars = db.query(func.sum(func.cast(DynamicVideoRating.is_awarded, Integer))).join(
        Video, DynamicVideoRating.video_id == Video.id
    ).join(
        RatingCriterion, DynamicVideoRating.criterion_id == RatingCriterion.id
    ).filter(
        RatingCriterion.video_type == 'اثرائي',
        Video.user_id == user_id,
        Video.is_approved == True
    ).scalar() or 0
    
    # Count badges by type
    superhero_count = sum(1 for b in badges if b.badge_type == 'superhero')
    champion_count = sum(1 for b in badges if b.badge_type == 'weekly_champion')
    
    # Check if currently champion this week
    is_champion_this_week = any(
        b.badge_type == 'weekly_champion' and b.week_start_date == week_start
        for b in badges
    )
    
    return {
        "user_id": user_id,
        "badges": [
            {
                "id": b.id,
                "type": b.badge_type,
                "awarded_at": b.awarded_at,
                "week_start_date": b.week_start_date,
                "video_id": b.video_id
            }
            for b in badges
        ],
        "stats": {
            "total_manhaji_stars": total_manhaji_stars,
            "total_ithrai_stars": total_ithrai_stars,
            "weekly_stars": weekly_stars,
            "banked_stars": banked_stars,
            "total_stars": total_manhaji_stars + total_ithrai_stars,
            "superhero_count": superhero_count,
            "champion_count": champion_count,
            "is_champion_this_week": is_champion_this_week,
            "stars_to_champion": max(0, 5 - (banked_stars + weekly_stars))
        }
    }


@router.get("/champions")
async def get_current_champions(
    class_name: Optional[str] = None,
    section_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current week champions"""
    from app.services.champion_service import get_week_champions, get_superhero_champions
    
    week_champions = get_week_champions(db, class_name, section_name)
    superheroes, max_stars = get_superhero_champions(db)
    
    return {
        "week_champions": week_champions,
        "superheroes": superheroes,
        "week_start": get_week_start_date_saturday()
    }


@router.get("/leaderboard")
async def get_leaderboard(
    class_name: Optional[str] = None,
    section_name: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get star leaderboard"""
    # Query total stars per user
    query = db.query(
        Video.user_id,
        func.sum(func.cast(DynamicVideoRating.is_awarded, Integer)).label('total_stars')
    ).join(
        DynamicVideoRating, Video.id == DynamicVideoRating.video_id
    ).filter(
        Video.is_approved == True
    ).group_by(
        Video.user_id
    ).order_by(
        func.sum(func.cast(DynamicVideoRating.is_awarded, Integer)).desc()
    )
    
    results = query.limit(limit).all()
    
    # Get user details
    leaderboard = []
    for rank, (user_id, total_stars) in enumerate(results, 1):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Apply filters if provided
            if class_name and user.class_name != class_name:
                continue
            if section_name and user.section_name != section_name:
                continue
            
            leaderboard.append({
                "rank": rank,
                "user_id": user_id,
                "username": user.username,
                "full_name": user.full_name,
                "class_name": user.class_name,
                "section_name": user.section_name,
                "total_stars": total_stars or 0,
                "profile_image": user.profile_image
            })
    
    return leaderboard
