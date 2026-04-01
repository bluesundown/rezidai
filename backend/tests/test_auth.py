import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient
from database.connection import SessionLocal
from models.user import User
from services.auth_service import hash_password
import uuid

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepassword123",
        "first_name": "New",
        "last_name": "User"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient):
    # First registration
    await client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    })
    
    # Second registration with same email
    response = await client.post("/api/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123",
        "first_name": "Another",
        "last_name": "User"
    })
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    response = await client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_user.email

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_password_reset_request(client: AsyncClient, test_user: User):
    response = await client.post("/api/auth/password-reset", json={
        "email": test_user.email
    })
    
    assert response.status_code == 200
    assert "sent" in response.json()["message"].lower()

@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    response = await client.get("/api/users/me")
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client: AsyncClient, test_user: User, user_token: str):
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email

@pytest.mark.asyncio
async def test_password_change(client: AsyncClient, test_user: User, user_token: str):
    response = await client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 200
    
    # Try logging in with new password
    response = await client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "newpassword123"
    })
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_password_change_wrong_current_password(client: AsyncClient, user_token: str):
    response = await client.put(
        "/api/users/me/password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 400
