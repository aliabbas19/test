"""
Device binding utilities
"""
import secrets
import hashlib
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.device_binding import DeviceBinding


def generate_auth_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def hash_device_fingerprint(fingerprint: str) -> str:
    """Hash device fingerprint for storage"""
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def verify_device_binding(db: Session, user_id: int, device_fingerprint: str) -> Tuple[Optional[bool], Optional[str]]:
    """
    Verify if device fingerprint matches user's bound device
    
    Returns:
        Tuple of (is_valid, auth_token)
        - (True, token) if valid
        - (False, None) if invalid
        - (None, None) if no binding exists (for admin, allows creation)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, None
    
    # Admin can login from any device - skip device binding check
    if user.role == 'admin':
        # For admin, get or create a token but don't enforce device binding
        binding = db.query(DeviceBinding).filter(DeviceBinding.user_id == user_id).first()
        if binding:
            return True, binding.auth_token
        # If no binding exists, return None to create one
        return None, None
    
    # For students, enforce device binding
    binding = db.query(DeviceBinding).filter(DeviceBinding.user_id == user_id).first()
    
    if not binding:
        return None, None
    
    hashed_fingerprint = hash_device_fingerprint(device_fingerprint)
    if binding.device_fingerprint == hashed_fingerprint:
        return True, binding.auth_token
    
    return False, None


def bind_device_to_user(db: Session, user_id: int, device_fingerprint: str) -> str:
    """
    Bind device to user account
    
    Returns:
        auth_token
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    hashed_fingerprint = hash_device_fingerprint(device_fingerprint) if device_fingerprint != 'pending' else hash_device_fingerprint('pending')
    auth_token = generate_auth_token()
    
    # Check if user already has a binding
    existing = db.query(DeviceBinding).filter(DeviceBinding.user_id == user_id).first()
    
    if existing:
        if user.role == 'admin':
            # For admin, just update token and timestamp, keep device_fingerprint as is (allow multiple devices)
            existing.auth_token = auth_token
            # last_used will be updated automatically by onupdate
        else:
            # For students, update device fingerprint (one device only)
            existing.device_fingerprint = hashed_fingerprint
            existing.auth_token = auth_token
    else:
        # Create new binding
        new_binding = DeviceBinding(
            user_id=user_id,
            device_fingerprint=hashed_fingerprint,
            auth_token=auth_token
        )
        db.add(new_binding)
    
    db.commit()
    return auth_token


def unbind_device(db: Session, user_id: int) -> bool:
    """Unbind device from user account (admin only)"""
    bindings = db.query(DeviceBinding).filter(DeviceBinding.user_id == user_id).all()
    for binding in bindings:
        db.delete(binding)
    db.commit()
    return True


def get_user_by_token(db: Session, auth_token: str) -> Optional[User]:
    """Get user by auth token"""
    binding = db.query(DeviceBinding).filter(DeviceBinding.auth_token == auth_token).first()
    
    if binding:
        return binding.user
    
    return None


def update_token_last_used(db: Session, auth_token: str) -> bool:
    """Update last used timestamp for token"""
    binding = db.query(DeviceBinding).filter(DeviceBinding.auth_token == auth_token).first()
    if binding:
        # last_used will be updated automatically by onupdate
        db.commit()
        return True
    return False

