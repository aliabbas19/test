"""
Messages API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.message import Message
from app.schemas.message import Message as MessageSchema, MessageCreate
from app.core.cache import unread_cache

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of conversations"""
    if current_user.role == 'admin':
        # Get all students
        students = db.query(User).filter(User.role == 'student').all()
        return [
            {
                "id": student.id,
                "username": student.username,
                "full_name": student.full_name,
                "class_name": student.class_name,
                "section_name": student.section_name,
                "profile_image": student.profile_image,
                "role": student.role,
                "unread_count": db.query(Message).filter(
                    Message.receiver_id == current_user.id,
                    Message.sender_id == student.id,
                    Message.is_read == False
                ).count()
            }
            for student in students
        ]
    else:
        # Get admin
        admin = db.query(User).filter(User.role == 'admin').first()
        if not admin:
            return []
        
        return [{
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "profile_image": admin.profile_image,
            "role": admin.role,
            "unread_count": db.query(Message).filter(
                Message.receiver_id == current_user.id,
                Message.sender_id == admin.id,
                Message.is_read == False
            ).count()
        }]


@router.get("/{user_id}", response_model=List[MessageSchema])
async def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages with a specific user"""
    # Verify user exists
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get messages between current user and other user
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()
    
    # Mark messages as read
    db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.sender_id == user_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    # Invalidate cache after marking as read
    unread_cache.delete(f"unread_{current_user.id}")
    
    return messages


@router.post("", response_model=MessageSchema)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message"""
    if message_data.type == 'user':
        # Individual message
        if not message_data.receiver_id:
            raise HTTPException(status_code=400, detail="Receiver ID required")
        
        receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")
        
        message = Message(
            sender_id=current_user.id,
            receiver_id=message_data.receiver_id,
            content=message_data.content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Invalidate cache for receiver
        unread_cache.delete(f"unread_{message_data.receiver_id}")
        
        return message
    
    elif message_data.type == 'group':
        # Group message (admin only)
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Only admins can send group messages")
        
        if not message_data.class_name:
            raise HTTPException(status_code=400, detail="Class name required for group messages")
        
        # Get students in class/section
        query = db.query(User).filter(
            User.role == 'student',
            User.class_name == message_data.class_name
        )
        
        if message_data.section_name:
            query = query.filter(User.section_name == message_data.section_name)
        
        students = query.all()
        
        # Create messages for all students
        messages = []
        for student in students:
            msg = Message(
                sender_id=current_user.id,
                receiver_id=student.id,
                content=message_data.content
            )
            db.add(msg)
            messages.append(msg)
        
        db.commit()
        
        return messages[0] if messages else None
    
    else:
        raise HTTPException(status_code=400, detail="Invalid message type")


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get unread message count (with caching)"""
    cache_key = f"unread_{current_user.id}"
    cached_value = unread_cache.get(cache_key)
    if cached_value is not None:
        return {"unread_count": cached_value}
    
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    unread_cache.set(cache_key, count)
    return {"unread_count": count}

