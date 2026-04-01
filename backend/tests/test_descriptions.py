import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_generate_description(client: AsyncClient, user_token: str, test_listing):
    response = await client.post(
        "/api/descriptions/generate",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "listing_id": str(test_listing.id),
            "tone": "professional",
            "focus": "general"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert data["tone"] == "professional"
    assert data["focus"] == "general"
    assert len(data["description"]) > 0

@pytest.mark.asyncio
async def test_generate_description_with_different_tones(client: AsyncClient, user_token: str, test_listing):
    tones = ["professional", "friendly", "luxury", "modern"]
    
    for tone in tones:
        response = await client.post(
            "/api/descriptions/generate",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "listing_id": str(test_listing.id),
                "tone": tone,
                "focus": "general"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["tone"] == tone
        assert len(data["description"]) > 50

@pytest.mark.asyncio
async def test_generate_description_invalid_listing(client: AsyncClient, user_token: str):
    import uuid
    fake_id = str(uuid.uuid4())
    
    response = await client.post(
        "/api/descriptions/generate",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "listing_id": fake_id,
            "tone": "professional",
            "focus": "general"
        }
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_description_filters(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/descriptions/filters",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tones" in data
    assert "focuses" in data
    assert len(data["tones"]) > 0
    assert len(data["focuses"]) > 0

@pytest.mark.asyncio
async def test_description_saved_to_listing(client: AsyncClient, user_token: str, test_listing):
    # Generate description
    await client.post(
        "/api/descriptions/generate",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "listing_id": str(test_listing.id),
            "tone": "professional",
            "focus": "general"
        }
    )
    
    # Get listing and verify description was saved
    response = await client.get(
        f"/api/listings/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ai_generated_description"] is not None
    assert len(data["ai_generated_description"]) > 0
