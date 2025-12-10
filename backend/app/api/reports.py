"""
Reports API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List, Dict
from datetime import datetime, timedelta, date
from collections import defaultdict
from app.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.models.video import Video
from app.models.comment import Comment
from app.models.rating import RatingCriterion, DynamicVideoRating

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_week_start_date():
    """Get start date of current week (Monday)"""
    today = date.today()
    days_since_monday = today.weekday()
    return today - timedelta(days=days_since_monday)


@router.get("/students")
async def get_students_report(
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed student activity reports"""
    # Get all classes
    all_classes = db.query(User.class_name).filter(
        User.role == 'student',
        User.class_name.isnot(None),
        User.class_name != ''
    ).distinct().all()
    
    # Get students
    query = db.query(User).filter(User.role == 'student')
    if class_name:
        query = query.filter(User.class_name == class_name)
    
    students = query.order_by(User.username).all()
    
    # Get all criteria
    all_criteria = db.query(RatingCriterion).all()
    criteria_by_type = defaultdict(list)
    for criterion in all_criteria:
        criteria_by_type[criterion.video_type].append({
            'id': criterion.id,
            'name': criterion.name,
            'key': criterion.key,
            'video_type': criterion.video_type
        })
    
    # Get all student video IDs
    student_ids = [s.id for s in students]
    if not student_ids:
        return {
            'all_classes': [c[0] for c in all_classes],
            'selected_class': class_name,
            'report_data': []
        }
    
    # Get all videos for these students
    videos = db.query(Video).filter(
        Video.user_id.in_(student_ids),
        Video.is_approved == True
    ).all()
    
    videos_by_student = defaultdict(lambda: defaultdict(list))
    video_ids = []
    for video in videos:
        videos_by_student[video.user_id][video.video_type].append({
            'id': video.id,
            'title': video.title,
            'timestamp': video.timestamp.isoformat(),
            'video_type': video.video_type
        })
        video_ids.append(video.id)
    
    # Get all ratings for these videos
    all_ratings = {}
    if video_ids:
        ratings = db.query(DynamicVideoRating, RatingCriterion).join(
            RatingCriterion, DynamicVideoRating.criterion_id == RatingCriterion.id
        ).filter(DynamicVideoRating.video_id.in_(video_ids)).all()
        
        for rating, criterion in ratings:
            video_id = rating.video_id
            if video_id not in all_ratings:
                all_ratings[video_id] = {'total_stars': 0, 'ratings': {}}
            
            all_ratings[video_id]['ratings'][criterion.key] = 1 if rating.is_awarded else 0
            if rating.is_awarded:
                all_ratings[video_id]['total_stars'] += 1
    
    # Get week start date
    week_start = get_week_start_date()
    week_start_dt = datetime.combine(week_start, datetime.min.time())
    
    # Get champion statuses (simplified - would need full champion logic)
    champion_statuses = {}
    
    # Build report data
    report_data = []
    for student in students:
        student_id = student.id
        
        # Get videos with ratings
        videos_manhaji = []
        for video in videos_by_student[student_id]['منهجي']:
            video_data = video.copy()
            video_ratings = all_ratings.get(video['id'], {'total_stars': 0, 'ratings': {}})
            video_data.update(video_ratings)
            videos_manhaji.append(video_data)
        
        videos_ithrai = []
        for video in videos_by_student[student_id]['اثرائي']:
            video_data = video.copy()
            video_ratings = all_ratings.get(video['id'], {'total_stars': 0, 'ratings': {}})
            video_data.update(video_ratings)
            videos_ithrai.append(video_data)
        
        # Get weekly activity
        weekly_uploads = db.query(func.count(Video.id)).filter(
            Video.user_id == student_id,
            Video.timestamp >= week_start_dt
        ).scalar() or 0
        
        weekly_comments = db.query(func.count(Comment.id)).filter(
            Comment.user_id == student_id,
            Comment.timestamp >= week_start_dt
        ).scalar() or 0
        
        # Check if champion (simplified)
        is_champion = champion_statuses.get(student_id) == 'بطل الأسبوع'
        
        report_data.append({
            'id': student.id,
            'username': student.username,
            'full_name': student.full_name,
            'class_name': student.class_name,
            'section_name': student.section_name,
            'videos_manhaji': videos_manhaji,
            'videos_ithrai': videos_ithrai,
            'weekly_activity': {
                'uploads': weekly_uploads,
                'comments': weekly_comments,
                'is_champion': is_champion
            }
        })
    
    return {
        'all_classes': [c[0] for c in all_classes],
        'selected_class': class_name,
        'all_criteria': dict(criteria_by_type),
        'report_data': report_data
    }

