"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import TokenData

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    Checks session_revocation_token to ensure session is still valid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # Check session revocation token
    # The token should contain the session_revocation_token at the time it was issued
    token_revocation = payload.get("revocation_token", 0)
    if user.session_revocation_token and user.session_revocation_token > token_revocation:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current active user (not suspended)
    Also checks profile completion for students
    """
    # Check if user is suspended
    from app.models.suspension import Suspension
    from datetime import datetime
    from sqlalchemy import and_
    
    active_suspension = db.query(Suspension).filter(
        and_(
            Suspension.user_id == current_user.id,
            Suspension.end_date > datetime.utcnow()
        )
    ).first()
    
    if active_suspension:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is suspended until {active_suspension.end_date}"
        )
    
    # Check profile completion for students (except for profile update endpoint)
    # This check will be done at the route level where needed
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current admin user
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_student_with_complete_profile(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current student user with completed profile
    Raises exception if profile is not complete or reset is required
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for students only"
        )
    
    if not current_user.is_profile_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile must be completed before accessing this resource"
        )
    
    if current_user.profile_reset_required:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile must be updated for the new school year"
        )
    
    return current_user
