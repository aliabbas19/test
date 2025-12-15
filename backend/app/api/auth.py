"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from sqlalchemy import and_
from app.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from app.models.user import User
from app.models.suspension import Suspension
from app.schemas.auth import Login, Token, AutoLogin, AutoLoginResponse
from app.core.device import verify_device_binding, bind_device_to_user, get_user_by_token, update_token_last_used
from app.models.device_binding import DeviceBinding
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    Returns access and refresh tokens
    Handles device binding for students
    """
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is suspended
    from app.models.suspension import Suspension
    from datetime import datetime
    from sqlalchemy import and_
    
    active_suspension = db.query(Suspension).filter(
        and_(
            Suspension.user_id == user.id,
            Suspension.end_date > datetime.utcnow()
        )
    ).first()
    
    if active_suspension:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is suspended until {active_suspension.end_date}. Reason: {active_suspension.reason or 'No reason provided'}"
        )
    
    # Handle device binding
    device_fingerprint = login_data.device_fingerprint or ''
    auth_token = None
    
    if user.role == 'admin':
        # Admin: Allow login from any device, create/update token without device binding restriction
        binding = db.query(DeviceBinding).filter(DeviceBinding.user_id == user.id).first()
        if binding:
            auth_token = binding.auth_token
            update_token_last_used(db, auth_token)
        else:
            # Create token for admin (use device_fingerprint if provided, otherwise 'pending')
            fingerprint = device_fingerprint if device_fingerprint else 'pending'
            auth_token = bind_device_to_user(db, user.id, fingerprint)
    else:
        # Student: Enforce device binding (one device only)
        if device_fingerprint:
            is_valid, stored_token = verify_device_binding(db, user.id, device_fingerprint)
            
            if is_valid is False:  # Device exists but doesn't match
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه."
                )
            
            # If no binding exists (first login), create one
            if is_valid is None:
                auth_token = bind_device_to_user(db, user.id, device_fingerprint)
            else:
                auth_token = stored_token
                update_token_last_used(db, auth_token)
        else:
            # If no fingerprint provided, check if account is already bound
            binding = db.query(DeviceBinding).filter(DeviceBinding.user_id == user.id).first()
            if binding:
                # Check if binding is pending (first login case)
                from app.core.device import hash_device_fingerprint
                if binding.device_fingerprint == hash_device_fingerprint('pending'):
                    # Keep existing pending token
                    auth_token = binding.auth_token
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه."
                    )
            else:
                # First login without fingerprint - create binding with pending fingerprint
                auth_token = bind_device_to_user(db, user.id, 'pending')
    
    # Create tokens (include session_revocation_token for session management)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        },
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        }
    )
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    # Also set auth_token cookie for device binding
    if auth_token:
        response.set_cookie(
            key="auth_token",
            value=auth_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=31536000  # 1 year
        )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "auth_token": auth_token,  # Return auth_token to frontend for localStorage backup
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_token: str = None,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Get refresh token from cookie if not provided
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens (include session_revocation_token for session management)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        },
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        }
    )
    
    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Logout endpoint - clears refresh token cookie
    """
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/auto-login", response_model=AutoLoginResponse)
async def auto_login(
    auto_login_data: AutoLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Auto-login endpoint that checks device fingerprint and token
    """
    device_fingerprint = auto_login_data.device_fingerprint
    auth_token = auto_login_data.auth_token
    
    if not device_fingerprint or not auth_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing credentials"
        )
    
    # Get user by token
    user = get_user_by_token(db, auth_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    if user.role == 'admin':
        # Admin can login from any device
        binding = db.query(DeviceBinding).filter(
            DeviceBinding.user_id == user.id,
            DeviceBinding.auth_token == auth_token
        ).first()
        if not binding:
            try:
                auth_token = bind_device_to_user(db, user.id, device_fingerprint)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error creating token: {str(e)}"
                )
    else:
        # For students, verify device fingerprint strictly
        try:
            is_valid, stored_token = verify_device_binding(db, user.id, device_fingerprint)
            if not is_valid or stored_token != auth_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="هذا الحساب مرتبط بجهاز آخر ولا يمكن فتحه."
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying device: {str(e)}"
            )
    
    # Check suspension
    active_suspension = db.query(Suspension).filter(
        and_(
            Suspension.user_id == user.id,
            Suspension.end_date > datetime.utcnow()
        )
    ).first()
    
    if active_suspension:
        end_date_formatted = active_suspension.end_date.strftime('%Y-%m-%d %H:%M:%S')
        reason = active_suspension.reason or 'لا يوجد سبب.'
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"حسابك موقوف حتى {end_date_formatted}. السبب: {reason}"
        )
    
    # Update token last used
    try:
        update_token_last_used(db, auth_token)
    except Exception as e:
        # Log error but don't fail the login
        print(f"Warning: Failed to update token last used: {e}")
    
    # Create JWT tokens (include session_revocation_token for session management)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        },
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={
            "sub": user.username, 
            "user_id": user.id, 
            "role": user.role,
            "revocation_token": user.session_revocation_token or 0
        }
    )
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    # Determine redirect URL
    needs_profile = user.role == 'student' and not user.is_profile_complete
    needs_reset = user.role == 'student' and user.profile_reset_required
    redirect_url = "/"
    if user.role == 'student' and (needs_profile or needs_reset):
        redirect_url = f"/profile/{user.username}"
    
    return {
        "status": "success",
        "redirect": redirect_url,
        "needs_profile": needs_profile,
        "needs_reset": needs_reset,
        "auth_token": auth_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/reset-admin-password")
async def reset_admin_password(
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset admin password - REMOVE IN PRODUCTION or add proper authentication
    """
    admin = db.query(User).filter(
        User.username == 'admin',
        User.role == 'admin'
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المدير غير موجود"
        )
    
    admin.password = get_password_hash(new_password)
    db.commit()
    
    return {
        "status": "success",
        "message": f"تم إعادة تعيين كلمة مرور المدير"
    }
