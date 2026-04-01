from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.connection import get_db
from models.listing import Listing
from models.user import User
from middleware.auth import get_current_user
from services.maps_service import google_maps_service
import uuid

router = APIRouter()

class POIItem(BaseModel):
    name: str
    type: str
    vicinity: str
    rating: Optional[float]
    user_ratings_total: Optional[int]

class POIResponse(BaseModel):
    address: str
    formatted_address: str
    latitude: float
    longitude: float
    poi: List[POIItem]
    description_text: str

@router.get("/poi", response_model=POIResponse)
async def get_poi(
    address: str = Query(..., description="Property address"),
    current_user: User = Depends(get_current_user)
):
    location = await google_maps_service.get_location_coordinates(address)
    
    if not location:
        raise HTTPException(
            status_code=400,
            detail="Could not geocode address"
        )
    
    poi_list = await google_maps_service.search_nearby_poi(
        location['lat'],
        location['lng']
    )
    
    description_text = google_maps_service.format_poi_for_description(poi_list)
    
    return POIResponse(
        address=address,
        formatted_address=location['formatted_address'],
        latitude=location['lat'],
        longitude=location['lng'],
        poi=[
            POIItem(
                name=poi['name'],
                type=poi['type'],
                vicinity=poi['vicinity'],
                rating=poi.get('rating'),
                user_ratings_total=poi.get('user_ratings_total')
            )
            for poi in poi_list
        ],
        description_text=description_text
    )

@router.post("/listing/{listing_id}/poi")
async def save_poi_to_listing(
    listing_id: str,
    address: str = None,
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
    
    if not address:
        address = f"{listing.address}, {listing.city}, {listing.state} {listing.postal_code}"
    
    location = await google_maps_service.get_location_coordinates(address)
    
    if location:
        listing.latitude = location['lat']
        listing.longitude = location['lng']
    
    poi_list = await google_maps_service.search_nearby_poi(
        listing.latitude or location['lat'],
        listing.longitude or location['lng']
    )
    
    listing.poi_data = poi_list
    listing.poi_text = google_maps_service.format_poi_for_description(poi_list)
    
    db.commit()
    
    return {
        "message": "POI data saved",
        "latitude": listing.latitude,
        "longitude": listing.longitude,
        "poi_count": len(poi_list)
    }
