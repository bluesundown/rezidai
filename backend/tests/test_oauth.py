import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_google_oauth_callback(client: AsyncClient):
    # In mock mode, this should work with any token
    response = await client.post(
        "/api/oauth/google/callback",
        json={
            "token": "mock_google_token_123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "mock.google@example.com"

@pytest.mark.asyncio
async def test_google_oauth_creates_new_user(client: AsyncClient):
    response = await client.post(
        "/api/oauth/google/callback",
        json={
            "token": "mock_google_token_new_user"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Use the token to get user info
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {data['access_token']}"}
    )
    
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email_verified"] == True

@pytest.mark.asyncio
async def test_apple_oauth_callback(client: AsyncClient):
    response = await client.post(
        "/api/oauth/apple/callback",
        json={
            "token": "mock_apple_token_123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "mock.apple@example.com"

@pytest.mark.asyncio
async def test_oauth_user_can_access_protected_routes(client: AsyncClient):
    # Login with Google OAuth
    response = await client.post(
        "/api/oauth/google/callback",
        json={
            "token": "mock_google_token_access"
        }
    )
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Access protected route
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
