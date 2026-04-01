from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database.connection import Base

class AIFilter(Base):
    __tablename__ = "ai_filters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    tone = Column(String(50))
    focus = Column(String(100))
    
    prompt_template = Column(Text)
    parameters = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
