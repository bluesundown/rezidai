from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database.connection import get_db
from models.user import User
from services.auth_service import create_access_token
from services.oauth_service import oauth_service
import uuid

router = APIRouter()

class OAuthCallbackRequest(BaseModel):
    token: str

class OAuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/google/callback", response_model=OAuthResponse)
async def google_oauth_callback(request: OAuthCallbackRequest, db: Session = Depends(get_db)):
    user_data = await oauth_service.verify_google_token(request.token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    existing_user = db.query(User).filter(User.oauth_id == user_data['sub']).first()
    
    if not existing_user:
        existing_user = db.query(User).filter(User.email == user_data['email']).first()
        if existing_user:
            existing_user.oauth_provider = "google"
            existing_user.oauth_id = user_data['sub']
            existing_user.profile_photo_url = user_data.get('picture')
            db.commit()
        else:
            name_parts = user_data['name'].split()
            new_user = User(
                email=user_data['email'],
                first_name=name_parts[0] if len(name_parts) > 0 else "User",
                last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else None,
                oauth_provider="google",
                oauth_id=user_data['sub'],
                profile_photo_url=user_data.get('picture'),
                email_verified=True,
                email_verified_at=datetime.utcnow()
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            existing_user = new_user
    
    existing_user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": str(existing_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(existing_user.id),
            "email": existing_user.email,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "is_admin": existing_user.is_admin,
            "email_verified": existing_user.email_verified
        }
    }

@router.post("/apple/callback", response_model=OAuthResponse)
async def apple_oauth_callback(request: OAuthCallbackRequest, db: Session = Depends(get_db)):
    user_data = await oauth_service.verify_apple_token(request.token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple token"
        )
    
    existing_user = db.query(User).filter(User.oauth_id == user_data['sub']).first()
    
    if not existing_user:
        existing_user = db.query(User).filter(User.email == user_data['email']).first()
        if existing_user:
            existing_user.oauth_provider = "apple"
            existing_user.oauth_id = user_data['sub']
            db.commit()
        else:
            name_parts = user_data['name'].split()
            new_user = User(
                email=user_data['email'],
                first_name=name_parts[0] if len(name_parts) > 0 else "User",
                last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else None,
                oauth_provider="apple",
                oauth_id=user_data['sub'],
                email_verified=True,
                email_verified_at=datetime.utcnow()
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            existing_user = new_user
    
    existing_user.last_login_at = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": str(existing_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(existing_user.id),
            "email": existing_user.email,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "is_admin": existing_user.is_admin,
            "email_verified": existing_user.email_verified
        }
    }
