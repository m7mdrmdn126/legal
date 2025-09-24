from pydantic import BaseModel, field_validator
from typing import Optional
from enum import Enum
from .base import BaseModelWithAudit, UserInfo
from .case_type import CaseTypeSimple

class JudgmentType(str, Enum):
    FIRST = "حكم اول"
    SECOND = "حكم ثان"
    THIRD = "حكم ثالث"

class CaseBase(BaseModel):
    """Base case model"""
    case_number: str
    plaintiff: str
    defendant: str
    case_type_id: int
    judgment_type: JudgmentType
    previous_judgment_id: Optional[int] = None
    
    @field_validator('case_number')
    @classmethod
    def validate_case_number(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('رقم القضية يجب أن يكون 3 أحرف على الأقل')
        return v.strip()
    
    @field_validator('plaintiff')
    @classmethod
    def validate_plaintiff(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('اسم المدعي يجب أن يكون حرفين على الأقل')
        return v.strip()
    
    @field_validator('defendant')
    @classmethod
    def validate_defendant(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('اسم المدعي عليه يجب أن يكون حرفين على الأقل')
        return v.strip()

class CaseCreate(CaseBase):
    """Case creation model"""
    pass

class CaseUpdate(BaseModel):
    """Case update model"""
    case_number: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    case_type_id: Optional[int] = None
    judgment_type: Optional[JudgmentType] = None
    previous_judgment_id: Optional[int] = None
    
    @field_validator('case_number')
    @classmethod
    def validate_case_number(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError('رقم القضية يجب أن يكون 3 أحرف على الأقل')
        return v.strip() if v else None
    
    @field_validator('plaintiff')
    @classmethod
    def validate_plaintiff(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('اسم المدعي يجب أن يكون حرفين على الأقل')
        return v.strip() if v else None
    
    @field_validator('defendant')
    @classmethod
    def validate_defendant(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('اسم المدعي عليه يجب أن يكون حرفين على الأقل')
        return v.strip() if v else None

class Case(BaseModelWithAudit):
    """Case response model"""
    case_number: str
    plaintiff: str
    defendant: str
    case_type_id: int
    case_type: Optional[CaseTypeSimple] = None
    judgment_type: JudgmentType
    previous_judgment_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class CaseWithDetails(Case):
    """Case with related data"""
    sessions_count: int = 0
    notes_count: int = 0
    latest_session: Optional[str] = None
