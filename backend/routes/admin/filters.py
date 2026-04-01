from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.connection import get_db
from models.ai_filter import AIFilter
from middleware.auth import get_current_admin_user
import uuid

router = APIRouter()

class AIFilterCreate(BaseModel):
    name: str
    slug: str
    description: str = ""
    tone: str
    focus: str
    prompt_template: str = ""
    is_active: bool = True
    is_default: bool = False
    display_order: int = 0

class AIFilterUpdate(BaseModel):
    name: str = None
    description: str = None
    tone: str = None
    focus: str = None
    prompt_template: str = None
    is_active: bool = None
    is_default: bool = None
    display_order: int = None

class AIFilterResponse(BaseModel):
    id: Optional[str] = None
    name: str
    slug: str
    description: str
    tone: str
    focus: str
    is_active: bool
    is_default: bool
    display_order: int
    usage_count: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AIFilterResponse])
async def get_filters(
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    filters = db.query(AIFilter).order_by(AIFilter.display_order).all()
    return filters

@router.get("/{filter_id}", response_model=AIFilterResponse)
async def get_filter(
    filter_id: str,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        filter_uuid = uuid.UUID(filter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filter ID")
    
    filter = db.query(AIFilter).filter(AIFilter.id == filter_uuid).first()
    
    if not filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    return filter

@router.post("/", response_model=AIFilterResponse)
async def create_filter(
    filter_data: AIFilterCreate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    existing = db.query(AIFilter).filter(AIFilter.slug == filter_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Filter with this slug already exists"
        )
    
    filter = AIFilter(
        name=filter_data.name,
        slug=filter_data.slug,
        description=filter_data.description,
        tone=filter_data.tone,
        focus=filter_data.focus,
        prompt_template=filter_data.prompt_template,
        is_active=filter_data.is_active,
        is_default=filter_data.is_default,
        display_order=filter_data.display_order
    )
    
    db.add(filter)
    db.commit()
    db.refresh(filter)
    
    return filter

@router.put("/{filter_id}", response_model=AIFilterResponse)
async def update_filter(
    filter_id: str,
    filter_data: AIFilterUpdate,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        filter_uuid = uuid.UUID(filter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filter ID")
    
    filter = db.query(AIFilter).filter(AIFilter.id == filter_uuid).first()
    
    if not filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    update_data = filter_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(filter, key, value)
    
    db.commit()
    db.refresh(filter)
    
    return filter

@router.delete("/{filter_id}")
async def delete_filter(
    filter_id: str,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    try:
        filter_uuid = uuid.UUID(filter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid filter ID")
    
    filter = db.query(AIFilter).filter(AIFilter.id == filter_uuid).first()
    
    if not filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    db.delete(filter)
    db.commit()
    
    return {"message": "Filter deleted successfully"}
