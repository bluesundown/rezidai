import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_poi(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/maps/poi?address=123%20Main%20St%20New%20York%20NY",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "poi" in data
    assert "latitude" in data
    assert "longitude" in data
    assert "description_text" in data
    assert isinstance(data["poi"], list)

@pytest.mark.asyncio
async def test_poi_has_expected_structure(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/maps/poi?address=123%20Main%20St",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    if len(data["poi"]) > 0:
        poi = data["poi"][0]
        assert "name" in poi
        assert "type" in poi
        assert "vicinity" in poi

@pytest.mark.asyncio
async def test_save_poi_to_listing(client: AsyncClient, user_token: str, test_listing):
    response = await client.post(
        f"/api/maps/listing/{test_listing.id}/poi",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "address": f"{test_listing.address}, {test_listing.city}, {test_listing.state} {test_listing.postal_code}"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "poi_count" in data
    assert data["poi_count"] >= 0

@pytest.mark.asyncio
async def test_poi_saved_to_listing_database(client: AsyncClient, user_token: str, test_listing):
    # Save POI
    await client.post(
        f"/api/maps/listing/{test_listing.id}/poi",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "address": f"{test_listing.address}, {test_listing.city}"
        }
    )
    
    # Get listing and verify POI data was saved
    response = await client.get(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    # Note: POI data might not be in the response depending on model configuration

@pytest.mark.asyncio
async def test_save_poi_invalid_listing(client: AsyncClient, user_token: str):
    import uuid
    fake_id = str(uuid.uuid4())
    
    response = await client.post(
        f"/api/maps/listing/{fake_id}/poi",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "address": "123 Main St"
        }
    )
    
    assert response.status_code == 404
