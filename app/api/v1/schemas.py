"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


# ============= Auth Schemas =============

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class JoinFamily(BaseModel):
    """Join existing family by invite code"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    invite_code: str = Field(..., min_length=6, max_length=6)


class JoinFamilyRequest(BaseModel):
    """Join family request for authenticated users"""
    invite_code: str = Field(..., min_length=6, max_length=6)


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    family_id: str
    invite_code: str


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    family_id: str
    invite_code: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Request password reset"""
    email: EmailStr


class PasswordResetResponse(BaseModel):
    """Password reset response"""
    message: str


# ============= Sync Schemas =============

class SyncPullResponse(BaseModel):
    """Response for pull synchronization"""
    changes: Dict[str, Any]
    timestamp: int


class TableChanges(BaseModel):
    """Changes for a single table"""
    created: List[Dict[str, Any]] = []
    updated: List[Dict[str, Any]] = []
    deleted: List[str] = []


class SyncPushRequest(BaseModel):
    """Request for push synchronization"""
    changes: Dict[str, TableChanges]


# ============= Family Schemas =============

class FamilyDetailsResponse(BaseModel):
    """Detailed family information including members"""
    id: str
    invite_code: str
    owner_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_current_weight: Optional[float] = None
    patient_birth_date: Optional[datetime] = None # Using datetime for simplicity with Pydantic
    members: List[UserResponse]

    class Config:
        from_attributes = True


class RemoveMemberRequest(BaseModel):
    """Request to remove a member from the family"""
    user_id: str


# ============= File Upload Schemas =============

class FileUploadResponse(BaseModel):
    """File upload response"""
    file_url: str
    filename: str
    size: int
