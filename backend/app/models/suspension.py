"""
Suspension model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Suspension(Base):
    __tablename__ = "suspensions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="suspensions")
