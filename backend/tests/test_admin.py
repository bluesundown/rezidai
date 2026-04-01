import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_api_keys_requires_admin(client: AsyncClient, user_token: str):
    response = await client.get(
        "/api/admin/config/api-keys",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_api_keys_success(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/admin/config/api-keys",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "config_keys" in data

@pytest.mark.asyncio
async def test_update_api_key(client: AsyncClient, admin_token: str):
    response = await client.put(
        "/api/admin/config/api-keys",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "key_name": "qwen",
            "key_value": "test-key-123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

@pytest.mark.asyncio
async def test_update_invalid_api_key(client: AsyncClient, admin_token: str):
    response = await client.put(
        "/api/admin/config/api-keys",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "key_name": "invalid_key",
            "key_value": "test-key-123"
        }
    )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_mock_services(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/admin/config/mock-services",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mock_services" in data

@pytest.mark.asyncio
async def test_toggle_mock_services(client: AsyncClient, admin_token: str):
    response = await client.put(
        "/api/admin/config/mock-services?enabled=false",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

@pytest.mark.asyncio
async def test_get_filters_admin(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/admin/filters/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_filter(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/admin/filters/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "New Filter",
            "slug": "new-filter",
            "tone": "professional",
            "focus": "investment",
            "description": "A new test filter"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Filter"
    assert data["slug"] == "new-filter"

@pytest.mark.asyncio
async def test_create_filter_duplicate_slug(client: AsyncClient, admin_token: str, test_filter):
    response = await client.post(
        "/api/admin/filters/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Duplicate Filter",
            "slug": test_filter.slug,
            "tone": "professional",
            "focus": "general"
        }
    )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_filter(client: AsyncClient, admin_token: str, test_filter):
    filter_id = str(test_filter.id)
    response = await client.put(
        f"/api/admin/filters/{filter_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Updated Filter",
            "is_active": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Filter"
    assert data["is_active"] == False

@pytest.mark.asyncio
async def test_delete_filter(client: AsyncClient, admin_token: str, test_filter):
    filter_id = str(test_filter.id)
    response = await client.delete(
        f"/api/admin/filters/{filter_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify filter is deleted
    response = await client.get(
        f"/api/admin/filters/{filter_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_feature_tiers(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/admin/features/tiers",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tiers" in data
    assert isinstance(data["tiers"], list)
    assert len(data["tiers"]) > 0
