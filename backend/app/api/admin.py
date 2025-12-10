"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.models.video import Video
from app.models.message import Message
from app.models.suspension import Suspension
from app.models.rating import RatingCriterion
from app.schemas.user import UserCreate
from app.services.champion_service import get_superhero_champions
from app.core.security import get_password_hash
from app.core.telegram import send_telegram_message, send_telegram_document, get_telegram_settings_from_env
from app.core.pdf_generator import create_champions_pdf
from app.core.device import unbind_device
from app.core.aws import delete_file_from_s3
from app.core.cache import unapproved_cache
from app.models.telegram_settings import TelegramSettings
from app.models.device_binding import DeviceBinding
from app.models.comment import Comment
from app.models.video import VideoLike
from app.models.rating import DynamicVideoRating
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import and_
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics (with caching for pending videos)"""
    total_students = db.query(User).filter(User.role == 'student').count()
    
    # Use cache for pending videos count
    cache_key = 'unapproved_videos'
    cached_value = unapproved_cache.get(cache_key)
    if cached_value is not None:
        pending_videos = cached_value
    else:
        pending_videos = db.query(Video).filter(Video.is_approved == False).count()
        unapproved_cache.set(cache_key, pending_videos)
    
    unread_messages = db.query(Message).filter(Message.is_read == False).count()
    
    return {
        "total_students": total_students,
        "pending_videos": pending_videos,
        "unread_messages": unread_messages
    }


@router.get("/ops/metrics")
async def get_ops_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """Return recent performance metrics (admin only)"""
    from app.core.metrics import request_metrics
    return request_metrics.snapshot()


@router.get("/champions")
async def get_champions(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get superhero champions for current month"""
    champions, max_stars = get_superhero_champions(db)
    return {
        "champions": champions,
        "max_stars": max_stars
    }


@router.post("/users")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    # Check if username exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        role=user_data.role,
        class_name=user_data.class_name,
        section_name=user_data.section_name,
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "message": "User created successfully"
    }


@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    days: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Suspend a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == 'admin':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend admin users"
        )
    
    end_date = datetime.utcnow() + timedelta(days=days)
    
    # Check if user already has an active suspension
    active_suspension = db.query(Suspension).filter(
        Suspension.user_id == user_id,
        Suspension.end_date > datetime.utcnow()
    ).first()
    
    if active_suspension:
        # Update existing suspension
        active_suspension.end_date = end_date
        if reason:
            active_suspension.reason = reason
    else:
        # Create new suspension
        suspension = Suspension(
            user_id=user_id,
            end_date=end_date,
            reason=reason
        )
        db.add(suspension)
    
    db.commit()
    
    return {
        "message": f"User suspended for {days} days",
        "end_date": end_date.isoformat()
    }


@router.get("/reports/students")
async def get_students_report(
    class_name: Optional[str] = None,
    section_name: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get students report"""
    query = db.query(User).filter(User.role == 'student')
    
    if class_name:
        query = query.filter(User.class_name == class_name)
    if section_name:
        query = query.filter(User.section_name == section_name)
    
    students = query.all()
    
    return [
        {
            "id": s.id,
            "username": s.username,
            "full_name": s.full_name,
            "class_name": s.class_name,
            "section_name": s.section_name,
            "profile_image": s.profile_image
        }
        for s in students
    ]


@router.post("/telegram/send-champions")
async def send_champions_telegram(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Send champions report to Telegram with PDF (admin only)"""
    
    # Get Telegram settings
    telegram_settings = db.query(TelegramSettings).first()
    if not telegram_settings or not telegram_settings.bot_token or not telegram_settings.chat_id:
        # Try environment variables
        settings_dict = get_telegram_settings_from_env()
        if not settings_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="إعدادات تيليجرام غير موجودة. يرجى إعداد bot_token و chat_id أولاً."
            )
        bot_token = settings_dict['bot_token']
        chat_id = settings_dict['chat_id']
    else:
        bot_token = telegram_settings.bot_token
        chat_id = telegram_settings.chat_id
    
    # Get champions (superhero champions for current month)
    champions, max_stars = get_superhero_champions(db)
    
    if not champions:
        return {
            "status": "info",
            "message": "لا يوجد أبطال هذا الشهر لإرسالهم"
        }
    
    # Group champions by class and section
    champions_by_class_section = defaultdict(list)
    for champion in champions:
        # Get user details
        user = db.query(User).filter(User.id == champion['id']).first()
        if user:
            key = (user.class_name or 'غير محدد', user.section_name or 'غير محدد')
            champions_by_class_section[key].append({
                'name': user.full_name or user.username
            })
    
    # Create and send PDF for each class-section group
    temp_files = []
    sent_count = 0
    
    try:
        for (class_name, section_name), champions_list in champions_by_class_section.items():
            # Create PDF file
            pdf_path = create_champions_pdf(class_name, section_name, champions_list)
            if pdf_path:
                temp_files.append(pdf_path)
                # Create caption for the file
                caption = f"🏆 أبطال الشهر\nالصف: {class_name}\nالشعبة: {section_name}"
                # Send PDF to Telegram
                success = send_telegram_document(bot_token, chat_id, pdf_path, caption=caption)
                if success:
                    sent_count += 1
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error deleting temporary file {temp_file}: {e}")
    
    if sent_count > 0:
        return {
            "status": "success",
            "message": f"تم إرسال {sent_count} تقرير PDF إلى تيليجرام بنجاح"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="حدث خطأ أثناء الإرسال إلى تيليجرام"
        )


@router.post("/telegram/settings")
async def update_telegram_settings(
    bot_token: str,
    chat_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update Telegram settings (admin only)"""
    settings = db.query(TelegramSettings).first()
    
    if settings:
        settings.bot_token = bot_token
        settings.chat_id = chat_id
    else:
        settings = TelegramSettings(
            bot_token=bot_token,
            chat_id=chat_id
        )
        db.add(settings)
    
    db.commit()
    
    return {
        "status": "success",
        "message": "تم تحديث إعدادات تيليجرام بنجاح"
    }


@router.get("/telegram/settings")
async def get_telegram_settings(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get Telegram settings (admin only)"""
    settings = db.query(TelegramSettings).first()
    
    if settings:
        return {
            "bot_token": settings.bot_token,
            "chat_id": settings.chat_id,
            "updated_at": settings.updated_at.isoformat() if settings.updated_at else None
        }
    
    # Check environment variables
    env_settings = get_telegram_settings_from_env()
    if env_settings:
        return {
            "bot_token": "***configured***",
            "chat_id": "***configured***",
            "source": "environment"
        }
    
    return {
        "bot_token": None,
        "chat_id": None
    }


@router.post("/start-new-year")
async def start_new_year(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Start new school year - marks all students as needing profile reset
    WARNING: This is a destructive operation
    """
    # Mark all students as needing profile reset
    students = db.query(User).filter(User.role == 'student').all()
    
    for student in students:
        student.profile_reset_required = True
        # Optionally clear class and section
        # student.class_name = None
        # student.section_name = None
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"تم بدء سنة دراسية جديدة. {len(students)} طالب يحتاجون لتحديث ملفاتهم الشخصية."
    }


@router.post("/users/{user_id}/mute")
async def toggle_mute(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle mute status for a student"""
    student = db.query(User).filter(User.id == user_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.is_muted = not student.is_muted
    db.commit()
    
    return {
        "status": "success",
        "message": f"تم تحديث حالة الكتم للطالب بنجاح",
        "is_muted": student.is_muted
    }


@router.post("/users/{user_id}/kick")
async def kick_student(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Kick student - revoke all sessions by incrementing session_revocation_token"""
    student = db.query(User).filter(User.id == user_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.session_revocation_token = (student.session_revocation_token or 0) + 1
    db.commit()
    
    return {
        "status": "success",
        "message": "تم طرد الطالب."
    }


@router.post("/users/{user_id}/lift-suspension")
async def lift_suspension(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Lift suspension from a student"""
    student = db.query(User).filter(User.id == user_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Delete all suspensions for this user
    db.query(Suspension).filter(Suspension.user_id == user_id).delete()
    db.commit()
    
    return {
        "status": "success",
        "message": "تم رفع الإيقاف عن الطالب."
    }


@router.post("/users/{user_id}/unbind-device")
async def unbind_user_device(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Unbind device from user account (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    unbind_device(db, user_id)
    
    return {
        "status": "success",
        "message": "تم إلغاء ربط الجهاز بنجاح"
    }


@router.post("/users/{user_id}/revoke-sessions")
async def revoke_sessions(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke all user sessions by incrementing session_revocation_token"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.session_revocation_token = (user.session_revocation_token or 0) + 1
    db.commit()
    
    return {
        "status": "success",
        "message": "تم إبطال جميع الجلسات بنجاح"
    }


@router.delete("/users/{user_id}")
async def delete_student(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete student account with all associated data"""
    student = db.query(User).filter(User.id == user_id, User.role == 'student').first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # 1. Delete all videos and their files
        videos = db.query(Video).filter(Video.user_id == user_id).all()
        for video in videos:
            # Delete comments on this video
            db.query(Comment).filter(Comment.video_id == video.id).delete()
            # Delete likes on this video
            db.query(VideoLike).filter(VideoLike.video_id == video.id).delete()
            # Delete ratings on this video
            db.query(DynamicVideoRating).filter(DynamicVideoRating.video_id == video.id).delete()
            # Delete video file from S3
            if video.filepath:
                delete_file_from_s3(video.filepath)
        
        # Delete videos from database
        db.query(Video).filter(Video.user_id == user_id).delete()
        
        # 2. Delete comments made by student
        db.query(Comment).filter(Comment.user_id == user_id).delete()
        
        # 3. Delete likes made by student
        db.query(VideoLike).filter(VideoLike.user_id == user_id).delete()
        
        # 4. Delete messages
        from app.models.message import Message
        db.query(Message).filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).delete()
        
        # 5. Delete suspensions
        db.query(Suspension).filter(Suspension.user_id == user_id).delete()
        
        # 6. Delete device bindings
        db.query(DeviceBinding).filter(DeviceBinding.user_id == user_id).delete()
        
        # 7. Delete posts
        from app.models.post import Post
        db.query(Post).filter(Post.user_id == user_id).delete()
        
        # 8. Delete profile image from S3 (if not default)
        if student.profile_image and student.profile_image != 'default.png':
            delete_file_from_s3(student.profile_image)
        
        # 9. Delete star bank
        from app.models.star_bank import StarBank
        db.query(StarBank).filter(StarBank.user_id == user_id).delete()
        
        # 10. Delete student account
        db.delete(student)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "تم حذف حساب الطالب بنجاح"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"حدث خطأ أثناء حذف الحساب: {str(e)}"
        )

