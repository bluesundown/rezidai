from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    profile_photo_url = Column(String(500))
    
    oauth_provider = Column(String(50))
    oauth_id = Column(String(255))
    
    stripe_customer_id = Column(String(255))
    subscription_tier = Column(String(50), default="free")
    subscription_status = Column(String(50), default="inactive")
    is_admin = Column(Boolean, default=False)
    
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    email_verification_token = Column(String(255))
    
    must_change_password = Column(Boolean, default=False)  # For auto-generated passwords
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
