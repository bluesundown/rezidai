import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.connection import engine, SessionLocal, Base
from models.user import User
from models.listing import Listing
from models.image import Image
from models.ai_filter import AIFilter
from services.auth_service import hash_password, create_access_token
from httpx import AsyncClient, ASGITransport
from main import app
import uuid

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Set up the database for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after test if needed

@pytest.fixture(scope="function")
async def client(setup_database):
    """Create a test client for the FastAPI app"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
async def test_user(db_session: Session):
    """Create a test user"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        first_name="Test",
        last_name="User",
        oauth_provider="email",
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
async def admin_user(db_session: Session):
    """Create a test admin user"""
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        first_name="Admin",
        last_name="User",
        oauth_provider="email",
        is_admin=True,
        email_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def user_token(test_user: User):
    """Generate a JWT token for test user"""
    return create_access_token({"sub": str(test_user.id)})

@pytest.fixture(scope="function")
def admin_token(admin_user: User):
    """Generate a JWT token for admin user"""
    return create_access_token({"sub": str(admin_user.id)})

@pytest.fixture(scope="function")
async def test_listing(db_session: Session, test_user: User):
    """Create a test listing"""
    listing = Listing(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Property",
        property_type="house",
        transaction_type="sale",
        address="123 Test Street",
        city="Test City",
        state="TS",
        postal_code="12345",
        price=500000,
        bedrooms=3,
        bathrooms=2,
        square_feet=2000,
        description="Test description"
    )
    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)
    return listing

@pytest.fixture(scope="function")
async def test_image(db_session: Session, test_listing: Listing):
    """Create a test image"""
    image = Image(
        id=uuid.uuid4(),
        listing_id=test_listing.id,
        original_filename="test.jpg",
        stored_filename="test.jpg",
        file_path="/uploads/test.jpg",
        thumbnail_path="/uploads/thumb_test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        width=1920,
        height=1080
    )
    db_session.add(image)
    db_session.commit()
    db_session.refresh(image)
    return image

@pytest.fixture(scope="function")
async def test_filter(db_session: Session):
    """Create a test AI filter"""
    filter = AIFilter(
        id=uuid.uuid4(),
        name="Test Filter",
        slug="test-filter",
        description="Test description",
        tone="professional",
        focus="general",
        is_active=True,
        display_order=0
    )
    db_session.add(filter)
    db_session.commit()
    db_session.refresh(filter)
    return filter
