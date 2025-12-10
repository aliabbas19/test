"""
Device Binding model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DeviceBinding(Base):
    __tablename__ = "device_bindings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_fingerprint = Column(String, nullable=False)  # Hashed fingerprint
    auth_token = Column(String, unique=True, nullable=False, index=True)
    last_used = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="device_bindings")
    
    __table_args__ = (
        Index('idx_device_binding_user', 'user_id'),
        Index('idx_device_binding_token', 'auth_token'),
    )

