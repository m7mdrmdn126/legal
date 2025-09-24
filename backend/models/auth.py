from pydantic import BaseModel
from typing import Optional
from .user import User

class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User

class TokenRefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str

class TokenData(BaseModel):
    """Token payload model"""
    user_id: int
    username: str
    user_type: str
    exp: int
    iat: int
