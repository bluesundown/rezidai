import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from httpx import AsyncClient
import io

@pytest.mark.asyncio
async def test_upload_image(client: AsyncClient, user_token: str, test_listing):
    # Create a test image file
    image_data = io.BytesIO()
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_data, format='JPEG')
    image_data.seek(0)
    
    files = [("file", ("test.jpg", image_data, "image/jpeg"))]
    
    response = await client.post(
        f"/api/images/upload?listing_id={test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "file_path" in data
    assert "thumbnail_path" in data
    assert data["width"] == 100
    assert data["height"] == 100

@pytest.mark.asyncio
async def test_upload_image_without_listing(client: AsyncClient, user_token: str):
    image_data = io.BytesIO()
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(image_data, format='JPEG')
    image_data.seek(0)
    
    files = [("file", ("test.jpg", image_data, "image/jpeg"))]
    
    response = await client.post(
        "/api/images/upload?listing_id=invalid-id",
        headers={"Authorization": f"Bearer {user_token}"},
        files=files
    )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_listing_images(client: AsyncClient, user_token: str, test_listing, test_image):
    response = await client.get(
        f"/api/images/listing/{test_listing.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == str(test_image.id)

@pytest.mark.asyncio
async def test_delete_image(client: AsyncClient, user_token: str, test_image):
    response = await client.delete(
        f"/api/images/{test_image.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_cannot_delete_other_user_image(client: AsyncClient, user_token: str, admin_user):
    import uuid
    from models.listing import Listing
    from models.image import Image
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
    admin_image = Image(
        id=uuid.uuid4(),
        listing_id=admin_listing.id,
        original_filename="admin.jpg",
        stored_filename="admin.jpg",
        file_path="/uploads/admin.jpg",
        thumbnail_path="/uploads/thumb_admin.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        width=1920,
        height=1080
    )
    db.add(admin_listing)
    db.add(admin_image)
    db.commit()
    db.close()
    
    response = await client.delete(
        f"/api/images/{admin_image.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    assert response.status_code == 403
