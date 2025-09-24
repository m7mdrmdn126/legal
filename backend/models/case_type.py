from pydantic import BaseModel, field_validator
from typing import Optional
from .base import BaseModelWithAudit

class CaseTypeBase(BaseModel):
    """Base case type model"""
    name: str
    description: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('اسم نوع القضية يجب أن يكون حرفين على الأقل')
        return v.strip()

class CaseTypeCreate(CaseTypeBase):
    """Case type creation model"""
    pass

class CaseTypeUpdate(BaseModel):
    """Case type update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('اسم نوع القضية يجب أن يكون حرفين على الأقل')
        return v.strip() if v else None

class CaseTypeSimple(BaseModel):
    """Simplified case type for embedding in other responses"""
    id: int
    name: str
    description: Optional[str] = None

class CaseType(BaseModelWithAudit):
    """Case type response model"""
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
