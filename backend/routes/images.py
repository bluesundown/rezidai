from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.connection import get_db
from models.image import Image
from models.listing import Listing
from models.user import User
from middleware.auth import get_current_user
from services.image_service import image_service
from services.storage_service import storage_service
import uuid

router = APIRouter()

class ImageResponse(BaseModel):
    id: str
    listing_id: str
    original_filename: str
    file_path: str
    thumbnail_path: str
    width: int
    height: int
    is_primary: bool
    display_order: int
    created_at: str

    class Config:
        from_attributes = True

@router.post("/upload")
async def upload_image(
    listing_id: str,
    file: UploadFile = File(...),
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
    
    if not image_service.is_valid_format(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(image_service.allowed_formats)}"
        )
    
    file_contents = await file.read()
    if len(file_contents) > image_service.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {image_service.max_file_size // (1024*1024)}MB"
        )
    
    unique_filename = storage_service.generate_unique_filename(file.filename)
    image_data = image_service.save_image(file_contents, str(listing_uuid), unique_filename)
    
    if not image_data:
        raise HTTPException(status_code=500, detail="Failed to save image")
    
    existing_images = db.query(Image).filter(Image.listing_id == listing_uuid).count()
    
    image = Image(
        listing_id=listing_uuid,
        original_filename=file.filename,
        stored_filename=unique_filename,
        file_path=image_data['file_path'],
        thumbnail_path=image_data['thumbnail_path'],
        file_size=len(file_contents),
        mime_type=file.content_type,
        width=image_data['width'],
        height=image_data['height'],
        display_order=existing_images,
        is_primary=existing_images == 0
    )
    
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return ImageResponse(
        id=str(image.id),
        listing_id=str(image.listing_id),
        original_filename=image.original_filename,
        file_path=image.file_path,
        thumbnail_path=image.thumbnail_path,
        width=image.width,
        height=image.height,
        is_primary=image.is_primary,
        display_order=image.display_order,
        created_at=image.created_at.isoformat()
    )

@router.get("/listing/{listing_id}", response_model=List[ImageResponse])
async def get_listing_images(
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
    
    images = db.query(Image).filter(
        Image.listing_id == listing_uuid
    ).order_by(Image.display_order).all()
    
    return [
        ImageResponse(
            id=str(img.id),
            listing_id=str(img.listing_id),
            original_filename=img.original_filename,
            file_path=img.file_path,
            thumbnail_path=img.thumbnail_path,
            width=img.width,
            height=img.height,
            is_primary=img.is_primary,
            display_order=img.display_order,
            created_at=img.created_at.isoformat()
        )
        for img in images
    ]

@router.put("/{image_id}")
async def update_image(
    image_id: str,
    is_primary: bool = None,
    display_order: int = None,
    alt_text: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        image_uuid = uuid.UUID(image_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image ID")
    
    image = db.query(Image).filter(Image.id == image_uuid).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    listing = db.query(Listing).filter(Listing.id == image.listing_id).first()
    if not listing or listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if is_primary is not None:
        db.query(Image).filter(Image.listing_id == image.listing_id).update({"is_primary": False})
        image.is_primary = is_primary
    
    if display_order is not None:
        image.display_order = display_order
    
    if alt_text is not None:
        image.alt_text = alt_text
    
    db.commit()
    db.refresh(image)
    
    return {
        "id": str(image.id),
        "is_primary": image.is_primary,
        "display_order": image.display_order,
        "alt_text": image.alt_text
    }

@router.delete("/{image_id}")
async def delete_image(
    image_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        image_uuid = uuid.UUID(image_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image ID")
    
    image = db.query(Image).filter(Image.id == image_uuid).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    listing = db.query(Listing).filter(Listing.id == image.listing_id).first()
    if not listing or listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    storage_service.delete_image(f"{image_service.uploads_dir}{image.file_path}")
    storage_service.delete_image(f"{image_service.uploads_dir}{image.thumbnail_path}")
    
    db.delete(image)
    db.commit()
    
    return {"message": "Image deleted successfully"}
