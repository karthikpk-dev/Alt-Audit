from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ScanStatus(str, Enum):
    """Enum for scan status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    is_active: Optional[bool] = None

    @validator('username')
    def validate_username(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower() if v else v


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Schema for JWT token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None


# Scan Result Schemas
class ScanResultBase(BaseModel):
    """Base scan result schema."""
    url: str = Field(..., min_length=1, max_length=2048)

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class ScanResultCreate(ScanResultBase):
    """Schema for creating a scan result."""
    pass


class ScanResultUpdate(BaseModel):
    """Schema for updating a scan result."""
    total_images: Optional[int] = Field(None, ge=0)
    images_with_alt: Optional[int] = Field(None, ge=0)
    images_missing_alt: Optional[int] = Field(None, ge=0)
    scan_status: Optional[ScanStatus] = None
    error_message: Optional[str] = None
    scan_duration_ms: Optional[int] = Field(None, ge=0)


class ScanResultResponse(ScanResultBase):
    """Schema for scan result response."""
    id: int
    total_images: int
    images_with_alt: int
    images_missing_alt: int
    scan_status: ScanStatus
    error_message: Optional[str]
    scan_duration_ms: Optional[int]
    alt_text_coverage_percentage: float
    missing_alt_percentage: float
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class ScanResultSummary(BaseModel):
    """Schema for scan result summary (for lists)."""
    id: int
    url: str
    total_images: int
    images_with_alt: int
    images_missing_alt: int
    scan_status: ScanStatus
    alt_text_coverage_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True


# Image Detail Schemas
class ImageDetailBase(BaseModel):
    """Base image detail schema."""
    image_url: str = Field(..., min_length=1, max_length=2048)
    alt_text: Optional[str] = None
    has_alt_text: bool
    alt_text_length: Optional[int] = Field(None, ge=0)
    image_width: Optional[int] = Field(None, ge=0)
    image_height: Optional[int] = Field(None, ge=0)
    is_decorative: bool = False


class ImageDetailCreate(ImageDetailBase):
    """Schema for creating image details."""
    scan_result_id: int


class ImageDetailResponse(ImageDetailBase):
    """Schema for image detail response."""
    id: int
    scan_result_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas
class AnalyticsSummary(BaseModel):
    """Schema for analytics summary."""
    total_scans: int
    total_images_scanned: int
    total_images_with_alt: int
    total_images_missing_alt: int
    average_coverage_percentage: float
    most_common_issues: List[str]
