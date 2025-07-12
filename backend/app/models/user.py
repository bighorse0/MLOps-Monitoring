from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import enum
import uuid

from app.core.database import Base

class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    BUSINESS_ANALYST = "business_analyst"
    VIEWER = "viewer"

class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    # Organization and billing
    organization_id = Column(UUID(as_uuid=True), index=True)
    subscription_tier = Column(String(50), default="starter")  # starter, professional, enterprise
    subscription_status = Column(String(50), default="active")  # active, suspended, cancelled
    
    # Stripe billing
    stripe_customer_id = Column(String(255), unique=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    
    # Profile and preferences
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    preferences = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Compliance and audit
    gdpr_consent = Column(Boolean, default=False)
    data_retention_consent = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    @property
    def can_manage_models(self) -> bool:
        """Check if user can manage models"""
        return self.role in [UserRole.ADMIN, UserRole.DATA_SCIENTIST, UserRole.ML_ENGINEER]
    
    @property
    def can_view_metrics(self) -> bool:
        """Check if user can view metrics"""
        return self.role in [UserRole.ADMIN, UserRole.DATA_SCIENTIST, UserRole.ML_ENGINEER, UserRole.BUSINESS_ANALYST]
    
    @property
    def can_generate_reports(self) -> bool:
        """Check if user can generate compliance reports"""
        return self.role in [UserRole.ADMIN, UserRole.DATA_SCIENTIST, UserRole.BUSINESS_ANALYST]
    
    def get_subscription_limits(self) -> dict:
        """Get subscription tier limits"""
        limits = {
            "starter": {"max_models": 10, "max_users": 5, "retention_days": 30},
            "professional": {"max_models": 100, "max_users": 25, "retention_days": 90},
            "enterprise": {"max_models": -1, "max_users": -1, "retention_days": 365}  # -1 = unlimited
        }
        return limits.get(self.subscription_tier, limits["starter"]) 