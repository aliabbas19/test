"""
Authentication schemas
"""
from pydantic import BaseModel
from typing import Optional


class Login(BaseModel):
    username: str
    password: str
    device_fingerprint: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class AutoLogin(BaseModel):
    device_fingerprint: str
    auth_token: str


class AutoLoginResponse(BaseModel):
    status: str
    redirect: Optional[str] = None
    needs_profile: bool = False
    needs_reset: bool = False
    auth_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    # Add auth_token to allow returning it in login response to handle HttpOnly cookie limitation
    token_type: str = "bearer"
    message: Optional[str] = None
