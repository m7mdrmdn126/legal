from pydantic import BaseModel, field_validator
from typing import Optional
from .base import BaseModelWithAudit

class CaseNoteBase(BaseModel):
    """Base case note model"""
    note_text: str
    
    @field_validator('note_text')
    @classmethod
    def validate_note_text(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError('نص الملاحظة يجب أن يكون 5 أحرف على الأقل')
        if len(v.strip()) > 2000:
            raise ValueError('نص الملاحظة لا يجب أن يتجاوز 2000 حرف')
        return v.strip()

class CaseNoteCreate(CaseNoteBase):
    """Case note creation model"""
    pass

class CaseNoteUpdate(BaseModel):
    """Case note update model"""
    note_text: Optional[str] = None
    
    @field_validator('note_text')
    @classmethod
    def validate_note_text(cls, v):
        if v is not None:
            if len(v.strip()) < 5:
                raise ValueError('نص الملاحظة يجب أن يكون 5 أحرف على الأقل')
            if len(v.strip()) > 2000:
                raise ValueError('نص الملاحظة لا يجب أن يتجاوز 2000 حرف')
            return v.strip()
        return None

class CaseNote(BaseModelWithAudit):
    """Case note response model"""
    case_id: int
    note_text: str
    
    class Config:
        from_attributes = True
