"""
Phone Directory Models
=====================

Pydantic models for phone directory (دليل التليفونات) feature.
All fields are optional except for audit fields.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class PhoneDirectoryBase(BaseModel):
    """Base phone directory model with Arabic field names"""
    الاسم: Optional[str] = Field(None, description="Name (الاسم)")
    الرقم: Optional[str] = Field(None, description="Phone Number (الرقم)")
    الجهه: Optional[str] = Field(None, description="Organization (الجهه)")
    
    @field_validator('الاسم', mode='before')
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            v = str(v).strip()
            return v if v else None
        return v
    
    @field_validator('الرقم', mode='before')
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            v = str(v).strip()
            return v if v else None
        return v
    
    @field_validator('الجهه', mode='before')
    @classmethod
    def validate_organization(cls, v):
        if v is not None:
            v = str(v).strip()
            return v if v else None
        return v

class PhoneDirectoryCreate(PhoneDirectoryBase):
    """Model for creating phone directory entries"""
    pass

class PhoneDirectoryUpdate(PhoneDirectoryBase):
    """Model for updating phone directory entries"""
    pass

class PhoneDirectoryResponse(PhoneDirectoryBase):
    """Model for phone directory API responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

class PhoneDirectoryListResponse(BaseModel):
    """Model for paginated phone directory list responses"""
    items: list[PhoneDirectoryResponse]
    total: int
    page: int
    size: int
    pages: int

class PhoneDirectorySearchRequest(BaseModel):
    """Model for phone directory search requests"""
    search_term: Optional[str] = Field(None, description="Search in all fields")
    الاسم: Optional[str] = Field(None, description="Search by name")
    الرقم: Optional[str] = Field(None, description="Search by phone number") 
    الجهه: Optional[str] = Field(None, description="Search by organization")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")
    
    @field_validator('search_term', 'الاسم', 'الرقم', 'الجهه', mode='before')
    @classmethod
    def validate_search_fields(cls, v):
        if v is not None:
            v = str(v).strip()
            return v if v else None
        return v
