from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        
        if email is None:
            return None
        
        token_data = TokenData(
            email=email,
            user_id=user_id,
            role=role
        )
        return token_data
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = verify_token(token)
        if token_data is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.email == token_data.email).first()
        if user is None:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_user_with_role(required_role: str):
    """Dependency to check user role"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role.value != required_role and current_user.role.value != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

def check_permissions(user: User, required_permissions: list) -> bool:
    """Check if user has required permissions"""
    if user.role.value == "admin":
        return True
    
    user_permissions = {
        "data_scientist": ["manage_models", "view_metrics", "generate_reports"],
        "ml_engineer": ["manage_models", "view_metrics"],
        "business_analyst": ["view_metrics", "generate_reports"],
        "viewer": ["view_metrics"]
    }
    
    user_perms = user_permissions.get(user.role.value, [])
    return all(perm in user_perms for perm in required_permissions)

def require_permissions(required_permissions: list):
    """Decorator to require specific permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not check_permissions(current_user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return permission_checker

def log_security_event(event_type: str, user_id: str, details: dict = None):
    """Log security-related events"""
    logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        details=details or {},
        timestamp=datetime.utcnow().isoformat()
    )

def validate_api_key(api_key: str) -> bool:
    """Validate API key (placeholder for future implementation)"""
    # TODO: Implement API key validation
    return True

def rate_limit_check(user_id: str, endpoint: str) -> bool:
    """Check rate limiting for user and endpoint"""
    # TODO: Implement rate limiting with Redis
    return True 