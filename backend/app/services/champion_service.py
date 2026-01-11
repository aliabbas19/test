"""
Champion service - handles superhero/champion logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, Integer
from datetime import date, timedelta, datetime
from typing import Tuple, List, Dict
from app.models.video import Video
from app.models.rating import DynamicVideoRating, RatingCriterion
from app.models.user import User
from app.models.star_bank import StarBank


def get_week_start_date_saturday(d: date = None) -> date:
    """
    Get the start date of the week (Saturday)
    Week starts on Saturday in the original app
    """
    if d is None:
        d = date.today()
    
    # Get day of week (Monday=0, Sunday=6)
    # Saturday = 5
    days_since_saturday = (d.weekday() + 2) % 7
    week_start = d - timedelta(days=days_since_saturday)
    return week_start


def calculate_weekly_stars(db: Session, user_id: int, week_start: date) -> int:
    """
    Calculate stars earned this week for a user from منهجي videos
    """
    from sqlalchemy import func
    
    stars = db.query(func.sum(DynamicVideoRating.is_awarded)).join(
        Video, DynamicVideoRating.video_id == Video.id
    ).join(
        RatingCriterion, DynamicVideoRating.criterion_id == RatingCriterion.id
    ).filter(
        RatingCriterion.video_type == 'منهجي',
        Video.user_id == user_id,
        func.date(Video.timestamp) >= week_start,
        Video.is_approved == True
    ).scalar() or 0
    
    return stars
    
    return stars if stars is not None else 0


def update_star_bank(db: Session, user_id: int, week_start: date, carried_stars: int, new_stars: int) -> StarBank:
    """
    Update star bank for a user
    """
    star_bank = db.query(StarBank).filter(StarBank.user_id == user_id).first()
    
    if star_bank:
        # Update existing
        star_bank.banked_stars = carried_stars + new_stars
        star_bank.last_updated_week_start_date = week_start
    else:
        # Create new
        star_bank = StarBank(
            user_id=user_id,
            banked_stars=carried_stars + new_stars,
            last_updated_week_start_date=week_start
        )
        db.add(star_bank)
    
    db.commit()
    db.refresh(star_bank)
    return star_bank


def get_superhero_champions(db: Session) -> Tuple[list, int]:
    """
    Get superhero champions (اثرائي videos with all stars) for current month
    Returns: (champions_list, max_stars)
    """
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Get all criteria for اثرائي
    criteria_count = db.query(RatingCriterion).filter(
        RatingCriterion.video_type == 'اثرائي'
    ).count()
    
    max_stars = criteria_count
    if max_stars == 0:
        return [], 0
    
    # Get users who have perfect اثرائي videos this month
    # Get users with total stars >= 10 (Accumulated)
    champions_query = db.query(Video.user_id, func.sum(func.cast(DynamicVideoRating.is_awarded, Integer)).label('total_stars')).join(
        DynamicVideoRating, Video.id == DynamicVideoRating.video_id
    ).join(
        RatingCriterion, DynamicVideoRating.criterion_id == RatingCriterion.id
    ).filter(
        RatingCriterion.video_type == 'اثرائي',
        Video.is_approved == True
    ).group_by(
        Video.user_id
    ).having(
        func.sum(func.cast(DynamicVideoRating.is_awarded, Integer)) >= 10
    ).all()
    
    # Get details for these users
    champion_ids = [r.user_id for r in champions_query]
    
    champions = db.query(User).filter(
        User.id.in_(champion_ids)
    ).order_by(User.username).all()
    
    champions_list = [
        {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "profile_image": user.profile_image
        }
        for user in champions
    ]
    
    return champions_list, max_stars


def get_week_champions(db: Session, class_name: str = None, section_name: str = None) -> List[Dict]:
    """
    Get week champions based on star bank
    Week starts on Saturday
    """
    today = date.today()
    start_of_week = get_week_start_date_saturday(today)
    start_of_previous_week = start_of_week - timedelta(days=7)
    
    # Fixed threshold for Methodological Champion = 5 stars
    CHAMPION_THRESHOLD = 5
    
    # Get all students
    query = db.query(User).filter(User.role == 'student')
    if class_name:
        query = query.filter(User.class_name == class_name)
    if section_name:
        query = query.filter(User.section_name == section_name)
    
    students = query.all()
    champions = []
    
    for student in students:
        student_id = student.id
        
        # Get carried stars from previous week
        carried_stars = 0
        bank_entry = db.query(StarBank).filter(
            StarBank.user_id == student_id,
            StarBank.last_updated_week_start_date == start_of_previous_week
        ).first()
        
        if bank_entry:
            carried_stars = bank_entry.banked_stars
        
        # Get new stars this week
        new_stars = calculate_weekly_stars(db, student_id, start_of_week)
        total_score_this_week = carried_stars + new_stars
        
        # Update star bank
        update_star_bank(db, student_id, start_of_week, carried_stars, new_stars)
        
        # Check if champion (total stars >= criteria count)
        if total_score_this_week >= CHAMPION_THRESHOLD:
            champions.append({
                'id': student_id,
                'name': student.full_name or student.username,
                'class': student.class_name or 'غير محدد',
                'section': student.section_name or 'غير محدد',
                'total_stars': total_score_this_week,
                'carried_stars': carried_stars,
                'new_stars': new_stars
            })
    
    return champions


def update_student_star_bank(db: Session, user_id: int):
    """
    Recalculate and update star bank for a specific student (Real-time update)
    """
    today = date.today()
    start_of_week = get_week_start_date_saturday(today)
    start_of_previous_week = start_of_week - timedelta(days=7)
    
    # Get carried stars from previous week
    carried_stars = 0
    bank_entry = db.query(StarBank).filter(
        StarBank.user_id == user_id,
        StarBank.last_updated_week_start_date == start_of_previous_week
    ).first()
    
    if bank_entry:
        carried_stars = bank_entry.banked_stars
    
    # Get new stars this week
    new_stars = calculate_weekly_stars(db, user_id, start_of_week)
    
    # Update star bank
    update_star_bank(db, user_id, start_of_week, carried_stars, new_stars)
    return carried_stars + new_stars
