from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password
)
from app.schemas.user import (
    User,
    UserCreate,
    UserLogin,
    UserLoginResponse,
    Token,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm
)
from app.models.user import User as UserModel

logger = structlog.get_logger()
router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.query(UserModel).filter(
        UserModel.email == user_in.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    existing_username = db.query(UserModel).filter(
        UserModel.username == user_in.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = UserModel(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info("New user registered", user_id=str(db_user.id), email=db_user.email)
    
    return db_user

@router.post("/login", response_model=UserLoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
    )
    
    # Update last login
    user.last_login = db.query(UserModel).filter(UserModel.id == user.id).first().created_at
    db.commit()
    
    logger.info("User logged in", user_id=str(user.id), email=user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login/email", response_model=UserLoginResponse)
async def login_with_email(
    user_in: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with email and password.
    """
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "role": user.role.value}
    )
    
    # Update last login
    user.last_login = db.query(UserModel).filter(UserModel.id == user.id).first().created_at
    db.commit()
    
    logger.info("User logged in with email", user_id=str(user.id), email=user.email)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Refresh access token.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email, "user_id": str(current_user.id), "role": current_user.role.value}
    )
    
    logger.info("Token refreshed", user_id=str(current_user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password.
    """
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    
    if not verify_password(password_change.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    logger.info("Password changed", user_id=str(user.id))
    
    return {"message": "Password changed successfully"}

@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset.
    """
    user = db.query(UserModel).filter(UserModel.email == password_reset.email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # TODO: Implement email sending with reset token
    # For now, just log the request
    logger.info("Password reset requested", email=password_reset.email)
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password/confirm")
async def reset_password_confirm(
    password_reset: PasswordResetConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirm password reset with token.
    """
    # TODO: Implement token verification
    # For now, just return success
    logger.info("Password reset confirmed")
    
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user 