from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from database.connection import get_db
from models.listing import Listing
from models.user import User
from middleware.auth import get_current_user
from services.ai_service import qwen_service
import uuid

router = APIRouter()

class GenerateDescriptionRequest(BaseModel):
    listing_id: str = Field(..., min_length=1, max_length=100, description="UUID of the listing")
    tone: str = Field("professional", min_length=1, max_length=50, description="Tone: professional, friendly, luxury, modern")
    focus: str = Field("general", min_length=1, max_length=50, description="Focus: general, investment, family, luxury, location, amenities")
    
    class Config:
        schema_extra = {
            "example": {
                "listing_id": "550e8400-e29b-41d4-a716-446655440000",
                "tone": "professional",
                "focus": "general"
            }
        }

class GenerateDescriptionResponse(BaseModel):
    listing_id: str
    description: str
    tone: str
    focus: str

@router.post("/generate", response_model=GenerateDescriptionResponse)
async def generate_description(
    request: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        listing_uuid = uuid.UUID(request.listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing ID")
    
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_data = {
        "property_type": listing.property_type,
        "address": listing.address,
        "city": listing.city,
        "state": listing.state,
        "bedrooms": listing.bedrooms,
        "bathrooms": listing.bathrooms,
        "square_feet": listing.square_feet,
        "price": listing.price,
        "description": listing.description or "",
        "poi_text": listing.poi_text or ""
    }
    
    description = await qwen_service.generate_description(
        listing_data,
        request.tone,
        request.focus
    )
    
    listing.ai_generated_description = description
    db.commit()
    
    return GenerateDescriptionResponse(
        listing_id=str(listing.id),
        description=description,
        tone=request.tone,
        focus=request.focus
    )

@router.get("/filters")
async def get_available_filters():
    from config import CONFIG
    tones = list(CONFIG['description']['tones'].keys())
    focuses = ["general", "investment", "family", "luxury", "location", "amenities"]
    return {
        "tones": tones,
        "focuses": focuses
    }
