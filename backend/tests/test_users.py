import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, user_token: str, test_user):
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name

@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, user_token: str, test_user):
    response = await client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "first_name": "Updated",
            "phone": "+1234567890"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["phone"] == "+1234567890"

@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient, user_token: str, test_user):
    response = await client.put(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "phone": "+1987654321"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+1987654321"
    assert data["first_name"] == test_user.first_name  # Unchanged

@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient, user_token: str, test_user):
    response = await client.delete(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    
    # Verify user is deleted
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, user_token: str):
    response = await client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "testpassword123",
            "new_password": "newsecurepassword123"
        }
    )
    
    assert response.status_code == 200
    assert "changed" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, user_token: str):
    response = await client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()
