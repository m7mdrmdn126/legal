from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserBase(BaseModel):
    """Base user model"""
    username: str
    full_name: str
    user_type: UserType = UserType.USER

class UserCreate(UserBase):
    """User creation model"""
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('اسم المستخدم يجب أن يكون 3 أحرف على الأقل')
        return v.lower()

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    user_type: Optional[UserType] = None
    is_active: Optional[bool] = None

class UserPasswordUpdate(BaseModel):
    """User password update model"""
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('كلمة المرور يجب أن تكون 6 أحرف على الأقل')
        return v

class User(UserBase):
    """User response model"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    """User model with password hash for internal use"""
    password_hash: str
