from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from middleware.auth import get_current_admin_user

router = APIRouter()

class APIKeyConfig(BaseModel):
    key_name: str
    key_value: str

class ConfigResponse(BaseModel):
    message: str
    config_keys: list

@router.get("/api-keys")
async def get_api_keys(current_user = Depends(get_current_admin_user)):
    from config import CONFIG
    
    config_keys = {
        "qwen": {
            "name": "Qwen AI",
            "endpoint": CONFIG['api']['qwen_endpoint'],
            "model": CONFIG['api']['qwen_model'],
            "configured": bool(CONFIG['api']['qwen_api_key'] and CONFIG['api']['qwen_api_key'] != "YOUR_QWEN_KEY")
        },
        "google_maps": {
            "name": "Google Maps",
            "configured": bool(CONFIG['api']['google_maps_api_key'] and CONFIG['api']['google_maps_api_key'] != "YOUR_GOOGLE_MAPS_KEY")
        },
        "stripe": {
            "name": "Stripe",
            "configured": bool(CONFIG['api']['stripe_secret_key'] and CONFIG['api']['stripe_secret_key'] != "sk_test_...")
        }
    }
    
    return {"config_keys": config_keys}

@router.put("/api-keys")
async def update_api_key(
    request: APIKeyConfig,
    current_user = Depends(get_current_admin_user)
):
    from config import CONFIG
    import os
    
    key_updates = {
        "qwen": {
            "env_var": "QWEN_API_KEY",
            "config_path": "api.qwen_api_key"
        },
        "google_maps": {
            "env_var": "GOOGLE_MAPS_API_KEY",
            "config_path": "api.google_maps_api_key"
        },
        "stripe": {
            "env_var": "STRIPE_SECRET_KEY",
            "config_path": "api.stripe_secret_key"
        }
    }
    
    if request.key_name not in key_updates:
        raise HTTPException(
            status_code=400,
            detail="Invalid API key name"
        )
    
    update_info = key_updates[request.key_name]
    os.environ[update_info['env_var']] = request.key_value
    
    return {
        "message": f"{request.key_name} API key updated",
        "note": "Changes will take effect on next server restart"
    }

@router.get("/mock-services")
async def get_mock_status(current_user = Depends(get_current_admin_user)):
    from config import CONFIG
    return {
        "mock_services": CONFIG.get('mock_services', {})
    }

@router.put("/mock-services")
async def toggle_mock_services(
    enabled: bool,
    current_user = Depends(get_current_admin_user)
):
    from config import CONFIG
    CONFIG['mock_services']['enabled'] = enabled
    return {
        "message": f"Mock services {'enabled' if enabled else 'disabled'}",
        "mock_services": CONFIG.get('mock_services', {})
    }
