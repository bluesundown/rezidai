from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database.connection import Base

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255))
    description = Column(Text)
    ai_generated_description = Column(Text)
    
    property_type = Column(String(50))
    transaction_type = Column(String(50))
    
    address = Column(String(500))
    city = Column(String(200))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="United States")
    latitude = Column(Float)
    longitude = Column(Float)
    
    price = Column(Integer)
    currency = Column(String(3), default="USD")
    
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_feet = Column(Integer)
    lot_size = Column(Float)
    year_built = Column(Integer)
    
    features = Column(JSON)
    amenities = Column(JSON)
    
    poi_data = Column(JSON)
    poi_text = Column(Text)
    
    status = Column(String(50), default="draft")
    is_published = Column(Boolean, default=False)
    
    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    user = relationship("User", backref="listings")
    images = relationship("Image", backref="listing", cascade="all, delete-orphan")
