"""
Star Bank model
"""
from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class StarBank(Base):
    __tablename__ = "star_bank"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    banked_stars = Column(Integer, nullable=False, default=0)
    last_updated_week_start_date = Column(Date, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="star_bank")

