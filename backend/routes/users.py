from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.connection import get_db
from models.user import User
from middleware.auth import get_current_user
from services.auth_service import hash_password

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    profile_photo_url: Optional[str]
    subscription_tier: str
    email_verified: bool
    created_at: str

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        profile_photo_url=current_user.profile_photo_url,
        subscription_tier=current_user.subscription_tier,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at.isoformat()
    )

@router.put("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.first_name is not None:
        current_user.first_name = request.first_name
    if request.last_name is not None:
        current_user.last_name = request.last_name
    if request.phone is not None:
        current_user.phone = request.phone
    if request.profile_photo_url is not None:
        current_user.profile_photo_url = request.profile_photo_url
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        profile_photo_url=current_user.profile_photo_url,
        subscription_tier=current_user.subscription_tier,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at.isoformat()
    )

@router.put("/me/password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from services.auth_service import verify_password
    
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from services.storage_service import storage_service
    storage_service.delete_listing_images(str(current_user.id))
    
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}
