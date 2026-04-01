from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database.connection import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)
    
    original_filename = Column(String(255))
    stored_filename = Column(String(255))
    file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    width = Column(Integer)
    height = Column(Integer)
    
    is_enhanced = Column(Boolean, default=False)
    enhancement_applied = Column(String(255))
    
    display_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    
    alt_text = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
