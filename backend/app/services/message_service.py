"""
Message service - handles messaging logic
"""
from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.user import User


def get_unread_count(db: Session, user_id: int) -> int:
    """Get unread message count for user"""
    return db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()


def mark_messages_as_read(db: Session, user_id: int, sender_id: int):
    """Mark messages from sender as read"""
    db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()

