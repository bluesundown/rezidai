import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_listing(client: AsyncClient, user_token: str):
    response = await client.post(
        "/api/listings/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "title": "Beautiful House",
            "property_type": "house",
            "transaction_type": "sale",
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62701",
            "price": 450000,
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 2000
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Beautiful House"
    assert data["price"] == 450000
    assert data["status"] == "draft"

@pytest.mark.asyncio
async def test_get_listings(client: AsyncClient, user_token: str, test_listing):
    response = await client.get(
        "/api/listings/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_get_listing_by_id(client: AsyncClient, user_token: str, test_listing):
    response = await client.get(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_listing.id)
    assert data["title"] == test_listing.title

@pytest.mark.asyncio
async def test_get_listing_not_found(client: AsyncClient, user_token: str):
    import uuid
    fake_id = str(uuid.uuid4())
    
    response = await client.get(
        f"/api/listings/{fake_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_listing(client: AsyncClient, user_token: str, test_listing):
    response = await client.put(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "price": 550000,
            "title": "Updated Title"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 550000
    assert data["title"] == "Updated Title"

@pytest.mark.asyncio
async def test_delete_listing(client: AsyncClient, user_token: str, test_listing):
    response = await client.delete(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify listing is deleted
    response = await client.get(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_cannot_access_other_user_listing(client: AsyncClient, user_token: str, admin_user):
    # Create listing for admin user
    import uuid
    from models.listing import Listing
    from database.connection import SessionLocal
    
    db = SessionLocal()
    admin_listing = Listing(
        id=uuid.uuid4(),
        user_id=admin_user.id,
        title="Admin Property",
        property_type="house",
        transaction_type="sale",
        address="456 Admin St",
        city="Admin City",
        state="AC",
        postal_code="99999",
        price=1000000,
        bedrooms=5,
        bathrooms=4,
        square_feet=4000
    )
    db.add(admin_listing)
    db.commit()
    listing_id = str(admin_listing.id)  # Get ID before closing session
    db.close()
    
    # Try to access with test_user's token
    response = await client.get(
        f"/api/listings/{listing_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 404
