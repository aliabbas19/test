"""
User model
"""
from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'admin' or 'student'
    profile_image = Column(String, default='default.png')
    class_name = Column(String, index=True)
    section_name = Column(String, index=True)
    session_revocation_token = Column(Integer, default=0)
    
    # Profile information
    full_name = Column(String)
    address = Column(String)
    phone_number = Column(String)
    father_education = Column(String)
    mother_education = Column(String)
    is_profile_complete = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    profile_reset_required = Column(Boolean, default=False)
    
    # Relationships
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    suspensions = relationship("Suspension", back_populates="user", cascade="all, delete-orphan")
    star_bank = relationship("StarBank", back_populates="user", uselist=False, cascade="all, delete-orphan")
    video_ratings = relationship("DynamicVideoRating", back_populates="admin", cascade="all, delete-orphan")
    device_bindings = relationship("DeviceBinding", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_class_section', 'class_name', 'section_name'),
    )
