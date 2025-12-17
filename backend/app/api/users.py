"""
Users API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, Form, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.get("", response_model=List[UserSchema])
async def get_users(
    role: Optional[str] = None,
    class_name: Optional[str] = None,
    section_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of users"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if class_name:
        query = query.filter(User.class_name == class_name)
    
    if section_name:
        query = query.filter(User.section_name == section_name)
    
    # Students can only see other students
    if current_user.role == 'student':
        query = query.filter(User.role == 'student')
    
    return query.all()


@router.get("/{username}", response_model=UserSchema)
async def get_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by username"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Students can only see other students
    if current_user.role == 'student' and user.role != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return user


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    father_education: Optional[str] = Form(None),
    mother_education: Optional[str] = Form(None),
    class_name: Optional[str] = Form(None),
    section_name: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile with support for file upload"""
    from app.core.utils import allowed_file, secure_filename_arabic
    from app.core.aws import upload_file_to_s3
    from app.config import settings
    from datetime import datetime

    if password:
        current_user.password = get_password_hash(password)
    
    if full_name is not None:
        current_user.full_name = full_name
    
    if address is not None:
        current_user.address = address
    
    if phone_number is not None:
        current_user.phone_number = phone_number
    
    if father_education is not None:
        current_user.father_education = father_education
    
    if mother_education is not None:
        current_user.mother_education = mother_education
    
    if class_name is not None:
        current_user.class_name = class_name
    
    if section_name is not None:
        current_user.section_name = section_name
    
    # Handle Profile Image Upload
    if profile_image:
        # Validate extension
        if not allowed_file(profile_image.filename, settings.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Allowed: png, jpg, jpeg, gif"
            )
        
        # Read content
        file_content = await profile_image.read()
        
        # Generate Key
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        safe_filename = secure_filename_arabic(profile_image.filename)
        s3_key = f"profile_images/{current_user.id}/{timestamp}_{safe_filename}"
        
        # Upload
        content_type = profile_image.content_type or 'image/jpeg'
        if upload_file_to_s3(file_content, s3_key, content_type):
            current_user.profile_image = s3_key
        else:
            raise HTTPException(status_code=500, detail="Failed to upload image")

    # Check if profile is complete
    # Check if profile is complete (Relaxed check: Only Class, Section, and Name are required)
    if all([
        current_user.full_name,
        current_user.class_name,
        current_user.section_name
    ]):
        current_user.is_profile_complete = True
    
    # Clear profile_reset_required if class and section are set
    if current_user.class_name and current_user.section_name:
        current_user.profile_reset_required = False
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

