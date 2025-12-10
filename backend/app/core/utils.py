"""
Utility functions
"""
from datetime import datetime, date, timedelta
from typing import Optional
import av
import os
from werkzeug.utils import secure_filename


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_video_duration(file_path: str) -> Optional[float]:
    """
    Get video duration in seconds using PyAV
    
    Args:
        file_path: Path to video file
    
    Returns:
        Duration in seconds or None if error
    """
    try:
        with av.open(file_path) as container:
            duration = container.duration / 1000000.0  # Convert microseconds to seconds
            return duration
    except Exception as e:
        print(f"Error reading video duration: {e}")
        return None


def secure_filename_arabic(filename: str) -> str:
    """
    Secure filename while preserving Arabic characters
    """
    # Keep Arabic characters, remove only dangerous characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    filename = ''.join(c if c in safe_chars or ord(c) > 127 else '_' for c in filename)
    return filename


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to string"""
    if dt is None:
        return None
    return dt.isoformat()


def get_week_start_date(d: Optional[date] = None) -> date:
    """
    Get the start date of the week (Friday)
    In Arabic culture, week starts on Friday
    """
    if d is None:
        d = date.today()
    
    # Get day of week (Monday=0, Sunday=6)
    days_since_friday = (d.weekday() + 3) % 7
    week_start = d - timedelta(days=days_since_friday)
    return week_start


def get_week_end_date(d: Optional[date] = None) -> date:
    """Get the end date of the week (Thursday)"""
    week_start = get_week_start_date(d)
    return week_start + timedelta(days=6)
