from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from middleware.auth import get_current_admin_user

router = APIRouter()

class FeatureTier(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    price_monthly: int
    price_yearly: int
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    features: List[str]
    is_active: bool = True
    display_order: int = 0

class FeatureResponse(BaseModel):
    tiers: List[FeatureTier]

@router.get("/tiers")
async def get_feature_tiers(current_user = Depends(get_current_admin_user)):
    default_tiers = [
        {
            "name": "Free",
            "description": "Basic features for getting started",
            "price_monthly": 0,
            "price_yearly": 0,
            "features": [
                "3 listings per month",
                "Basic AI descriptions",
                "Standard image enhancement",
                "Email support"
            ],
            "is_active": True,
            "display_order": 0
        },
        {
            "name": "Pro",
            "description": "Advanced features for serious agents",
            "price_monthly": 2900,
            "price_yearly": 29000,
            "features": [
                "Unlimited listings",
                "Premium AI descriptions",
                "Advanced image enhancement",
                "Priority support",
                "Custom branding",
                "Analytics dashboard"
            ],
            "is_active": True,
            "display_order": 1
        },
        {
            "name": "Enterprise",
            "description": "Full-featured solution for teams",
            "price_monthly": 9900,
            "price_yearly": 99000,
            "features": [
                "Everything in Pro",
                "Team collaboration",
                "API access",
                "Dedicated support",
                "Custom integrations",
                "White-label option"
            ],
            "is_active": True,
            "display_order": 2
        }
    ]
    
    return {"tiers": default_tiers}

@router.post("/tiers")
async def create_feature_tier(
    tier: FeatureTier,
    current_user = Depends(get_current_admin_user)
):
    return {
        "message": "Feature tier created",
        "tier": tier.dict()
    }

@router.put("/tiers/{tier_name}")
async def update_feature_tier(
    tier_name: str,
    tier: FeatureTier,
    current_user = Depends(get_current_admin_user)
):
    return {
        "message": f"Feature tier {tier_name} updated",
        "tier": tier.dict()
    }

@router.delete("/tiers/{tier_name}")
async def delete_feature_tier(
    tier_name: str,
    current_user = Depends(get_current_admin_user)
):
    return {
        "message": f"Feature tier {tier_name} deleted"
    }
