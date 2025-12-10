"""
Background tasks and scheduled jobs
"""
import logging
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from collections import defaultdict
from app.database import SessionLocal
from app.models.video import Video
from app.config import settings
from app.services.champion_service import get_week_champions
from app.core.telegram import send_telegram_document, get_telegram_settings_from_env
from app.core.pdf_generator import create_champions_pdf
from app.models.telegram_settings import TelegramSettings
import os

# Track last known champions to detect new ones (stored in memory)
_last_known_champions = None
_last_sent_date = None  # Track last date when champions were sent


def auto_archive_videos():
    """
    Auto-archive videos older than VIDEO_ARCHIVE_DAYS
    This should be called by a scheduler (e.g., Celery, APScheduler, or AWS EventBridge)
    """
    db: Session = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=settings.VIDEO_ARCHIVE_DAYS)
        
        # Archive approved videos older than cutoff date
        videos = db.query(Video).filter(
            Video.is_approved == True,
            Video.is_archived == False,
            Video.timestamp < cutoff_date
        ).all()
        
        count = 0
        for video in videos:
            video.is_archived = True
            count += 1
        
        db.commit()
        
        return {
            "status": "success",
            "archived_count": count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()


def send_week_champions_to_telegram():
    """
    Send week champions to Telegram automatically as PDF files grouped by class and section
    """
    logging.info("Starting scheduled send_week_champions_to_telegram task")
    temp_files = []  # Track temporary files for cleanup
    db: Session = SessionLocal()
    
    try:
        # Get Telegram settings
        telegram_settings = db.query(TelegramSettings).first()
        if not telegram_settings or not telegram_settings.bot_token or not telegram_settings.chat_id:
            # Try environment variables
            settings_dict = get_telegram_settings_from_env()
            if not settings_dict:
                logging.warning("Telegram settings not configured, skipping send")
                return  # No settings configured, silently skip
            bot_token = settings_dict['bot_token']
            chat_id = settings_dict['chat_id']
        else:
            bot_token = telegram_settings.bot_token
            chat_id = telegram_settings.chat_id
        
        # Get champions
        champions = get_week_champions(db)
        if not champions:
            logging.info("No champions this week, skipping send")
            return  # No champions this week
        
        # Group champions by class and section
        champions_by_class_section = defaultdict(list)
        for champion in champions:
            class_name = champion.get('class') or 'غير محدد'
            section_name = champion.get('section') or 'غير محدد'
            key = (class_name, section_name)
            champions_by_class_section[key].append(champion)
        
        # Create and send PDF for each class-section group
        sent_count = 0
        for (class_name, section_name), champions_list in champions_by_class_section.items():
            # Create PDF file
            pdf_path = create_champions_pdf(class_name, section_name, champions_list)
            if pdf_path:
                temp_files.append(pdf_path)
                # Create caption for the file
                caption = f"🏆 أبطال الأسبوع\nالصف: {class_name}\nالشعبة: {section_name}"
                # Send PDF to Telegram
                success = send_telegram_document(
                    bot_token, 
                    chat_id, 
                    pdf_path, 
                    caption=caption
                )
                if success:
                    logging.info(f"Successfully sent champions PDF for {class_name} - {section_name}")
                    sent_count += 1
                else:
                    logging.error(f"Failed to send champions PDF for {class_name} - {section_name}")
        
        logging.info(f"Completed sending {sent_count} champion PDFs to Telegram")
        
    except Exception as e:
        logging.error(f"Error in send_week_champions_to_telegram: {e}", exc_info=True)
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logging.error(f"Error deleting temporary file {temp_file}: {e}")
        db.close()


def scheduled_send_champions():
    """
    Wrapper function for scheduled task with proper error handling
    """
    logging.info("Scheduled task triggered: send_week_champions_to_telegram")
    try:
        send_week_champions_to_telegram()
    except Exception as e:
        logging.error(f"Error in scheduled_send_champions: {e}", exc_info=True)


def check_and_send_new_champions():
    """
    Check for new champions and send to Telegram only on Wednesday at 8 PM
    """
    global _last_known_champions, _last_sent_date
    db: Session = SessionLocal()
    
    try:
        current_champions = get_week_champions(db)
        current_ids = {c['id'] for c in current_champions}
        
        # If this is the first run, initialize but don't send
        if _last_known_champions is None:
            _last_known_champions = current_ids
            return
        
        # Get current date and time
        now = datetime.now()
        current_weekday = now.weekday()  # 0=Monday, 1=Tuesday, 2=Wednesday, etc.
        current_hour = now.hour
        current_date = now.date()
        
        # Check if it's Wednesday (2) and 8 PM (20:00)
        is_wednesday_8pm = (current_weekday == 2 and current_hour == 20)
        
        # Only send if:
        # 1. It's Wednesday at 8 PM
        # 2. We haven't sent today yet (to avoid multiple sends on the same day)
        if is_wednesday_8pm and _last_sent_date != current_date:
            # Send all current champions (not just new ones) on Wednesday at 8 PM
            if current_champions:  # Only send if there are champions
                send_week_champions_to_telegram()
                _last_sent_date = current_date  # Mark that we sent today
        
        # Update last known champions
        _last_known_champions = current_ids
    finally:
        db.close()


# For AWS EventBridge or Lambda, you can use:
# def lambda_handler(event, context):
#     return auto_archive_videos()

