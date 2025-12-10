"""
Message schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str


class MessageCreate(MessageBase):
    receiver_id: Optional[int] = None
    type: Optional[str] = None  # 'user' or 'group'
    class_name: Optional[str] = None
    section_name: Optional[str] = None


class Message(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    timestamp: datetime
    is_read: bool
    
    class Config:
        from_attributes = True
