import pytest
from services.ai_service import qwen_service

@pytest.mark.asyncio
async def test_generate_description_professional():
    listing_data = {
        "property_type": "house",
        "address": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 2000,
        "price": 450000,
        "description": "Beautiful home",
        "poi_text": ""
    }
    
    result = await qwen_service.generate_description(listing_data, "professional", "general")
    
    assert isinstance(result, str)
    assert len(result) > 50
    assert "Springfield" in result or "3" in result

@pytest.mark.asyncio
async def test_generate_description_friendly():
    listing_data = {
        "property_type": "apartment",
        "address": "456 Oak Ave",
        "city": "Chicago",
        "state": "IL",
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 1200,
        "price": 250000,
        "description": "Cozy apartment",
        "poi_text": ""
    }
    
    result = await qwen_service.generate_description(listing_data, "friendly", "family")
    
    assert isinstance(result, str)
    assert len(result) > 50

@pytest.mark.asyncio
async def test_generate_description_luxury():
    listing_data = {
        "property_type": "villa",
        "address": "789 Luxury Lane",
        "city": "Beverly Hills",
        "state": "CA",
        "bedrooms": 5,
        "bathrooms": 4,
        "square_feet": 5000,
        "price": 2500000,
        "description": "Luxury estate",
        "poi_text": ""
    }
    
    result = await qwen_service.generate_description(listing_data, "luxury", "luxury")
    
    assert isinstance(result, str)
    assert len(result) > 100

@pytest.mark.asyncio
async def test_generate_description_modern():
    listing_data = {
        "property_type": "condo",
        "address": "321 Modern Blvd",
        "city": "San Francisco",
        "state": "CA",
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1500,
        "price": 850000,
        "description": "Modern condo",
        "poi_text": ""
    }
    
    result = await qwen_service.generate_description(listing_data, "modern", "amenities")
    
    assert isinstance(result, str)
    assert len(result) > 50

@pytest.mark.asyncio
async def test_generate_description_with_poi():
    listing_data = {
        "property_type": "house",
        "address": "123 Main St",
        "city": "Austin",
        "state": "TX",
        "bedrooms": 4,
        "bathrooms": 3,
        "square_feet": 2800,
        "price": 650000,
        "description": "Spacious home",
        "poi_text": "Nearby amenities include: Dining: Whole Foods, The Salt Tr | Education: Zilker Elementary"
    }
    
    result = await qwen_service.generate_description(listing_data, "professional", "location")
    
    assert isinstance(result, str)
    assert len(result) > 50

@pytest.mark.asyncio
async def test_generate_description_minimal_data():
    listing_data = {
        "property_type": "house",
        "address": "",
        "city": "",
        "state": "",
        "bedrooms": 0,
        "bathrooms": 0,
        "square_feet": 0,
        "price": 0,
        "description": "",
        "poi_text": ""
    }
    
    result = await qwen_service.generate_description(listing_data, "professional", "general")
    
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_mock_mode_enabled():
    from config import CONFIG
    
    # Verify mock mode is enabled
    assert CONFIG.get('mock_services', {}).get('ai_responses', False) == True
    assert qwen_service.use_mock == True
