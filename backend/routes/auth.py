import re
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from database.connection import get_db
from models.user import User
from services.auth_service import hash_password, verify_password, create_access_token, generate_email_verification_token, decode_access_token
from middleware.rate_limiter import limiter
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(
    # Apply rate limiting at router level
)

# Password validation constants
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security requirements.
    Returns: (is_valid, error_message)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password must be less than {MAX_PASSWORD_LENGTH} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=)"
    
    return True, ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH, description="Password for authentication")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict
    must_change_password: bool = False

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ..., 
        min_length=MIN_PASSWORD_LENGTH, 
        max_length=MAX_PASSWORD_LENGTH,
        description=f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters with uppercase, lowercase, number, and special character"
    )
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    
    @validator('password')
    @classmethod
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe"
            }
        }

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="New password must meet security requirements"
    )
    
    @validator('new_password')
    @classmethod
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    new_password: str = Field(
        ...,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
        description="New password must meet security requirements"
    )
    
    @validator('new_password')
    @classmethod
    def validate_password(cls, v):
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5 per minute")  # Strict rate limit for login
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        logger.warning(f"Login attempt for deactivated account: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Check if user must change password (auto-generated)
    must_change = getattr(user, 'must_change_password', False)
    
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": str(user.id)})
    
    logger.info(f"Successful login for user: {request.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "email_verified": user.email_verified
        },
        "must_change_password": must_change
    }

@router.post("/register", response_model=LoginResponse)
@limiter.limit("3 per minute")  # Strict rate limit for registration
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    verification_token = generate_email_verification_token(uuid.uuid4().hex)
    
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        oauth_provider="email",
        email_verification_token=verification_token,
        must_change_password=False  # User created their own password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token({"sub": str(user.id)})
    
    logger.info(f"New user registered: {request.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "email_verified": user.email_verified
        },
        "must_change_password": False
    }

@router.post("/password-reset")
@limiter.limit("3 per hour")  # Very strict rate limit for password reset
async def password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists (security best practice)
        return {"message": "If email exists, reset link has been sent"}
    
    reset_token = create_access_token(
        {"sub": str(user.id), "type": "password_reset"},
        expires_delta=None
    )
    
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    
    from services.email_service import email_service
    await email_service.send_password_reset_email(request.email, reset_link)
    
    logger.info(f"Password reset requested for: {request.email}")
    
    return {"message": "If email exists, reset link has been sent"}

@router.post("/password-reset-confirm")
async def password_reset_confirm(request: PasswordResetConfirmRequest, db: Session = Depends(get_db)):
    payload = decode_access_token(request.token)
    
    if not payload or payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = hash_password(request.new_password)
    user.email_verification_token = None
    db.commit()
    
    logger.info(f"Password reset confirmed for user: {user.email}")
    
    return {"message": "Password has been reset"}

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), 
                         current_user: User = Depends(lambda db: db.query(User).first())):  # TODO: Add proper auth dependency
    """Change password (requires user to be logged in)"""
    # This endpoint should be protected with authentication
    # For now, just a placeholder
    raise HTTPException(status_code=501, detail="Not implemented yet")
