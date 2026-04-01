from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import List, Optional
from database.connection import get_db
from models.listing import Listing
from models.user import User
from middleware.auth import get_current_user
import uuid

router = APIRouter()

class CreateListingRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Listing title")
    property_type: str = Field(..., min_length=1, max_length=100, description="Property type")
    transaction_type: str = Field(..., min_length=1, max_length=50, description="Sale or rent")
    address: str = Field(..., min_length=5, max_length=500, description="Street address")
    city: str = Field(..., min_length=1, max_length=200, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State/Province")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal/ZIP code")
    country: str = Field("United States", min_length=1, max_length=100, description="Country")
    price: int = Field(..., gt=0, description="Price must be positive")
    bedrooms: int = Field(..., ge=0, le=50, description="Number of bedrooms (0-50)")
    bathrooms: float = Field(..., gt=0, le=50, description="Number of bathrooms (0.5-50)")
    square_feet: int = Field(..., gt=0, le=100000, description="Square footage (1-100000)")
    description: Optional[str] = Field("", max_length=5000, description="Property description")
    features: Optional[dict] = Field({}, description="Property features")
    amenities: Optional[List[str]] = Field([], description="List of amenities")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Beautiful Modern Home",
                "property_type": "House",
                "transaction_type": "sale",
                "address": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States",
                "price": 500000,
                "bedrooms": 3,
                "bathrooms": 2.5,
                "square_feet": 2500,
                "description": "A beautiful modern home..."
            }
        }

class UpdateListingRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    property_type: Optional[str] = Field(None, min_length=1, max_length=100)
    transaction_type: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=200)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[int] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, ge=0, le=50)
    bathrooms: Optional[float] = Field(None, gt=0, le=50)
    square_feet: Optional[int] = Field(None, gt=0, le=100000)
    description: Optional[str] = Field(None, max_length=5000)
    features: Optional[dict] = None
    amenities: Optional[List[str]] = None
    status: Optional[str] = Field(None, min_length=1, max_length=50)

class ListingResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    ai_generated_description: Optional[str]
    property_type: str
    transaction_type: str
    address: str
    city: str
    state: str
    postal_code: str
    country: str
    price: int
    bedrooms: int
    bathrooms: int
    square_feet: int
    status: str
    is_published: bool
    image_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=ListingResponse)
async def create_listing(
    request: CreateListingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = Listing(
        user_id=current_user.id,
        title=request.title,
        property_type=request.property_type,
        transaction_type=request.transaction_type,
        address=request.address,
        city=request.city,
        state=request.state,
        postal_code=request.postal_code,
        country=request.country,
        price=request.price,
        bedrooms=request.bedrooms,
        bathrooms=request.bathrooms,
        square_feet=request.square_feet,
        description=request.description,
        features=request.features,
        amenities=request.amenities
    )
    
    db.add(listing)
    db.commit()
    db.refresh(listing)
    
    return ListingResponse(
        id=str(listing.id),
        user_id=str(listing.user_id),
        title=listing.title,
        description=listing.description,
        ai_generated_description=listing.ai_generated_description,
        property_type=listing.property_type,
        transaction_type=listing.transaction_type,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        postal_code=listing.postal_code,
        country=listing.country,
        price=listing.price,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        square_feet=listing.square_feet,
        status=listing.status,
        is_published=listing.is_published,
        image_count=0,
        created_at=listing.created_at.isoformat(),
        updated_at=listing.updated_at.isoformat()
    )

@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Listing).filter(Listing.user_id == current_user.id)
    
    total = query.count()
    listings = query.offset(skip).limit(limit).all()
    
    return [
        ListingResponse(
            id=str(l.id),
            user_id=str(l.user_id),
            title=l.title,
            description=l.description,
            ai_generated_description=l.ai_generated_description,
            property_type=l.property_type,
            transaction_type=l.transaction_type,
            address=l.address,
            city=l.city,
            state=l.state,
            postal_code=l.postal_code,
            country=l.country,
            price=l.price,
            bedrooms=l.bedrooms,
            bathrooms=l.bathrooms,
            square_feet=l.square_feet,
            status=l.status,
            is_published=l.is_published,
            image_count=0,
            created_at=l.created_at.isoformat(),
            updated_at=l.updated_at.isoformat()
        )
        for l in listings
    ]

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        listing_uuid = uuid.UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing ID")
    
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return ListingResponse(
        id=str(listing.id),
        user_id=str(listing.user_id),
        title=listing.title,
        description=listing.description,
        ai_generated_description=listing.ai_generated_description,
        property_type=listing.property_type,
        transaction_type=listing.transaction_type,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        postal_code=listing.postal_code,
        country=listing.country,
        price=listing.price,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        square_feet=listing.square_feet,
        status=listing.status,
        is_published=listing.is_published,
        image_count=0,
        created_at=listing.created_at.isoformat(),
        updated_at=listing.updated_at.isoformat()
    )

@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: str,
    request: UpdateListingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        listing_uuid = uuid.UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing ID")
    
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(listing, key, value)
    
    db.commit()
    db.refresh(listing)
    
    return ListingResponse(
        id=str(listing.id),
        user_id=str(listing.user_id),
        title=listing.title,
        description=listing.description,
        ai_generated_description=listing.ai_generated_description,
        property_type=listing.property_type,
        transaction_type=listing.transaction_type,
        address=listing.address,
        city=listing.city,
        state=listing.state,
        postal_code=listing.postal_code,
        country=listing.country,
        price=listing.price,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        square_feet=listing.square_feet,
        status=listing.status,
        is_published=listing.is_published,
        image_count=0,
        created_at=listing.created_at.isoformat(),
        updated_at=listing.updated_at.isoformat()
    )

@router.delete("/{listing_id}")
async def delete_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        listing_uuid = uuid.UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid listing ID")
    
    listing = db.query(Listing).filter(
        Listing.id == listing_uuid,
        Listing.user_id == current_user.id
    ).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    from services.storage_service import storage_service
    storage_service.delete_listing_images(str(listing.id))
    
    db.delete(listing)
    db.commit()
    
    return {"message": "Listing deleted successfully"}
