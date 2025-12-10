"""
User schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    role: str
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    section_name: Optional[str] = None
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    father_education: Optional[str] = None
    mother_education: Optional[str] = None
    class_name: Optional[str] = None
    section_name: Optional[str] = None
    profile_image: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_profile_complete: bool
    is_muted: bool
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass
