from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.user import UserRole

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    preferences: Optional[dict] = None

class UserInDB(UserBase):
    """Schema for user in database"""
    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    subscription_tier: str = "starter"
    subscription_status: str = "active"
    is_active: bool = True
    is_verified: bool = False
    preferences: dict = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    gdpr_consent: bool = False
    data_retention_consent: bool = False
    
    class Config:
        from_attributes = True

class User(UserInDB):
    """Schema for user response"""
    pass

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: User

class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    role: Optional[UserRole] = None

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserPreferences(BaseModel):
    """Schema for user preferences"""
    theme: Optional[str] = "light"
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"
    notification_preferences: Optional[dict] = {
        "email": True,
        "slack": False,
        "webhook": False
    }
    dashboard_layout: Optional[dict] = {}
    alert_preferences: Optional[dict] = {
        "drift_alerts": True,
        "performance_alerts": True,
        "compliance_alerts": True
    }

class UserSubscription(BaseModel):
    """Schema for user subscription"""
    tier: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    limits: dict = {
        "max_models": 10,
        "max_users": 5,
        "retention_days": 30
    }
    usage: dict = {
        "models_count": 0,
        "users_count": 0,
        "storage_used_gb": 0.0
    }

class UserList(BaseModel):
    """Schema for user list response"""
    users: List[User]
    total: int
    page: int
    size: int
    pages: int 