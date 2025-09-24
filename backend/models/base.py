from pydantic import BaseModel
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    field_errors: Optional[dict] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class UserInfo(BaseModel):
    """User information for responses"""
    id: int
    full_name: str

class BaseModelWithAudit(BaseModel):
    """Base model with audit fields"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UserInfo] = None
    updated_by: Optional[UserInfo] = None
