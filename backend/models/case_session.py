from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from .base import BaseModelWithAudit

class CaseSessionBase(BaseModel):
    """Base case session model"""
    session_date: Optional[datetime] = None
    session_notes: Optional[str] = None
    
    @field_validator('session_notes')
    @classmethod
    def validate_notes(cls, v):
        if v and len(v.strip()) > 1000:
            raise ValueError('ملاحظات الجلسة لا يجب أن تتجاوز 1000 حرف')
        return v.strip() if v else None

class CaseSessionCreate(CaseSessionBase):
    """Case session creation model"""
    pass

class CaseSessionUpdate(BaseModel):
    """Case session update model"""
    session_date: Optional[datetime] = None
    session_notes: Optional[str] = None
    
    @field_validator('session_notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v.strip()) > 1000:
            raise ValueError('ملاحظات الجلسة لا يجب أن تتجاوز 1000 حرف')
        return v.strip() if v else None

class CaseSession(BaseModelWithAudit):
    """Case session response model"""
    case_id: int
    session_date: Optional[datetime] = None
    session_notes: Optional[str] = None
    
    class Config:
        from_attributes = True
