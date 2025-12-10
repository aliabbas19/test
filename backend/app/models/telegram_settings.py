"""
Telegram Settings model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class TelegramSettings(Base):
    __tablename__ = "telegram_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_token = Column(String)
    chat_id = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

